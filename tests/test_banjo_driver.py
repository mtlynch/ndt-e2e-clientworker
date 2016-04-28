# Copyright 2016 Measurement Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import
import datetime
import unittest

import mock
import pytz
from selenium.common import exceptions
from client_wrapper import banjo_driver
from client_wrapper import browser_client_common
from client_wrapper import names
from tests import ndt_client_test


class BanjoDriverTest(ndt_client_test.NdtClientTest):

    def setUp(self):
        self.mock_driver = mock.Mock()
        self.mock_driver.capabilities = {'version': 'mock_version'}

        wait_until_visible_patcher = mock.patch.object(
            banjo_driver.browser_client_common, 'wait_until_element_is_visible')
        self.addCleanup(wait_until_visible_patcher.stop)
        wait_until_visible_patcher.start()
        banjo_driver.browser_client_common.wait_until_element_is_visible.return_value = (
            True)

        webdriver_wait_patcher = mock.patch.object(banjo_driver.ui,
                                                   'WebDriverWait')
        self.addCleanup(webdriver_wait_patcher.stop)
        webdriver_wait_patcher.start()

        text_to_be_present_patcher = mock.patch.object(
            banjo_driver.expected_conditions, 'text_to_be_present_in_element')
        self.addCleanup(text_to_be_present_patcher.stop)
        text_to_be_present_patcher.start()

        self.timeout_by_text = {
            'Testing download...': False,
            'Waiting for upload to start...': False,
            'Testing upload...': False,
        }

        def mock_text_to_be_present_in_element(_, text):
            if self.timeout_by_text[text]:
                raise exceptions.TimeoutException('mock timeout')

        banjo_driver.expected_conditions.text_to_be_present_in_element.side_effect = (
            mock_text_to_be_present_in_element)

        self.mock_latency = mock.Mock(text='1.23 ms')
        mock_latency_parent = mock.Mock()
        #TODO: Explain why lambda is necessary instead of return_value
        mock_latency_parent.find_elements_by_tag_name.side_effect = lambda _: [None, self.mock_latency]
        self.mock_download = mock.Mock(text='4.56')
        mock_download_parent = mock.Mock()
        mock_download_parent.find_elements_by_tag_name.side_effect = lambda _: [self.mock_download]
        self.mock_upload = mock.Mock(text='7.89')
        mock_upload_parent = mock.Mock()
        mock_upload_parent.find_elements_by_tag_name.side_effect = lambda _: [self.mock_upload]
        # Create mock DOM elements that are returned by calls to
        # find_element_by_id.
        self.mock_elements_by_id = {
            'lrfactory-internetspeed__test_button': mock.Mock(),
            'lrfactory-internetspeed__latency': mock_latency_parent,
            'lrfactory-internetspeed__download': mock_download_parent,
            'lrfactory-internetspeed__upload': mock_upload_parent,
        }
        self.mock_driver.find_element_by_id.side_effect = (
            lambda id: self.mock_elements_by_id[id])

        # Patch the call to create the browser driver to return our mock driver.
        create_browser_patcher = mock.patch.object(browser_client_common,
                                                   'create_browser')
        self.addCleanup(create_browser_patcher.stop)
        create_browser_patcher.start()
        browser_client_common.create_browser.return_value = self.mock_driver
        self.banjo = banjo_driver.BanjoDriver(names.FIREFOX,
                                              'http://fakelocalhost:1234/foo')

    def test_test_yields_valid_results_when_all_page_elements_are_expected_values(
            self):
        result = self.banjo.perform_test()

        self.assertEqual(1.23, result.latency)
        self.assertEqual(4.56, result.s2c_result.throughput)
        self.assertEqual(7.89, result.c2s_result.throughput)
        self.assertErrorMessagesEqual([], result.errors)

    def test_test_in_progress_timeout_yields_timeout_errors(self):
        """If each test times out, expect an error for each timeout."""
        self.timeout_by_text['Testing download...'] = True
        self.timeout_by_text['Waiting for upload to start...'] = True
        self.timeout_by_text['Testing upload...'] = True
        banjo_driver.browser_client_common.wait_until_element_is_visible.return_value = (
            False)

        result = self.banjo.perform_test()

        self.assertErrorMessagesEqual(
            [browser_client_common.ERROR_S2C_NEVER_STARTED,
             browser_client_common.ERROR_S2C_NEVER_ENDED,
             browser_client_common.ERROR_C2S_NEVER_STARTED,
             browser_client_common.ERROR_C2S_NEVER_ENDED], result.errors)

    def test_download_start_timeout_yields_errors(self):
        """If waiting for just download start times out, expect just one error."""
        self.timeout_by_text['Testing download...'] = True
        result = self.banjo.perform_test()

        self.assertErrorMessagesEqual(
            [browser_client_common.ERROR_S2C_NEVER_STARTED], result.errors)

    def test_results_page_displays_non_numeric_latency(self):
        self.mock_latency = mock.Mock(text='banana ms')
        result = self.banjo.perform_test()

        self.assertIsNone(result.latency)
        self.assertEqual(4.56, result.s2c_result.throughput)
        self.assertEqual(7.89, result.c2s_result.throughput)

        self.assertErrorMessagesEqual(
            ['Illegal value shown for latency: banana ms'], result.errors)

    def test_results_page_displays_non_numeric_download_throughput(self):
        self.mock_download.text = 'banana'

        result = self.banjo.perform_test()

        self.assertEqual(1.23, result.latency)
        self.assertIsNone(result.s2c_result.throughput)
        self.assertEqual(7.89, result.c2s_result.throughput)

        self.assertErrorMessagesEqual(
            ['Illegal value shown for s2c throughput: banana'], result.errors)

    def test_results_page_displays_non_numeric_upload_throughput(self):
        self.mock_upload = mock.Mock(text='banana')

        result = self.banjo.perform_test()

        self.assertEqual(1.23, result.latency)
        self.assertEqual(4.56, result.s2c_result.throughput)
        self.assertIsNone(result.c2s_result.throughput)

        self.assertErrorMessagesEqual(
            ['Illegal value shown for c2s throughput: banana'], result.errors)

    def test_results_page_displays_non_numeric_metrics(self):
        """A results page with non-numeric metrics results in error list errors.

        When latency, c2s_throughput, and s2c_throughput are all non-numeric values,
        corresponding error objects are added to the errors list that indicate
        that each of these values is invalid.
        """
        self.mock_latency = mock.Mock(text='apple')
        self.mock_download = mock.Mock(text='banana')
        self.mock_upload = mock.Mock(text='cherry')

        result = self.banjo.perform_test()

        self.assertIsNone(result.latency)
        self.assertIsNone(result.c2s_result.throughput)
        self.assertIsNone(result.s2c_result.throughput)
        self.assertErrorMessagesEqual(
            ['Illegal value shown for latency: apple',
             'Illegal value shown for s2c throughput: banana',
             'Illegal value shown for c2s throughput: cherry'], result.errors)

    def test_ndt_result_increments_time_correctly(self):
        # Create a list of mock times to be returned by datetime.now().
        times = []
        for i in range(15):
            times.append(datetime.datetime(2016, 1, 1, 0, 0, i))

        with mock.patch.object(banjo_driver.datetime,
                               'datetime',
                               autospec=True) as mocked_datetime:
            # Patch datetime.now to return the next mock time on every call to
            # now().
            mocked_datetime.now.side_effect = times

            # Modify the create_browser mock to increment the clock forward one
            # call.
            def mock_create_browser(unused_browser_name):
                datetime.datetime.now(pytz.utc)
                return self.mock_driver

            browser_client_common.create_browser.side_effect = (
                mock_create_browser)

            # Modify the wait_until_element_is_visible mock to increment the
            # clock forward one call.
            def mock_visibility_of(unused_driver, unused_element,
                                   unused_timeout):
                datetime.datetime.now(pytz.utc)
                return True

            banjo_driver.browser_client_common.wait_until_element_is_visible.side_effect = (
                mock_visibility_of)
            def mock_webdriver_wait(unused_driver, unused_timeout):
                datetime.datetime.now(pytz.utc)
                return mock.Mock()
            banjo_driver.ui.WebDriverWait.side_effect = mock_webdriver_wait
            result = self.banjo.perform_test()

        # Verify the recorded times matches the expected sequence.
        self.assertEqual(times[0], result.start_time)
        # times[1] is the call from mock_firefox
        self.assertEqual(times[3], result.s2c_result.start_time)
        self.assertEqual(times[5], result.s2c_result.end_time)
        # times[2] is the check for visibility of c2s test start
        self.assertEqual(times[7], result.c2s_result.start_time)
        # times[4] is the check for visibility of s2c test start (start of s2c
        #   marks the end of c2s)
        self.assertEqual(times[9], result.c2s_result.end_time)
        self.assertEqual(times[10], result.end_time)


if __name__ == '__main__':
    unittest.main()

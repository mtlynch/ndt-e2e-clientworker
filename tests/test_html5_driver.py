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
import re
import unittest

import mock
import pytz
import freezegun
import selenium.webdriver.support.expected_conditions as selenium_expected_conditions
from selenium.common import exceptions

from client_wrapper import html5_driver


class NdtHtml5SeleniumDriverTest(unittest.TestCase):

    def setUp(self):
        self.mock_visibility = mock.patch.object(selenium_expected_conditions,
                                                 'visibility_of',
                                                 autospec=True)
        self.addCleanup(self.mock_visibility.stop)
        self.mock_visibility.start()

        self.mock_driver = mock.Mock()
        self.mock_driver.capabilities = {'version': 'mock_version'}

        # Create mock DOM elements that are returned by calls to
        # find_element_by_id.
        self.mock_page_elements = {
            'websocketButton': mock.Mock(),
            'upload-speed': mock.Mock(text='1'),
            'upload-speed-units': mock.Mock(text='Mb/s'),
            'download-speed': mock.Mock(text='2'),
            'download-speed-units': mock.Mock(text='Mb/s'),
            'latency': mock.Mock(text='3'),
            'results': mock.Mock(),
        }
        self.mock_driver.find_element_by_id.side_effect = (
            lambda id: self.mock_page_elements[id])

        # Create mock DOM elements that are returned by calls to
        # find_elements_by_xpath.
        self.mock_elements_by_text = {
            'Start Test': mock.Mock(),
            'your upload speed': mock.Mock(),
            'your download speed': mock.Mock(),
        }

        def mock_find_elements_by_xpath(xpath):
            """Mock implementation that only supports searching by text."""
            matching_text = re.match('^//\*\[contains\(text\(\), \'(.+)\'\)\]$',
                                     xpath).group(1)
            return [self.mock_elements_by_text[matching_text]]

        self.mock_driver.find_elements_by_xpath = mock_find_elements_by_xpath

        firefox_patcher = mock.patch.object(html5_driver.webdriver, 'Firefox')
        self.addCleanup(firefox_patcher.stop)
        firefox_patcher.start()

        html5_driver.webdriver.Firefox.return_value = self.mock_driver

    def assertErrorMessagesEqual(self, expected_messages, actual_errors):
        """Verifies that a list of TestErrors have the expected error messages.

        Note that this compares just by message text and ignores timestamp.
        """
        actual_messages = [e.message for e in actual_errors]
        self.assertListEqual(expected_messages, actual_messages)

    def test_test_yields_valid_results_when_all_page_elements_are_expected_values(
            self):
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertEqual(1.0, result.c2s_result.throughput)
        self.assertEqual(2.0, result.s2c_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual([], result.errors)

    def test_invalid_URL_throws_error(self):
        self.mock_driver.get.side_effect = (
            exceptions.WebDriverException('Failed to load test UI.'))
        result = html5_driver.NdtHtml5SeleniumDriver(browser='firefox',
                                                     url='invalid_url',
                                                     timeout=1).perform_test()

        self.assertErrorMessagesEqual(
            ['Failed to load test UI.'], result.errors)

    def test_test_in_progress_timeout_throws_error(self):
        # Call to webdriverwait throws timeout exception
        with mock.patch.object(html5_driver.ui,
                               'WebDriverWait',
                               side_effect=exceptions.TimeoutException,
                               autospec=True):
            result = html5_driver.NdtHtml5SeleniumDriver(
                browser='firefox',
                url='http://ndt.mock-server.com:7123/',
                timeout=1).perform_test()

        self.assertErrorMessagesEqual(
            ['Test did not complete within timeout period.'], result.errors)

    def test_unrecognized_browser_raises_error(self):
        selenium_driver = html5_driver.NdtHtml5SeleniumDriver(
            browser='not_a_browser',
            url='http://ndt.mock-server.com:7123',
            timeout=1)
        with self.assertRaises(ValueError):
            selenium_driver.perform_test()

    def test_results_page_displays_non_numeric_latency(self):
        self.mock_page_elements['latency'] = mock.Mock(text='Non-numeric value')
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertEqual(1.0, result.c2s_result.throughput)
        self.assertEqual(2.0, result.s2c_result.throughput)
        self.assertIsNone(result.latency)
        self.assertErrorMessagesEqual(
            ['illegal value shown for latency: Non-numeric value'],
            result.errors)

    def test_results_page_displays_non_numeric_c2s_throughput(self):
        self.mock_page_elements['upload-speed'] = mock.Mock(
            text='Non-numeric value')
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertIsNone(result.c2s_result.throughput)
        self.assertEqual(2.0, result.s2c_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual(
            ['illegal value shown for c2s throughput: Non-numeric value'],
            result.errors)

    def test_results_page_displays_non_numeric_s2c_throughput(self):
        self.mock_page_elements['download-speed'] = mock.Mock(
            text='Non-numeric value')
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertEqual(1.0, result.c2s_result.throughput)
        self.assertIsNone(result.s2c_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual(
            ['illegal value shown for s2c throughput: Non-numeric value'],
            result.errors)

    def test_results_page_displays_non_numeric_metrics(self):
        """A results page with non-numeric metrics results in error list errors.

        When latency, c2s_throughput, and s2c_throughput are all non-numeric values,
        corresponding error objects are added to the errors list that indicate
        that each of these values is invalid.
        """
        self.mock_page_elements['upload-speed'] = mock.Mock(
            text='Non-numeric value')
        self.mock_page_elements['download-speed'] = mock.Mock(
            text='Non-numeric value')
        self.mock_page_elements['latency'] = mock.Mock(text='Non-numeric value')

        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertIsNone(result.c2s_result.throughput)
        self.assertIsNone(result.s2c_result.throughput)
        self.assertIsNone(result.latency)
        self.assertErrorMessagesEqual(
            ['illegal value shown for c2s throughput: Non-numeric value',
             'illegal value shown for s2c throughput: Non-numeric value',
             'illegal value shown for latency: Non-numeric value'],
            result.errors)

    def test_s2c_gbps_speed_conversion(self):
        """Test s2c speed converts from Gb/s to Mb/s correctly."""
        # If s2c speed is 72 Gb/s and c2s is speed is 34 in the browser
        self.mock_page_elements['upload-speed'] = mock.Mock(text='34')
        self.mock_page_elements['upload-speed-units'] = mock.Mock(text='Mb/s')
        self.mock_page_elements['download-speed'] = mock.Mock(text='72')
        self.mock_page_elements['download-speed-units'] = mock.Mock(text='Gb/s')

        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        # Then s2c is converted from Gb/s to Mb/s
        self.assertEqual(72000.0, result.s2c_result.throughput)
        # And c2s is not
        self.assertEqual(34.0, result.c2s_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual([], result.errors)

    def test_invalid_throughput_unit_yields_error(self):
        self.mock_page_elements['upload-speed-units'] = mock.Mock(text='banana')

        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertIsNone(result.c2s_result.throughput)
        self.assertEqual(2.0, result.s2c_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual(
            ['Invalid throughput unit specified: banana'], result.errors)

    def test_reading_in_result_page_timeout_throws_error(self):
        # Simulate a timeout exception when the driver attempts to read the
        # metric page.
        def mock_find_element_by_id(id):
            if id == 'upload-speed':
                raise exceptions.TimeoutException
            return self.mock_page_elements[id]

        self.mock_driver.find_element_by_id.side_effect = (
            mock_find_element_by_id)
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertIsNone(result.c2s_result.throughput)
        self.assertIsNone(result.s2c_result.throughput)
        self.assertIsNone(result.latency)
        self.assertErrorMessagesEqual(
            ['Test did not complete within timeout period.'], result.errors)

    @mock.patch.object(html5_driver.webdriver, 'Chrome')
    def test_chrome_driver_can_be_used_for_test(self, mock_chrome):
        mock_chrome.return_value = self.mock_driver
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='chrome',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertEqual(1.0, result.c2s_result.throughput)
        self.assertEqual(2.0, result.s2c_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual([], result.errors)

    @mock.patch.object(html5_driver.webdriver, 'Edge')
    def test_edge_driver_can_be_used_for_test(self, mock_edge):
        mock_edge.return_value = self.mock_driver
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='edge',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertEqual(1.0, result.c2s_result.throughput)
        self.assertEqual(2.0, result.s2c_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual([], result.errors)

    @mock.patch.object(html5_driver.webdriver, 'Safari')
    def test_safari_driver_can_be_used_for_test(self, mock_safari):
        mock_safari.return_value = self.mock_driver
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='safari',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        self.assertEqual(1.0, result.c2s_result.throughput)
        self.assertEqual(2.0, result.s2c_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual([], result.errors)

    def test_c2s_kbps_speed_conversion(self):
        """Test c2s speed converts from kb/s to Mb/s correctly."""
        # If c2s speed is 72 kb/s and s2c speed is 34 in the browser
        self.mock_page_elements['upload-speed'] = mock.Mock(text='72')
        self.mock_page_elements['upload-speed-units'] = mock.Mock(text='kb/s')
        self.mock_page_elements['download-speed'] = mock.Mock(text='34')
        self.mock_page_elements['download-speed-units'] = mock.Mock(text='Mb/s')
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        # Then c2s is converted from kb/s to Mb/s
        self.assertEqual(0.072, result.c2s_result.throughput)
        # And s2c is not
        self.assertEqual(34.0, result.s2c_result.throughput)
        self.assertEqual(3.0, result.latency)
        self.assertErrorMessagesEqual([], result.errors)

    @freezegun.freeze_time('2016-01-01', tz_offset=0)
    def test_ndt_result_records_todays_times(self):
        # When we patch datetime so it shows our current date as 2016-01-01
        self.assertEqual(datetime.datetime.now(), datetime.datetime(2016, 1, 1))
        result = html5_driver.NdtHtml5SeleniumDriver(
            browser='firefox',
            url='http://ndt.mock-server.com:7123/',
            timeout=1000).perform_test()

        # Then the readings for our test start and end times occur within
        # today's date
        self.assertEqual(result.start_time,
                         datetime.datetime(2016,
                                           1,
                                           1,
                                           tzinfo=pytz.utc))
        self.assertEqual(result.end_time,
                         datetime.datetime(2016,
                                           1,
                                           1,
                                           tzinfo=pytz.utc))

    def test_ndt_result_increments_time_correctly(self):
        # Create a list of times every minute starting at 2016-1-1 8:00:00 and
        # ending at 2016-1-1 8:04:00. These will be the values that our mock
        # datetime.now() function returns.
        base_date = datetime.datetime(2016, 1, 1, 8, 0, 0, tzinfo=pytz.utc)
        dates = [base_date + datetime.timedelta(0, 60) * x for x in range(6)]

        with mock.patch.object(html5_driver.datetime,
                               'datetime',
                               autospec=True) as mocked_datetime:
            mocked_datetime.now.side_effect = dates

            result = html5_driver.NdtHtml5SeleniumDriver(
                browser='firefox',
                url='http://ndt.mock-server.com:7123/',
                timeout=1).perform_test()

        # And the sequence of returned values follows the expected timeline
        # that the readings are taken in.

        # yapf: disable
        self.assertEqual(
            result.start_time,
            datetime.datetime(2016, 1, 1, 8, 0, 0, tzinfo=pytz.utc))
        self.assertEqual(
            result.c2s_result.start_time,
            datetime.datetime(2016, 1, 1, 8, 1, 0, tzinfo=pytz.utc))
        self.assertEqual(
            result.s2c_result.start_time,
            datetime.datetime(2016, 1, 1, 8, 3, 0, tzinfo=pytz.utc))
        self.assertEqual(
            result.end_time,
            datetime.datetime(2016, 1, 1, 8, 5, 0, tzinfo=pytz.utc))
        # yapf: enable


if __name__ == '__main__':
    unittest.main()

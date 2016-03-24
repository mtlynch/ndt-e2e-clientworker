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
import unittest
import datetime
import mock
import pytz
import freezegun
import selenium.webdriver.support.expected_conditions as selenium_expected_conditions
from selenium.common import exceptions
from client_wrapper import client_wrapper


class NdtHtml5SeleniumDriverGeneralTest(unittest.TestCase):

    def setUp(self):
        self.mock_browser = mock.MagicMock()

        self.mock_driver = mock.patch.object(client_wrapper.webdriver,
                                             'Firefox',
                                             autospec=True,
                                             return_value=self.mock_browser)
        self.addCleanup(self.mock_driver.stop)
        self.mock_driver.start()

        self.mock_visibility = mock.patch.object(selenium_expected_conditions,
                                                 'visibility_of',
                                                 autospec=True)
        self.addCleanup(self.mock_visibility.stop)
        self.mock_visibility.start()
        self.mock_visibility.return_value = True

    def test_invalid_URL_throws_error(self):
        self.mock_browser.get.side_effect = exceptions.WebDriverException(
            u'Failed to load test UI.')

        selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
        test_results = selenium_driver.perform_test(url='invalid_url',
                                                    browser='firefox',
                                                    timeout=1)

        # We have one error
        self.assertEqual(len(test_results.errors), 1)

        # And that error is about test UI loading failure
        self.assertEqual(test_results.errors[0].message,
                         'Failed to load test UI.')

    def test_timeout_throws_error(self):

        # Call to webdriverwait throws timeout exception
        with mock.patch.object(client_wrapper.ui,
                               'WebDriverWait',
                               side_effect=exceptions.TimeoutException,
                               autospec=True):
            selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
            test_results = selenium_driver.perform_test(
                url='http://ndt.mock-server.com:7123/',
                browser='firefox',
                timeout=1)

        # We have one error
        self.assertEqual(len(test_results.errors), 1)

        # And that is a timout error
        self.assertEqual(test_results.errors[0].message,
                         'Test did not complete within timeout period.')

    def test_unimplemented_browsers_raise_error(self):
        selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
        with self.assertRaises(NotImplementedError):
            selenium_driver.perform_test(url='http://ndt.mock-server.com:7123',
                                         browser='chrome',
                                         timeout=1)
        with self.assertRaises(NotImplementedError):
            selenium_driver.perform_test(url='http://ndt.mock-server.com:7123',
                                         browser='edge',
                                         timeout=1)
        with self.assertRaises(NotImplementedError):
            selenium_driver.perform_test(url='http://ndt.mock-server.com:7123',
                                         browser='safari',
                                         timeout=1)

    def test_unrecognized_browser_raises_error(self):
        selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
        with self.assertRaises(ValueError):
            selenium_driver.perform_test(url='http://ndt.mock-server.com:7123',
                                         browser='not_a_browser',
                                         timeout=1)

    @freezegun.freeze_time('2016-01-01', tz_offset=0)
    def test_ndt_test_results_records_todays_times(self):
        # When we patch datetime so it shows our current date as 2016-01-01
        self.assertEqual(datetime.datetime.now(), datetime.datetime(2016, 1, 1))

        with mock.patch.object(client_wrapper.ui,
                               'WebDriverWait',
                               autospec=True):
            selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
            test_results = selenium_driver.perform_test(
                url='http://ndt.mock-server.com:7123/',
                browser='firefox',
                timeout=1)

        # Then the readings for our test start and end times occur within
        # today's date
        self.assertEqual(test_results.start_time,
                         datetime.datetime(2016,
                                           1,
                                           1,
                                           tzinfo=pytz.utc))
        self.assertEqual(test_results.end_time,
                         datetime.datetime(2016,
                                           1,
                                           1,
                                           tzinfo=pytz.utc))

    def test_ndt_test_results_increments_time_correctly(self):
        # Create a list of times every minute starting at 2016-1-1 8:00:00
        # and ending at 2016-1-1 8:04:00. These will be the values that our
        # mock datetime.now() function returns.
        base_date = datetime.datetime(2016, 1, 1, 8, 0, 0, tzinfo=pytz.utc)
        dates = [base_date + datetime.timedelta(0, 60) * x for x in range(5)]

        def mock_dates(_):
            return dates.pop(0)

        with mock.patch.object(client_wrapper.datetime,
                               'datetime',
                               autospec=True,) as mocked_datetime:

            mocked_datetime.now.side_effect = mock_dates
            selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()

            test_results = selenium_driver.perform_test(
                url='http://ndt.mock-server.com:7123/',
                browser='firefox',
                timeout=1)

        # And the sequence of returned values follows the expected timeline
        # that the readings are taken in.
        self.assertEqual(test_results.start_time,
                         datetime.datetime(2016,
                                           1,
                                           1,
                                           8,
                                           0,
                                           0,
                                           tzinfo=pytz.utc))
        self.assertEqual(test_results.c2s_start_time,
                         datetime.datetime(2016,
                                           1,
                                           1,
                                           8,
                                           1,
                                           0,
                                           tzinfo=pytz.utc))
        self.assertEqual(test_results.s2c_start_time,
                         datetime.datetime(2016,
                                           1,
                                           1,
                                           8,
                                           2,
                                           0,
                                           tzinfo=pytz.utc))
        self.assertEqual(test_results.end_time,
                         datetime.datetime(2016,
                                           1,
                                           1,
                                           8,
                                           3,
                                           0,
                                           tzinfo=pytz.utc))


class NdtHtml5SeleniumDriverCustomClassTest(unittest.TestCase):

    def setUp(self):
        self.mock_visibility = mock.patch.object(selenium_expected_conditions,
                                                 'visibility_of',
                                                 autospec=True)
        self.addCleanup(self.mock_visibility.stop)
        self.mock_visibility.return_value = True
        self.mock_visibility.start()

    def test_results_page_displays_non_numeric_metrics(self):
        """A results page with non-numeric metrics results in error list errors.

        When latency, c2s_throughput, and s2c_throughput are non-numeric values,
        corresponding error objects are added to the errors list that indicate
        that each of these values is invalid.
        """

        # We patch selenium's web driver so it always has a non numeric
        # value as a WebElement.text attribute
        class NewWebElement(object):

            def __init__(self):
                self.text = 'Non numeric value'

            def click(self):
                pass

        class NewDriver(object):

            def get(self, url):
                pass

            def close(self):
                pass

            def find_element_by_id(self, id):
                return NewWebElement()

            def find_elements_by_xpath(self, xpath):
                return [NewWebElement()]

        with mock.patch.object(client_wrapper.webdriver,
                               'Firefox',
                               autospec=True,
                               return_value=NewDriver()):

            selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
            test_results = selenium_driver.perform_test(
                url='http://ndt.mock-server.com:7123/',
                browser='firefox',
                timeout=1000)

        # And the appropriate error objects are contained in
        # the list
        self.assertEqual(
            test_results.errors[0].message,
            'illegal value shown for c2s_throughput: Non numeric value')
        self.assertEqual(
            test_results.errors[1].message,
            'illegal value shown for s2c_throughput: Non numeric value')
        self.assertEqual(test_results.errors[2].message,
                         'illegal value shown for latency: Non numeric value')

    def test_results_page_displays_numeric_latency(self):
        """A valid (numeric) latency results in an empty errors list."""

        # Mock so always returns a numeric value for a WebElement.text attribute
        class NewWebElement(object):

            def __init__(self):
                self.text = '72'

            def click(self):
                pass

        class NewDriver(object):

            def get(self, url):
                pass

            def close(self):
                pass

            def find_element_by_id(self, id):
                return NewWebElement()

            def find_elements_by_xpath(self, xpath):
                return [NewWebElement()]

        with mock.patch.object(client_wrapper.webdriver,
                               'Firefox',
                               autospec=True,
                               return_value=NewDriver()):

            selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
            test_results = selenium_driver.perform_test(
                url='http://ndt.mock-server.com:7123/',
                browser='firefox',
                timeout=1000)

        self.assertEqual(test_results.latency, '72')
        # And an error object is not contained in the list
        self.assertEqual(len(test_results.errors), 0)


if __name__ == '__main__':
    unittest.main()

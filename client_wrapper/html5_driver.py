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

import contextlib
import datetime

import pytz
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions

import names
import results


class NdtHtml5SeleniumDriver(object):

    def __init__(self, browser, url, timeout):
        """Creates a NDT HTML5 client driver for the given URL and browser.

        Args:
            url: The URL of an NDT server to test against.
            browser: Can be one of 'firefox', 'chrome', 'edge', or 'safari'.
            timeout: The number of seconds that the driver will wait for each
                element to become visible before timing out.
        """
        self._browser = browser
        self._url = url
        self._timeout = timeout

    def perform_test(self):
        """Performs a full NDT test (both s2c and c2s) with the HTML5 client.

        Returns:
            A populated NdtResult object.
        """
        result = results.NdtResult(start_time=None,
                                   end_time=None,
                                   c2s_start_time=None,
                                   s2c_start_time=None,
                                   errors=[])

        with contextlib.closing(_create_browser(self._browser)) as driver:

            if not _load_url(driver, self._url, result):
                return result

            _click_start_button(driver, result)

            if not _record_test_in_progress_values(result, driver,
                                                   self._timeout):
                return result

            if not _populate_metric_values(result, driver):
                return result

            return result


def _create_browser(browser):
    """Creates browser for an NDT test.

    Args:
        browser: Can be one of 'firefox', 'chrome', 'edge', or 'safari'

    Returns:
        An instance of a Selenium webdriver browser class corresponding to
        the specified browser.
    """
    if browser == names.FIREFOX:
        return webdriver.Firefox()
    if browser in [names.CHROME, names.EDGE, names.SAFARI]:
        raise NotImplementedError
    raise ValueError('Invalid browser specified: %s' % browser)


def _load_url(driver, url, result):
    """Loads the URL in a Selenium driver for an NDT test.

    Args:
        driver: An instance of a Selenium webdriver.
        url: The The URL of an NDT server to test against.
        result: An instance of NdtResult.

    Returns:
        True if loading the URL was successful, False if otherwise.
    """
    try:
        driver.get(url)
    except exceptions.WebDriverException:
        message = 'Failed to load test UI.'
        result.errors.append(results.TestError(
            datetime.datetime.now(pytz.utc), message))
        return False
    return True


def _click_start_button(driver, result):
    """Clicks start test button and records start time.

    Clicks the start test button for an NDT test and records the start time in
    an NdtResult instance.

    Args:
        driver: An instance of a Selenium webdriver browser class.
        result: An instance of an NdtResult class.
    """
    driver.find_element_by_id('websocketButton').click()

    start_button = driver.find_elements_by_xpath(
        "//*[contains(text(), 'Start Test')]")[0]
    start_button.click()
    result.start_time = datetime.datetime.now(pytz.utc)


def _record_test_in_progress_values(result, driver, timeout):
    """Records values that are measured while the NDT test is in progress.

    Measures s2c_start_time, c2s_end_time, and end_time, which are stored in
    an instance of NdtResult. These times are measured while the NDT test is
    in progress.

    Args:
        result: An instance of NdtResult.
        driver: An instance of a Selenium webdriver browser class.
        timeout: The number of seconds that the driver will wait for
            each element to become visible before timing out.

    Returns:
        True if recording the measured values was successful, False if otherwise.
    """
    try:
        # wait until 'Now Testing your upload speed' is displayed
        upload_speed_text = driver.find_elements_by_xpath(
            "//*[contains(text(), 'your upload speed')]")[0]
        result.c2s_start_time = _record_time_when_element_displayed(
            upload_speed_text,
            driver,
            timeout=timeout)

        # wait until 'Now Testing your download speed' is displayed
        download_speed_text = driver.find_elements_by_xpath(
            "//*[contains(text(), 'your download speed')]")[0]
        result.s2c_start_time = _record_time_when_element_displayed(
            download_speed_text,
            driver,
            timeout=timeout)

        # wait until the results page appears
        results_text = driver.find_element_by_id('results')
        result.end_time = _record_time_when_element_displayed(results_text,
                                                              driver,
                                                              timeout=timeout)
    except exceptions.TimeoutException:
        message = 'Test did not complete within timeout period.'
        result.errors.append(results.TestError(
            datetime.datetime.now(pytz.utc), message))
        return False
    return True


def _record_time_when_element_displayed(element, driver, timeout):
    """Return the time when the specified element is displayed.

    The Selenium WebDriver checks whether the specified element is visible. If
    it becomes visible before the request has timed out, the timestamp of the
    time when the element becomes visible is returned.

    Args:
        element: A selenium webdriver element.
        driver: An instance of a Selenium webdriver browser class.
        timeout: The number of seconds that the driver will wait for
            each element to become visible before timing out.

    Returns: A datetime object with a timezone information attribute.

    Raises:
        TimeoutException: If the element does not become visible before the
            timeout time passes.
    """
    ui.WebDriverWait(driver, timeout=timeout).until(EC.visibility_of(element))
    return datetime.datetime.now(pytz.utc)


def _populate_metric_values(result, driver):
    """Populates NdtResult with metrics from page, checks values are valid.

    Populates the NdtResult instance with metrics from the NDT test page. Checks
    thatthe values for upload (c2s) throughput, download (s2c) throughput, and
    latency within the NdtResult instance dict are valid.

    Args:
        result: An instance of NdtResult.
        driver: An instance of a Selenium webdriver browser class.

    Returns:
        True if populating metrics and checking their values was successful.
            False if otherwise.
    """
    try:
        result.c2s_throughput = driver.find_element_by_id('upload-speed').text
        result = _validate_metric(result, result.c2s_throughput,
                                  'c2s_throughput')
        result.s2c_throughput = driver.find_element_by_id('download-speed').text
        result = _validate_metric(result, result.s2c_throughput,
                                  's2c_throughput')
        result.latency = driver.find_element_by_id('latency').text
        result = _validate_metric(result, result.latency, 'latency')
    except exceptions.TimeoutException:
        message = 'Test did not complete within timeout period.'
        result.errors.append(results.TestError(
            datetime.datetime.now(pytz.utc), message))
        return False
    return True


def _validate_metric(result, metric, metric_name):
    """Checks whether a given metric is a valid numeric value.

    For a given metric, checks that it is a valid numeric value. If not, an
    error is added to the list contained in the NdtResult instance attribute.

    Args:
        result: An instance of NdtResult.
        metric: The value of the metric that is to be evaluated.
        metric_name: A string representing the name of the metric to validate.

    Returns:
        An instance of NdtResult.
    """
    try:
        float(metric)
    except ValueError:
        message = 'illegal value shown for ' + metric_name + ': ' + str(metric)
        result.errors.append(results.TestError(
            datetime.datetime.now(pytz.utc), message))
    return result

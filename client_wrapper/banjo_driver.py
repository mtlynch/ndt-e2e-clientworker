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

from __future__ import division
import contextlib
import datetime

import pytz
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions
from selenium.common import exceptions
from selenium.webdriver.common import by

import browser_client_common
import names
import results

ERROR_FAILED_TO_LOCATE_RUN_TEST_BUTTON = 'Failed to locate "Run Speed Test" button.'
ERROR_NO_LATENCY_FIELD = 'Could not find latency field.'
ERROR_NO_S2C_FIELD = 'Could not find s2c throughput field.'
ERROR_NO_C2S_FIELD = 'Could not find c2s throughput field.'
ERROR_FORMAT_ILLEGAL_LATENCY = 'Illegal value shown for latency: %s'
ERROR_FORMAT_ILLEGAL_S2C_THROUGHPUT = 'Illegal value shown for s2c throughput: %s'
ERROR_FORMAT_ILLEGAL_C2S_THROUGHPUT = 'Illegal value shown for c2s throughput: %s'

# Default number of seconds to wait for any particular stage of the UI flow to
# complete.
_DEFAULT_TIMEOUT = 20


class BanjoDriver(object):

    def __init__(self, browser, url):
        """Creates a Banjo client driver for the given URL and browser.

        Args:
            url: The URL of an NDT server to test against.
            browser: Can be one of 'firefox', 'chrome', 'edge', or 'safari'.
        """
        self._browser = browser
        self._url = url

    def perform_test(self):
        """Performs a full NDT test (both s2c and c2s) with the HTML5 client.

        Returns:
            A populated NdtResult object.
        """
        result = results.NdtResult(client=names.BANJO,
                                   start_time=datetime.datetime.now(pytz.utc))
        # TODO: Remove, this shouldn't be necessary.
        result.c2s_result = results.NdtSingleTestResult()
        result.s2c_result = results.NdtSingleTestResult()
        result.errors = []

        with contextlib.closing(browser_client_common.create_browser(
                self._browser)) as driver:
            result.browser = self._browser
            result.browser_version = driver.capabilities['version']

            if not browser_client_common.load_url(driver, self._url,
                                                  result.errors):
                return

            _BanjoUiFlowWrapper(driver, self._url, result).complete_ui_flow()

        result.end_time = datetime.datetime.now(pytz.utc)
        return result


class _BanjoUiFlowWrapper(object):

    def __init__(self, driver, url, result):
        """Performs the UI flow for the Banjo client test and records results.

        Args:
            driver: An instance of a Selenium webdriver browser class.
            url: URL to load to start the UI flow.
            result: NdtResult instance to populate with results from proceeding
                through the UI flow.
        """
        self._driver = driver
        self._url = url
        self._result = result

    def complete_ui_flow(self):
        if not self._click_run_test_button():
            return

        if self._wait_for_download_test_to_start():
            self._result.s2c_result.start_time = datetime.datetime.now(pytz.utc)
        else:
            self._add_test_error(browser_client_common.ERROR_S2C_NEVER_STARTED)

        if self._wait_for_download_test_to_end():
            self._result.s2c_result.end_time = datetime.datetime.now(pytz.utc)
        else:
            self._add_test_error(browser_client_common.ERROR_S2C_NEVER_ENDED)

        if self._wait_for_upload_test_to_start():
            self._result.c2s_result.start_time = datetime.datetime.now(pytz.utc)
        else:
            self._add_test_error(browser_client_common.ERROR_C2S_NEVER_STARTED)

        # When the latency field becomes visible in the web UI, the NDT test is
        # complete.
        if self._wait_for_latency_field():
            self._result.c2s_result.end_time = datetime.datetime.now(pytz.utc)
        else:
            self._add_test_error(browser_client_common.ERROR_C2S_NEVER_ENDED)

        latency = self._parse_latency()
        if latency is not None:
            self._result.latency = latency

        download_throughput = self._parse_download_throughput()
        if download_throughput is not None:
            self._result.s2c_result.throughput = download_throughput

        upload_throughput = self._parse_upload_throughput()
        if upload_throughput is not None:
            self._result.c2s_result.throughput = upload_throughput

    def _click_run_test_button(self):
        start_button = self._driver.find_element_by_id(
            'lrfactory-internetspeed__test_button')
        if not start_button:
            self._add_test_error(ERROR_FAILED_TO_LOCATE_RUN_TEST_BUTTON)
            return False
        start_button.click()
        return True

    def _wait_for_download_test_to_start(self):
        return self._wait_for_status_banner_text('Testing download...')

    def _wait_for_download_test_to_end(self):
        return self._wait_for_status_banner_text(
            'Waiting for upload to start...')

    def _wait_for_upload_test_to_start(self):
        return self._wait_for_status_banner_text('Testing upload...')

    def _wait_for_status_banner_text(self, status_text):
        try:
            ui.WebDriverWait(self._driver, _DEFAULT_TIMEOUT).until(
                expected_conditions.text_to_be_present_in_element(
                    (by.By.CLASS_NAME,
                     'lrfactory-internetspeed__status-indicator'), status_text))
        except exceptions.TimeoutException:
            return False
        return True

    def _wait_for_latency_field(self):
        return browser_client_common.wait_until_element_is_visible(
            self._driver,
            self._driver.find_element_by_id('lrfactory-internetspeed__latency'),
            _DEFAULT_TIMEOUT)

    def _parse_latency(self):
        latency_parent = self._driver.find_element_by_id(
            'lrfactory-internetspeed__latency')
        if not latency_parent:
            self._add_test_error(ERROR_NO_LATENCY_FIELD)
            return None
        children = latency_parent.find_elements_by_tag_name('span')
        if not children or len(children) < 2:
            self._add_test_error(ERROR_NO_LATENCY_FIELD)
            return None
        latency_text = children[1].text
        latency_value_parts = latency_text.split()
        latency_value = latency_value_parts[0]
        try:
            return float(latency_value)
        except ValueError:
            self._add_test_error(ERROR_FORMAT_ILLEGAL_LATENCY % latency_text)
            return None

    def _parse_download_throughput(self):
        download_parent = self._driver.find_element_by_id(
            'lrfactory-internetspeed__download')
        if not download_parent:
            self._add_test_error(ERROR_NO_S2C_FIELD)
            return None
        children = download_parent.find_elements_by_tag_name('p')
        if not children:
            self._add_test_error(ERROR_NO_S2C_FIELD)
            return None
        throughput_text = children[0].text
        try:
            return float(throughput_text)
        except ValueError:
            self._add_test_error(ERROR_FORMAT_ILLEGAL_S2C_THROUGHPUT %
                                 throughput_text)
            return None

    def _parse_upload_throughput(self):
        upload_parent = self._driver.find_element_by_id(
            'lrfactory-internetspeed__upload')
        if not upload_parent:
            self._add_test_error(ERROR_NO_C2S_FIELD)
            return None
        children = upload_parent.find_elements_by_tag_name('p')
        if not children:
            self._add_test_error(ERROR_NO_C2S_FIELD)
            return None
        throughput_text = children[0].text
        try:
            return float(throughput_text)
        except ValueError:
            self._add_test_error(ERROR_FORMAT_ILLEGAL_C2S_THROUGHPUT %
                                 throughput_text)
            return None

    def _add_test_error(self, error_message):
        self._result.errors.append(results.TestError(error_message))

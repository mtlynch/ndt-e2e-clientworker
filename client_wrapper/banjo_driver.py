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
        """Performs a full NDT test (both s2c and c2s) with the Banjo client.

        Returns:
            A populated NdtResult object.
        """
        result = results.NdtResult(client=names.BANJO,
                                   start_time=datetime.datetime.now(pytz.utc))

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

        # When the latency field becomes visible in the web UI, the C2S test is
        # complete.
        if self._wait_for_latency_field():
            self._result.c2s_result.end_time = datetime.datetime.now(pytz.utc)
        else:
            self._add_test_error(browser_client_common.ERROR_C2S_NEVER_ENDED)

        # TODO(mtlynch): Implement the rest of the UI flow.

    def _click_run_test_button(self):
        start_button = self._driver.find_element_by_id(
            'lrfactory-internetspeed__test_button')
        if not start_button:
            self._add_test_error(ERROR_FAILED_TO_LOCATE_RUN_TEST_BUTTON)
            return False
        # We skip waiting for the element to become visible because it should
        # be visible as soon as the page loads.
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
        """Wait until specified text appears in the status banner of the web UI.

        Args:
            status_text: The text in the web UI banner for which to wait.

        Returns:
            True if the status banner displayed the specified within the
            timeout period.
        """
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

    def _add_test_error(self, error_message):
        self._result.errors.append(results.TestError(error_message))

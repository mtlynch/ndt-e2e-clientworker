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

import browser_client_common
import names
import results

ERROR_FAILED_TO_LOCATE_RUN_TEST_BUTTON = 'Failed to locate "Run Speed Test" button.'


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
        # TODO(mtlynch): Implement the rest of the UI flow.
        raise NotImplementedError('Remainder of UI flow not yet implemented.')

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

    def _add_test_error(self, error_message):
        self._result.errors.append(results.TestError(error_message))

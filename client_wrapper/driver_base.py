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
import datetime

import pytz
from selenium import webdriver
from selenium.common import exceptions

import names


class BrowserDriverBase(object):

    def __init__(self, browser, url, timeout):
        """Creates a client NDT driver for the given URL and browser.

        Args:
            url: The URL of an NDT server to test against.
            browser: Can be one of 'firefox', 'chrome', 'edge', or 'safari'.
            timeout: The number of seconds that the driver will wait for each
                element to become visible before timing out.
        """
        self._browser = browser
        self._url = url
        self._timeout = timeout

    def _create_browser(self):
        if self._browser == names.FIREFOX:
            return webdriver.Firefox()
        elif self._browser == names.CHROME:
            return webdriver.Chrome()
        elif self._browser == names.EDGE:
            return webdriver.Edge()
        elif self._browser == names.SAFARI:
            return webdriver.Safari()
        raise ValueError('Invalid browser specified: %s' % self._browser)

    def _load_test_page(self, driver, errors):
        """Loads the NDT test page URL in the given Selenium driver.

        Args:
            driver: An instance of a Selenium webdriver.
            url: The The URL of an NDT server to test against.
            result: An instance of NdtResult.

        Returns:
            True if loading the URL was successful.
        """
        try:
            driver.get(url)
        except exceptions.WebDriverException:
            errors.append(results.TestError(
                datetime.datetime.now(pytz.utc), 'Failed to load test UI.'))
            return False
        return True

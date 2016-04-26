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

import mock
from selenium.common import exceptions

from client_wrapper import browser_client_common
from client_wrapper import names
from tests import ndt_client_test


class CreateBrowserTest(unittest.TestCase):
    """Tests for create_browser function."""

    @mock.patch.object(browser_client_common.webdriver, 'Firefox')
    def test_create_firefox_browser_succeeds(self, mock_firefox):
        mock_firefox.return_value = 'mock firefox driver'

        self.assertEqual('mock firefox driver',
                         browser_client_common.create_browser(names.FIREFOX))
        self.assertTrue(mock_firefox.called)

    @mock.patch.object(browser_client_common.webdriver, 'Chrome')
    def test_create_chrome_browser_succeeds(self, mock_chrome):
        mock_chrome.return_value = 'mock chrome driver'

        self.assertEqual('mock chrome driver',
                         browser_client_common.create_browser(names.CHROME))
        self.assertTrue(mock_chrome.called)

    @mock.patch.object(browser_client_common.webdriver, 'Edge')
    def test_create_edge_driver_succeeds(self, mock_edge):
        mock_edge.return_value = 'mock edge driver'

        self.assertEqual('mock edge driver',
                         browser_client_common.create_browser(names.EDGE))
        self.assertTrue(mock_edge.called)

    @mock.patch.object(browser_client_common.webdriver, 'Safari')
    def test_create_safari_browser_succeeds(self, mock_safari):
        mock_safari.return_value = 'mock safari driver'

        self.assertEqual('mock safari driver',
                         browser_client_common.create_browser(names.SAFARI))
        self.assertTrue(mock_safari.called)

    def test_create_unrecognized_browser_raises_error(self):
        with self.assertRaises(ValueError):
            browser_client_common.create_browser('not a real browser name')


class LoadUrlTest(ndt_client_test.NdtClientTest):
    """Tests for load_url function."""

    def test_load_url_loads_correct_url(self):
        mock_driver = mock.Mock(spec=browser_client_common.webdriver.Firefox)
        errors = []
        self.assertTrue(browser_client_common.load_url(
            mock_driver, 'http://fake.url/foo', errors))
        self.assertListEqual([], errors)
        mock_driver.get.assert_called_once_with('http://fake.url/foo')

    def test_load_url_adds_error_when_loading_url_fails(self):
        mock_driver = mock.Mock(spec=browser_client_common.webdriver.Firefox)
        mock_driver.get.side_effect = exceptions.WebDriverException(
            'dummy exception')
        errors = []
        self.assertFalse(browser_client_common.load_url(
            mock_driver, 'http://fake.url/foo', errors))
        self.assertErrorMessagesEqual(
            ['Failed to load URL: http://fake.url/foo'], errors)


if __name__ == '__main__':
    unittest.main()

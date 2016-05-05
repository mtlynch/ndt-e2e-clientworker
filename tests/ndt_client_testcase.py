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
import unittest

import mock

from client_wrapper import browser_client_common


class NdtClientTestCase(unittest.TestCase):
    """Base class for unit tests of NDT clients.

    Defines common functions needed in unit tests of NDT clients.
    """

    def assertErrorMessagesEqual(self, expected_messages, actual_errors):
        """Verifies that a list of TestErrors have the expected error messages.

        Note that this compares just by message text and ignores timestamp.
        """
        actual_messages = [e.message for e in actual_errors]
        self.assertListEqual(expected_messages, actual_messages)

    def apply_patches_for_create_browser(self):
        """Set up patches related to creating the Selenium Browser."""
        self.mock_driver = mock.Mock()
        self.mock_driver.capabilities = {'version': 'mock_version'}

        @contextlib.contextmanager
        def mock_create_browser(browser):
            yield self.mock_driver

        # Patch the call to create the browser driver to return our mock driver.
        create_browser_patcher = mock.patch.object(browser_client_common,
                                                   'create_browser')
        self.addCleanup(create_browser_patcher.stop)
        create_browser_patcher.start()
        browser_client_common.create_browser.side_effect = mock_create_browser

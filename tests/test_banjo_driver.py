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
from client_wrapper import banjo_driver
from client_wrapper import browser_client_common
from client_wrapper import names
from tests import ndt_client_test


class BanjoDriverTest(ndt_client_test.NdtClientTest):

    def setUp(self):
        self.mock_driver = mock.Mock()
        self.mock_driver.capabilities = {'version': 'mock_version'}

        # Create mock DOM elements that are returned by calls to
        # find_element_by_id.
        self.mock_elements_by_id = {
            'lrfactory-internetspeed__test_button': mock.Mock(),
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

    def test_test_records_error_when_run_test_button_is_not_in_dom(self):
        self.mock_elements_by_id['lrfactory-internetspeed__test_button'] = None

        result = self.banjo.perform_test()

        self.assertIsNone(result.latency)
        self.assertIsNone(result.s2c_result.throughput)
        self.assertIsNone(result.c2s_result.throughput)
        self.assertErrorMessagesEqual(
            [banjo_driver.ERROR_FAILED_TO_LOCATE_RUN_TEST_BUTTON],
            result.errors)


if __name__ == '__main__':
    unittest.main()

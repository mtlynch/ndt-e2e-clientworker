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
import unittest

import pytz

from client_wrapper import result_decoder
from client_wrapper import results


class NdtResultDecoderTest(unittest.TestCase):

    def setUp(self):
        self.decoder = result_decoder.NdtResultDecoder()

    def test_decodes_correctly_when_only_required_fields_are_set(self):
        encoded = """
{
    "start_time": "2016-02-26T15:51:23.452234Z",
    "end_time": "2016-02-26T15:59:33.284345Z",
    "client": "mock_client",
    "client_version": "mock_client_version",
    "browser": null,
    "browser_version": null,
    "os": "mock_os",
    "os_version": "mock_os_version",
    "c2s_start_time": null,
    "c2s_end_time": null,
    "c2s_throughput": null,
    "s2c_start_time": null,
    "s2c_end_time": null,
    "s2c_throughput": null,
    "latency": null,
    "errors": []
}"""

        decoded_expected = results.NdtResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')

        decoded_actual = self.decoder.decode(encoded)
        self.assertEqual(decoded_expected, decoded_actual)

    def test_decodes_fully_populated_result_correctly(self):
        encoded = """
{
    "start_time": "2016-02-26T15:51:23.452234Z",
    "end_time": "2016-02-26T15:59:33.284345Z",
    "client": "mock_client",
    "client_version": "mock_client_version",
    "browser": "mock_browser",
    "browser_version": "mock_browser_version",
    "os": "mock_os",
    "os_version": "mock_os_version",
    "c2s_start_time": "2016-02-26T15:51:24.123456Z",
    "c2s_end_time": "2016-02-26T15:51:34.123456Z",
    "c2s_throughput": 10.127,
    "s2c_start_time": "2016-02-26T15:51:35.123456Z",
    "s2c_end_time": "2016-02-26T15:51:45.123456Z",
    "s2c_throughput": 98.235,
    "latency": 23.8,
    "errors": [
        {
            "timestamp": "2016-02-26T15:53:29.123456Z",
            "message": "mock error message 1"
        },
        {
            "timestamp": "2016-02-26T15:53:30.654321Z",
            "message": "mock error message 2"
        }
    ]
}"""

        decoded_expected = results.NdtResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version',
            c2s_result=results.NdtSingleTestResult(
                start_time=datetime.datetime(2016, 2, 26, 15, 51, 24, 123456,
                                             pytz.utc),
                end_time=datetime.datetime(2016, 2, 26, 15, 51, 34, 123456,
                                           pytz.utc),
                throughput=10.127),
            s2c_result=results.NdtSingleTestResult(
                start_time=datetime.datetime(2016, 2, 26, 15, 51, 35, 123456,
                                             pytz.utc),
                end_time=datetime.datetime(2016, 2, 26, 15, 51, 45, 123456,
                                           pytz.utc),
                throughput=98.235),
            latency=23.8,
            browser='mock_browser',
            browser_version='mock_browser_version',
            errors=[
                results.TestError('mock error message 1',
                                  datetime.datetime(2016, 2, 26, 15, 53, 29,
                                                    123456, pytz.utc)),
                results.TestError('mock error message 2',
                                  datetime.datetime(2016, 2, 26, 15, 53, 30,
                                                    654321, pytz.utc))
            ])

        decoded_actual = self.decoder.decode(encoded)
        self.assertEqual(decoded_expected, decoded_actual)

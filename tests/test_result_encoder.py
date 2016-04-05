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
import json
import unittest

import pytz

from client_wrapper import result_encoder
from client_wrapper import results


def create_ndt_result(start_time, end_time, client, client_version, os,
                      os_version):
    result = results.NdtResult(start_time=start_time, end_time=end_time)
    result.client = client
    result.client_version = client_version
    result.os = os
    result.os_version = os_version
    return result


class NdtResultEncoderTest(unittest.TestCase):

    def setUp(self):
        # Disable maxDiff, as diffing JSON can generate large diffs
        self.maxDiff = None
        self.encoder = result_encoder.NdtResultEncoder()

    def assertJsonEqual(self, expected, actual):
        self.assertDictEqual(json.loads(expected), json.loads(actual))

    def test_encodes_correctly_when_only_required_fields_are_set(self):
        result = create_ndt_result(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')
        encoded_expected = """
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

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

    def test_encodes_correctly_when_result_includes_one_error(self):
        result = create_ndt_result(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')
        result.errors = [results.TestError(
            datetime.datetime(2016, 2, 26, 15, 53, 29, 123456, pytz.utc),
            'mock error message 1')]
        encoded_expected = """
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
    "errors": [
        {
            "timestamp": "2016-02-26T15:53:29.123456Z",
            "message": "mock error message 1"
        }
    ]
}"""

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

    def test_encodes_correctly_when_result_includes_two_errors(self):
        result = create_ndt_result(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')
        result.errors = [
            results.TestError(
                datetime.datetime(2016, 2, 26, 15, 53, 29, 123456, pytz.utc),
                'mock error message 1'),
            results.TestError(
                datetime.datetime(2016, 2, 26, 15, 53, 29, 654321, pytz.utc),
                'mock error message 2')
        ]
        encoded_expected = """
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
    "errors": [
        {
            "timestamp": "2016-02-26T15:53:29.123456Z",
            "message": "mock error message 1"
        },
        {
            "timestamp": "2016-02-26T15:53:29.654321Z",
            "message": "mock error message 2"
        }
    ]
}"""

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

    def test_encodes_fully_populated_result_correctly(self):
        result = create_ndt_result(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')
        result.c2s_result = results.NdtSingleTestResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 24, 123456,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 51, 34, 123456,
                                       pytz.utc),
            throughput=10.127)
        result.s2c_result = results.NdtSingleTestResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 35, 123456,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 51, 45, 123456,
                                       pytz.utc),
            throughput=98.235)
        result.latency = 23.8
        result.browser = 'mock_browser'
        result.browser_version = 'mock_browser_version'
        result.errors = [
            results.TestError(
                datetime.datetime(2016, 2, 26, 15, 53, 29, 123456, pytz.utc),
                'mock error message 1'),
        ]
        encoded_expected = """
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
        }
    ]
}"""

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

    def test_encodes_correctly_when_c2s_result_is_missing(self):
        result = create_ndt_result(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')
        result.s2c_result = results.NdtSingleTestResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 35, 123456,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 51, 45, 123456,
                                       pytz.utc),
            throughput=98.235)
        result.latency = 23.8
        encoded_expected = """
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
    "s2c_start_time": "2016-02-26T15:51:35.123456Z",
    "s2c_end_time": "2016-02-26T15:51:45.123456Z",
    "s2c_throughput": 98.235,
    "latency": 23.8,
    "errors": []
}"""

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

    def test_encodes_correctly_when_s2c_result_is_missing(self):
        result = create_ndt_result(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')
        result.c2s_result = results.NdtSingleTestResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 24, 123456,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 51, 34, 123456,
                                       pytz.utc),
            throughput=10.127)
        result.latency = 23.8
        encoded_expected = """
{
    "start_time": "2016-02-26T15:51:23.452234Z",
    "end_time": "2016-02-26T15:59:33.284345Z",
    "client": "mock_client",
    "client_version": "mock_client_version",
    "browser": null,
    "browser_version": null,
    "os": "mock_os",
    "os_version": "mock_os_version",
    "c2s_start_time": "2016-02-26T15:51:24.123456Z",
    "c2s_end_time": "2016-02-26T15:51:34.123456Z",
    "c2s_throughput": 10.127,
    "s2c_start_time": null,
    "s2c_end_time": null,
    "s2c_throughput": null,
    "latency": 23.8,
    "errors": []
}"""

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

    def test_encodes_correctly_when_latency_is_missing(self):
        result = create_ndt_result(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')
        result.c2s_result = results.NdtSingleTestResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 24, 123456,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 51, 34, 123456,
                                       pytz.utc),
            throughput=10.127)
        result.s2c_result = results.NdtSingleTestResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 35, 123456,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 51, 45, 123456,
                                       pytz.utc),
            throughput=98.235)
        encoded_expected = """
{
    "start_time": "2016-02-26T15:51:23.452234Z",
    "end_time": "2016-02-26T15:59:33.284345Z",
    "client": "mock_client",
    "client_version": "mock_client_version",
    "browser": null,
    "browser_version": null,
    "os": "mock_os",
    "os_version": "mock_os_version",
    "c2s_start_time": "2016-02-26T15:51:24.123456Z",
    "c2s_end_time": "2016-02-26T15:51:34.123456Z",
    "c2s_throughput": 10.127,
    "s2c_start_time": "2016-02-26T15:51:35.123456Z",
    "s2c_end_time": "2016-02-26T15:51:45.123456Z",
    "s2c_throughput": 98.235,
    "latency": null,
    "errors": []
}"""

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

    def test_encodes_zero_valued_metrics(self):
        """Explicit zeroes should be encoded as zeroes, not nulls."""
        result = create_ndt_result(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc),
            client='mock_client',
            client_version='mock_client_version',
            os='mock_os',
            os_version='mock_os_version')
        result.c2s_result = results.NdtSingleTestResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 24, 123456,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 51, 34, 123456,
                                       pytz.utc),
            throughput=0.0)
        result.s2c_result = results.NdtSingleTestResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 35, 123456,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 51, 45, 123456,
                                       pytz.utc),
            throughput=0.0)
        result.latency = 0.0
        encoded_expected = """
{
    "start_time": "2016-02-26T15:51:23.452234Z",
    "end_time": "2016-02-26T15:59:33.284345Z",
    "client": "mock_client",
    "client_version": "mock_client_version",
    "browser": null,
    "browser_version": null,
    "os": "mock_os",
    "os_version": "mock_os_version",
    "c2s_start_time": "2016-02-26T15:51:24.123456Z",
    "c2s_end_time": "2016-02-26T15:51:34.123456Z",
    "c2s_throughput": 0.0,
    "s2c_start_time": "2016-02-26T15:51:35.123456Z",
    "s2c_end_time": "2016-02-26T15:51:45.123456Z",
    "s2c_throughput": 0.0,
    "latency": 0.0,
    "errors": []
}"""

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

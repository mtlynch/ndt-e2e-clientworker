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


class NdtResultEncoderTest(unittest.TestCase):

    def setUp(self):
        # Disable maxDiff, as diffing JSON can generate large diffs
        self.maxDiff = None
        self.encoder = result_encoder.NdtResultEncoder()

    def assertJsonEqual(self, expected, actual):
        self.assertDictEqual(json.loads(expected), json.loads(actual))

    def test_encodes_correctly_when_only_required_fields_are_set(self):
        result = results.NdtResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc))
        encoded_expected = """
{
    "start_time": "2016-02-26T15:51:23.452234Z",
    "end_time": "2016-02-26T15:59:33.284345Z",
    "errors": []
}"""

        encoded_actual = self.encoder.encode(result)
        self.assertJsonEqual(encoded_expected, encoded_actual)

    def test_encodes_correctly_when_result_includes_one_error(self):
        result = results.NdtResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc))
        result.errors = [results.TestError(
            datetime.datetime(2016, 2, 26, 15, 53, 29, 123456, pytz.utc),
            'mock error message 1')]
        encoded_expected = """
{
    "start_time": "2016-02-26T15:51:23.452234Z",
    "end_time": "2016-02-26T15:59:33.284345Z",
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
        result = results.NdtResult(
            start_time=datetime.datetime(2016, 2, 26, 15, 51, 23, 452234,
                                         pytz.utc),
            end_time=datetime.datetime(2016, 2, 26, 15, 59, 33, 284345,
                                       pytz.utc))
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

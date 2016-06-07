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

from client_wrapper import http_response


class HttpResponseTest(unittest.TestCase):

    def test_identical_responses_evaluate_as_equal(self):
        a = http_response.HttpResponse(200, {'Mock-Header': 'OK'}, 'mock data')
        a_equivalent = http_response.HttpResponse(200, {'Mock-Header': 'OK'},
                                                  'mock data')
        self.assertEqual(a, a_equivalent)

    def test_different_responses_evaluate_as_unequal(self):
        # Create baseline response.
        a = http_response.HttpResponse(200, {'Mock-Header': 'OK'}, 'mock data')

        # Different response code field.
        b = http_response.HttpResponse(500, {'Mock-Header': 'OK'}, 'mock data')
        self.assertNotEqual(a, b)

        # Different header field.
        c = http_response.HttpResponse(200, {'Mock-Header': 'FAIL'},
                                       'mock data')
        self.assertNotEqual(a, c)

        # Different data field.
        d = http_response.HttpResponse(200, {'Mock-Header': 'OK'},
                                       'mock different data')
        self.assertNotEqual(a, d)

    def test_parse_yaml_can_successfully_parse_dictionary_of_responses(self):
        yaml_contents = """---
/foo: !<u!HttpResponse>
    response_code: 200
    headers: {Mock-Header: OK}
    data: foo response
/bar: !<u!HttpResponse>
    response_code: 500
    headers: {Mock-Header2: purple}
    data: bar response
"""

        expected = {
            '/foo': http_response.HttpResponse(200, {'Mock-Header': 'OK'},
                                               'foo response'),
            '/bar': http_response.HttpResponse(500, {'Mock-Header2': 'purple'},
                                               'bar response'),
        }
        self.assertEqual(expected, http_response.parse_yaml(yaml_contents))

    def test_parse_yaml_raises_exception_when_yaml_is_missing_http_response_field(
            self):
        with self.assertRaises(http_response.MissingFieldError):
            http_response.parse_yaml("""---
    !<u!HttpResponse>
        headers: {Mock-Header: OK}
        data: foo response
""")
        with self.assertRaises(http_response.MissingFieldError):
            http_response.parse_yaml("""---
    !<u!HttpResponse>
        response_code: 200
        data: foo response
""")
        with self.assertRaises(http_response.MissingFieldError):
            http_response.parse_yaml("""---
    !<u!HttpResponse>
        response_code: 200
        headers: {Mock-Header: OK}
""")


if __name__ == '__main__':
    unittest.main()

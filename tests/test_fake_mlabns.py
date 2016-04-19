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
import json
import threading
import unittest
import urllib2

from client_wrapper import fake_mlabns


class FakeMLabNsServerTest(unittest.TestCase):

    def setUp(self):
        self.server = None

    def tearDown(self):
        if self.server:
            self.server.shutdown()

    def assertJsonEqual(self, expected, actual):
        self.assertDictEqual(json.loads(expected), json.loads(actual))

    def test_server_returns_correct_fqdn(self):
        self.server = fake_mlabns.FakeMLabNsServer('ndt.mock-server.com')
        threading.Thread(target=self.server.serve_forever).start()
        response_actual = urllib2.urlopen('http://127.0.0.1:%d/ndt_ssl' %
                                          self.server.port).read()
        response_expected = """{
            "fqdn": "ndt.mock-server.com",
            "ip": ["1.2.3.4"],
            "site": "iad0t",
            "city": "Washington_DC",
            "country": "US"
            }"""

        self.assertJsonEqual(response_expected, response_actual)

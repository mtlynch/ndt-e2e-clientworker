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

from client_wrapper import canonicalize
from client_wrapper import names


class CanonicalizeTest(unittest.TestCase):

    def test_os_to_shortname_converts_recognized_platforms(self):
        self.assertEqual(names.WINDOWS_10,
                         canonicalize.os_to_shortname('Windows', '10'))
        self.assertEqual(names.UBUNTU_14,
                         canonicalize.os_to_shortname('Ubuntu', '14.04'))
        self.assertEqual(names.OSX_10_11,
                         canonicalize.os_to_shortname('OSX', '10.11.3'))

    def test_os_to_shortname_raises_error_on_unsupported_platforms(self):
        with self.assertRaises(canonicalize.UnsupportedPlatformError):
            canonicalize.os_to_shortname('SpaghettiOS', '6.7')
        with self.assertRaises(canonicalize.UnsupportedPlatformError):
            canonicalize.os_to_shortname('Windows', '7.0')
        with self.assertRaises(canonicalize.UnsupportedPlatformError):
            canonicalize.os_to_shortname('OSX', '5.6')
        with self.assertRaises(canonicalize.UnsupportedPlatformError):
            canonicalize.os_to_shortname('Ubuntu', '10.04')

    def test_browser_to_canonical_name_creates_valid_browser_strings(self):
        self.assertEqual(
            'chrome49',
            canonicalize.browser_to_canonical_name(names.CHROME, '49.0.2623'))
        self.assertEqual(
            'firefox45',
            canonicalize.browser_to_canonical_name(names.FIREFOX, '45.0'))
        self.assertEqual(
            'edge25',
            canonicalize.browser_to_canonical_name(names.EDGE, '25.10586.0.0'))
        self.assertEqual(
            'safari9',
            canonicalize.browser_to_canonical_name(names.SAFARI, '9.03'))

    def test_browser_to_canonical_name_raise_error_on_bad_version_strings(self):
        # Version string must contain a dot separator
        with self.assertRaises(canonicalize.UnrecognizedVersionStringError):
            canonicalize.browser_to_canonical_name(names.EDGE, 'banana')
        with self.assertRaises(canonicalize.UnrecognizedVersionStringError):
            canonicalize.browser_to_canonical_name(names.CHROME, '6')

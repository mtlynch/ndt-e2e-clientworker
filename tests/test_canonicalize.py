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


class CanonicalizeTest(unittest.TestCase):

    def test_os_to_shortname_raises_error_on_unsupported_platforms(self):
        self.assertEqual(names.WINDOWS_10,
                         canonicalize.os_to_shortname('Windows', '10.0'))
        self.assertEqual(names.UBUNTU_14,
                         canonicalize.os_to_shortname('Ubuntu', '14.04'))
        self.assertEqual(names.OSX_CAPITAN,
                         canonicalize.os_to_shortname('OSX', '10.11'))

    def test_os_to_shortname_raises_error_on_unsupported_platforms(self):
        with self.assertRaises(canonicalize.UnsupportedPlatformError):
            canonicalize.os_to_shortname('SpaghettiOS', '6.7')
        with self.assertRaises(canonicalize.UnsupportedPlatformError):
            canonicalize.os_to_shortname('Windows', '7.0')
        with self.assertRaises(canonicalize.UnsupportedPlatformError):
            canonicalize.os_to_shortname('OSX', '5.6')
        with self.assertRaises(canonicalize.UnsupportedPlatformError):
            canonicalize.os_to_shortname('Ubuntu', '10.04')

    def test_browser_to_shortname_creates_valid_browser_strings(self):
        self.assertEqual(
            'chrome_v49',
            canonicalize.browser_to_shortname('Chrome', '49.0.2623'))
        self.assertEqual('firefox_v45',
                         canonicalize.browser_to_shortname('Firefox', '45.0'))
        self.assertEqual(
            'edge_v25',
            canonicalize.browser_to_shortname('Edge', '25.10586.0.0'))
        self.assertEqual('safari_v9',
                         canonicalize.browser_to_shortname('Safari', '9.03'))
        # Canonicalization should support even unknown browser names.
        self.assertEqual(
            'imaginarybrowser_v7',
            canonicalize.browser_to_shortname('ImaginaryBrowser', '7.06a'))
        # The version string does not need to have a dot separator.
        self.assertEqual(
            'imaginarybrowser_v4',
            canonicalize.browser_to_shortname('ImaginaryBrowser', '4'))

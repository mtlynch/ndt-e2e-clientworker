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

from client_wrapper import filename
from client_wrapper import names
from client_wrapper import results


def get_result_filename(os, os_version, browser, browser_version, client,
                        start_time):
    """Creates an NdtResult with the given values and returns its filename."""
    result = results.NdtResult(start_time=start_time)
    result.os = os
    result.os_version = os_version
    result.client = client
    result.browser = browser
    result.browser_version = browser_version
    return filename.create_result_filename(result)


class FilenamesTest(unittest.TestCase):

    def test_creates_correct_result_filename_for_valid_browser_based_tests(
            self):
        self.assertEqual(
            'win10-chrome49-ndt_js-2016-02-26T155423Z-results.json',
            get_result_filename(os='Windows',
                                os_version='10',
                                browser=names.CHROME,
                                browser_version='49.0.2623',
                                client=names.NDT_HTML5,
                                start_time=datetime.datetime(
                                    2016, 2, 26, 15, 54, 23, 0, pytz.utc)))
        self.assertEqual(
            'osx10.11-safari9-ndt_js-2017-03-29T042116Z-results.json',
            get_result_filename(os='OSX',
                                os_version='10.11.3',
                                browser=names.SAFARI,
                                browser_version='9.0.3',
                                client=names.NDT_HTML5,
                                start_time=datetime.datetime(2017, 3, 29, 4, 21,
                                                             16, 0, pytz.utc)))
        self.assertEqual(
            'ubuntu14.04-firefox45-ndt_js-2015-09-17T080949Z-results.json',
            get_result_filename(os='Ubuntu',
                                os_version='14.04',
                                browser=names.FIREFOX,
                                browser_version='45.0',
                                client=names.NDT_HTML5,
                                start_time=datetime.datetime(2015, 9, 17, 8, 9,
                                                             49, 0, pytz.utc)))

    def test_creates_correct_result_filename_for_valid_non_browser_tests(self):
        with self.assertRaises(NotImplementedError):
            get_result_filename(os='Ubuntu',
                                os_version='14.04',
                                browser=None,
                                browser_version=None,
                                client='future client',
                                start_time=datetime.datetime(2015, 9, 17, 8, 9,
                                                             49, 0, pytz.utc))

    def test_raises_error_on_invalid_ndt_results(self):
        with self.assertRaises(filename.FilenameCreationError):
            get_result_filename(os='invalid OS',
                                os_version='14.04',
                                browser=names.FIREFOX,
                                browser_version='45.0',
                                client=names.NDT_HTML5,
                                start_time=datetime.datetime(2015, 9, 17, 8, 9,
                                                             49, 0, pytz.utc))
        with self.assertRaises(filename.FilenameCreationError):
            get_result_filename(os='Ubuntu',
                                os_version='14.04',
                                browser=names.FIREFOX,
                                browser_version='invalid version',
                                client=names.NDT_HTML5,
                                start_time=datetime.datetime(2015, 9, 17, 8, 9,
                                                             49, 0, pytz.utc))

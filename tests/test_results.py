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

import mock

from client_wrapper import results


class TestErrorTest(unittest.TestCase):

    def test_constructor_using_default_timestamp_creates_distinct_timestamps(
            self):
        """Constructing a TestError with no timestamp should use current time.

        If the caller constructs a TestError instance and uses the default value
        for the timestamp parameter, the constructor should use the timestamp at
        the time the constructor was called.
        """
        with mock.patch.object(results.datetime,
                               'datetime',
                               autospec=True) as mocked_datetime:
            mocked_datetime.now.side_effect = [datetime.datetime(2001, 1, 1),
                                               datetime.datetime(2002, 1, 1)]
            error_a = results.TestError('error A')
            error_b = results.TestError('error B')

            self.assertEqual(datetime.datetime(2001, 1, 1), error_a.timestamp)
            self.assertEqual(datetime.datetime(2002, 1, 1), error_b.timestamp)


if __name__ == '__main__':
    unittest.main()

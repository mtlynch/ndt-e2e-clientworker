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


class TestError(object):
    """Log message of an error encountered in the test.

    Attributes:
        timestamp: Datetime of when the error was observed
        message: String message describing the error.
    """

    def __init__(self, timestamp, message):
        self.timestamp = timestamp
        self.message = message


class NdtResult(object):
    """Represents the results of a complete NDT HTML5 client test.

    Attributes:
        start_time: The datetime at which tests were initiated (i.e. the time
            the driver pushed the 'Start Test' button).
        end_time: The datetime at which the tests completed (i.e. the time the
            results page loaded).
        c2s_start_time: The NdtSingleResult for the c2s (upload) test.
        s2c_start_time: The NdtSingleResult for the s2c (download) test.
        latency: The reported latency (in milliseconds).
        c2s_throughput: The reported upload (c2s) throughput (in kb/s).
        s2c_throughput: The reported download (s2c) throughput (in kb/s).
        errors: a list of TestError objects representing any errors encountered
            during the tests (or an empty list if all tests were successful).
    """

    def __init__(self,
                 start_time=None,
                 end_time=None,
                 c2s_start_time=None,
                 s2c_start_time=None,
                 errors=[],
                 latency=None,
                 c2s_throughput=None,
                 s2c_throughput=None):
        self.start_time = start_time
        self.end_time = end_time
        self.c2s_start_time = c2s_start_time
        self.s2c_start_time = s2c_start_time
        self.errors = errors
        self.latency = latency
        self.c2s_throughput = c2s_throughput
        self.s2c_throughput = s2c_throughput

    def __str__(self):
        return 'NDT Results:\n Start Time: %s,\n End Time: %s'\
        ',\n Latency: %s, \nErrors: %s' % (
            self.start_time, self.end_time, self.latency, self.errors)

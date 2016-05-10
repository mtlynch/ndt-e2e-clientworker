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

import datetime

import pytz


class NdtSingleTestResult(object):
    """Result of a single NDT test.

    Attributes:
        throughput: The final recorded throughput (in Mbps) (or None if the test
            did not complete).
        start_time: The datetime when the test began (or None if the test
            never began).
        end_time: The datetime when the test competed (or None if the test
            never completed).
    """

    def __init__(self, throughput=None, start_time=None, end_time=None):
        self.throughput = throughput
        self.start_time = start_time
        self.end_time = end_time

    def __eq__(self, other):
        return all(((self.throughput == other.throughput),
                    (self.start_time == other.start_time),
                    (self.end_time == other.end_time)))  # yapf: disable

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return ('[throughput={throughput}, '
                'start_time={start_time}, '
                'end_time={end_time}]').format(throughput=self.throughput,
                                               start_time=self.start_time,
                                               end_time=self.end_time)


class TestError(object):
    """Log message of an error encountered in the test.

    Attributes:
        message: String describing the error.
        timestamp: Datetime of when the error was observed.
    """

    def __init__(self, message, timestamp=None):
        self._message = message
        if timestamp:
            self._timestamp = timestamp
        else:
            self._timestamp = datetime.datetime.now(pytz.utc)

    def __eq__(self, other):
        return all(((self.message == other.message),
                    (self.timestamp == other.timestamp)))  # yapf: disable

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '[message={message}, timestamp={timestamp}]'.format(
            message=self.message,
            timestamp=self.timestamp)

    @property
    def message(self):
        return self._message

    @property
    def timestamp(self):
        return self._timestamp


class NdtResult(object):
    """Represents the results of a complete NDT HTML5 client test.

    Attributes:
        start_time: The datetime at which the NDT client was launched. This is
            time at which the client wrapper begins running a particular client,
            but is not necessarily the time at which the client itself initiated
            a test.
        end_time: The datetime at which the NDT client completed. This should be
            equal to the end_time of the client's last test or the time of a
            fatal error in the client.
        errors: A list of TestError objects representing any errors encountered
            during the tests (or an empty list if all tests were successful).
        c2s_result: The NdtSingleResult for the c2s (upload) test.
        s2c_result: The NdtSingleResult for the s2c (download) test.
        latency: The reported latency (in milliseconds) or None if the test did
            not complete.
        os: Name of OS in which the test ran (e.g. "Windows").
        os_version: OS version string (e.g. "10.0").
        client: Shortname of the NDT client (e.g. "ndt_js").
        client_version: Version string of the NDT client (e.g. "4.0.1").
        browser: Name of browser through which the test was performed (or None
            for a non-browser test).
        browser_version: Browser's version string (or None for a non-browser
            test).
    """

    def __init__(self,
                 start_time=None,
                 end_time=None,
                 errors=None,
                 c2s_result=None,
                 s2c_result=None,
                 latency=None,
                 os=None,
                 os_version=None,
                 client=None,
                 client_version=None,
                 browser=None,
                 browser_version=None):
        self.start_time = start_time
        self.end_time = end_time
        self.c2s_result = c2s_result if c2s_result else NdtSingleTestResult()
        self.s2c_result = s2c_result if s2c_result else NdtSingleTestResult()
        self.errors = errors if errors else []
        self.latency = latency
        self.os = os
        self.os_version = os_version
        self.client = client
        self.client_version = client_version
        self.browser = browser
        self.browser_version = browser_version

    def __eq__(self, other):
        return all((
            (self.start_time == other.start_time),
            (self.end_time == other.end_time),
            (self.c2s_result == other.c2s_result),
            (self.s2c_result == other.s2c_result),
            (self.latency == other.latency),
            (self.os == other.os),
            (self.os_version == other.os_version),
            (self.client == other.client),
            (self.client_version == other.client_version),
            (self.browser == other.browser),
            (self.browser_version == other.browser_version)))  # yapf: disable

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return ('[start_time={start_time}, '
                'end_time={end_time}, '
                'errors={errors}, '
                'c2s_result={c2s_result}, '
                's2c_result={s2c_result}, '
                'latency={latency}, '
                'os={os}, '
                'os_version={os_version}, '
                'client={client}, '
                'client_version={client_version}, '
                'browser={browser}, '
                'browser_version={browser_version}]').format(
                    start_time=self.start_time,
                    end_time=self.end_time,
                    errors=[str(e) for e in self.errors],
                    c2s_result=str(self.c2s_result),
                    s2c_result=str(self.s2c_result),
                    latency=self.latency,
                    os=self.os,
                    os_version=self.os_version,
                    client=self.client,
                    client_version=self.client_version,
                    browser=self.browser,
                    browser_version=self.browser_version)

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

import json

import dateutil.parser

import results


class NdtResultDecoder(json.JSONDecoder):
    """Decodes a JSON string into an NdtResult instance.

    The decoder assumes that the input is valid JSON and that the JSON
    represents a valid NdtResult (where all required fields are defined and all
    defined fields have legal values).
    """

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=_dict_to_object)


def _dict_to_object(d):
    """Converts dictionary items in an NdtResult JSON string into objects."""
    # Check if this is a TestError dict.
    if ('timestamp' in d) and ('message' in d):
        return _decode_error(d)
    return _decode_ndt_result(d)


def _decode_error(error):
    """Decodes a dictionary into a TestError instance."""
    return results.TestError(error['message'], _decode_time(error['timestamp']))


def _decode_ndt_result(result):
    """Decodes a dictionary into an NdtResult instance."""
    return results.NdtResult(
        start_time=_decode_time(result['start_time']),
        end_time=_decode_time(result['end_time']),
        client=result['client'],
        client_version=result['client_version'],
        os=result['os'],
        os_version=result['os_version'],
        browser=result['browser'],
        browser_version=result['browser_version'],
        c2s_result=results.NdtSingleTestResult(
            throughput=result['c2s_throughput'],
            start_time=_decode_time(result['c2s_start_time']),
            end_time=_decode_time(result['c2s_end_time'])),
        s2c_result=results.NdtSingleTestResult(
            throughput=result['s2c_throughput'],
            start_time=_decode_time(result['s2c_start_time']),
            end_time=_decode_time(result['s2c_end_time'])),
        latency=result['latency'],
        errors=result['errors'])


def _decode_time(time):
    """Decodes a time string

    Args:
        time: A time in ISO-8601 string format.

    Returns:
        A datetime corresponding to the specified time or None if time was None
        or an empty string.
    """
    if not time:
        return None
    # We need to use dateutil to parse because datetime.strptime can't parse
    # time zones.
    return dateutil.parser.parse(time)

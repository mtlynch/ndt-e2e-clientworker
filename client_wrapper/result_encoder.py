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
import json

import results


class NdtResultEncoder(json.JSONEncoder):
    """Encodes an NdtResult instance into JSON.

    Given a populated NdtResult instance, serializes the result to JSON.

    The encoder assumes that:

    * NdtResult's required fields (those not documented as allowing None
        values) are populated
    * All populated fields are valid

    In other words, it is caller's responsibility to pass valid data.
    """

    def default(self, obj):
        if isinstance(obj, results.NdtResult):
            return _encode_ndt_result(obj)
        elif isinstance(obj, results.TestError):
            return _encode_error(obj)
        elif isinstance(obj, datetime.datetime):
            return _encode_time(obj)
        return json.JSONEncoder.default(self, obj)


def _encode_ndt_result(result):
    result_dict = {
        'start_time': result.start_time,
        'end_time': result.end_time,
        'client': result.client,
        'client_version': result.client_version,
        'os': result.os,
        'os_version': result.os_version,
        'errors': result.errors,
    }
    # Flatten out c2s result so that all fields are in the root of the overall
    # NDT result.
    if result.c2s_result:
        result_dict['c2s_start_time'] = result.c2s_result.start_time
        result_dict['c2s_end_time'] = result.c2s_result.end_time
        result_dict['c2s_throughput'] = result.c2s_result.throughput
    else:
        result_dict['c2s_start_time'] = None
        result_dict['c2s_end_time'] = None
        result_dict['c2s_throughput'] = None

    # Flatten out s2c result so that all fields are in the root of the overall
    # NDT result.
    if result.s2c_result:
        result_dict['s2c_start_time'] = result.s2c_result.start_time
        result_dict['s2c_end_time'] = result.s2c_result.end_time
        result_dict['s2c_throughput'] = result.s2c_result.throughput
    else:
        result_dict['s2c_start_time'] = None
        result_dict['s2c_end_time'] = None
        result_dict['s2c_throughput'] = None
    result_dict['latency'] = result.latency
    result_dict['browser'] = result.browser
    result_dict['browser_version'] = result.browser_version

    return result_dict


def _encode_error(error):
    return {'timestamp': error.timestamp, 'message': error.message}


def _encode_time(time):
    return datetime.datetime.strftime(time, '%Y-%m-%dT%H:%M:%S.%fZ')

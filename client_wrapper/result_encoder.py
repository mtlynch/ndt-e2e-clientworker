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
    # TODO(mtlynch): Implement encoding for NdtResult's other fields.

    return result_dict


def _encode_error(error):
    return {'timestamp': error.timestamp, 'message': error.message}


def _encode_time(time):
    return datetime.datetime.strftime(time, '%Y-%m-%dT%H:%M:%S.%fZ')

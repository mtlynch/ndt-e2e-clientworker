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
    """Encodes an NdtResult instance into JSON."""

    def default(self, obj):
        if isinstance(obj, results.NdtResult):
            return self._encode_ndt_result(obj)
        return json.JSONEncoder.default(self, obj)

    def _encode_ndt_result(self, result):
        result_dict = {
            'start_time': _encode_time(result.start_time),
            'end_time': _encode_time(result.end_time),
            'errors': _encode_errors(result.errors),
        }
        # TODO(mtlynch): Implement encoding for NdtResult's other fields.

        return result_dict


def _encode_errors(errors):
    return [_encode_error(e) for e in errors]


def _encode_error(error):
    return {
        'timestamp': _encode_time(error.timestamp),
        'message': error.message,
    }


def _encode_time(time):
    return datetime.datetime.strftime(time, '%Y-%m-%dT%H:%M:%S.%fZ')

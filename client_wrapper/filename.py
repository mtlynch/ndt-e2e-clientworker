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

import canonicalize


class Error(Exception):
    pass


class FilenameCreationError(Error):
    pass


_FILENAME_FORMAT = ('{os}-{browser}-{client}-{timestamp}-{type}.{extension}')


def create_result_filename(result):
    """Create an output filename based on an NdtResult.

    Args:
        result: NdtResult instance for which to create an output filename.

    Returns:
        An output filename representing the result, for example:

            win10-chrome49-ndt_js-2016-02-26T155423Z-results.json
    """
    if not result.browser:
        raise NotImplementedError(
            'support for non-browser test filenames is not yet implemented')
    try:
        os = canonicalize.os_to_shortname(result.os, result.os_version)
        browser = canonicalize.browser_to_canonical_name(result.browser,
                                                         result.browser_version)
    except canonicalize.Error as e:
        raise FilenameCreationError(
            'Could not generate filename for NDT result: %s' % e.message)
    client = result.client
    timestamp = _format_time(result.start_time)
    return _FILENAME_FORMAT.format(os=os,
                                   browser=browser,
                                   client=client,
                                   timestamp=timestamp,
                                   type='results',
                                   extension='json')


def _format_time(timestamp):
    return timestamp.strftime('%Y-%m-%dT%H%M%SZ')

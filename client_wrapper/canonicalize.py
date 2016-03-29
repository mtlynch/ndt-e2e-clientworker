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

import names


class Error(Exception):
    pass


class UnsupportedPlatformError(Error):
    pass


def os_to_shortname(os, os_version):
    """Converts an OS name and version to its shortname.

    Given an OS name and OS version, return the OS shortname (e.g. 'win10').

    Args:
        os: The OS platform name (e.g. "Windows" or "Ubuntu").
        os_version: The version string for the platform in the form x.y where x
            is the major version and y is the minor version.

    Returns:
        The os shortname for the OS and version.

    Raises:
        UnsupportedPlatformError if the caller specifies an OS and version
        combination that does not have a known shortname.
    """
    shortname_map = {
        #TODO(mtlynch): Check whether this is the right version string for
        # Win10.
        'Windows-10.0': names.WINDOWS_10,
        'Ubuntu-14.04': names.UBUNTU_14,
        #TODO(mtlynch): Check whether this is the right version string for
        # El Capitan.
        'OSX-10.11': names.OSX_CAPITAN,
    }
    key = '%s-%s' % (os, os_version)
    try:
        return shortname_map[key]
    except KeyError:
        raise UnsupportedPlatformError('Unsupported OS platform: %s v%s' %
                                       (os, os_version))


def browser_to_shortname(browser, browser_version):
    """Converts a browser and version to its shortname.

    Converts a browser to the format of "[name]_v[major version]", e.g.
    "firefox_v49".

    Args:
        browser: Browser name to convert to shortname (e.g. "Firefox" or "Edge")
        browser_version: Browser version string. If this contains dots, the
            portion before the first dot is treated as the major version. If
            there are no dots, the full string is treated as the major version.

    Returns:
        Returns the browser in shortname form, e.g. "firefox_v49".
    """
    version_parts = browser_version.split('.')
    return '%s_v%s' % (browser.lower(), version_parts[0])

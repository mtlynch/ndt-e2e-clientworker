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

import platform


def get_os_metadata():
    """Retrieves the OS name and version for the host system.

    Retrieves the OS name and OS version string for the host system. The OS name
    can be "Windows", "OSX", the name of the Linux distribution, or, if the OS
    is none of those, the name will be the OS platform name. The version string
    is the version that corresponds to the OS or distribution (not the OS
    kernel).

    Returns:
        A two-tuple of OS name and OS version string. Examples:

            ('Windows', '10')
            ('OSX', '10.11.3')
            ('Ubuntu', '14.04')
    """
    os_name = platform.system()
    if os_name == 'Linux':
        return _get_linux_metadata()
    elif os_name == 'Darwin':
        return _get_osx_metadata()
    return os_name, platform.release()


def _get_linux_metadata():
    linux_distribution, distribution_version, _ = platform.linux_distribution()
    return linux_distribution, distribution_version


def _get_osx_metadata():
    return 'OSX', platform.mac_ver()[0]

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

import yaml


class Error(Exception):
    pass


class MissingFieldError(Error):
    """Error raised when YAML-serialized HttpResponse is missing fields."""

    def __init__(self, field):
        super(MissingFieldError, self).__init__(
            'Failed to parse HttpResponse from yaml, missing expected field: %s'
            % field)


class HttpResponse(yaml.YAMLObject):
    """Representation of an HTTP server response.

    Attributes:
        response_code: The response code of the HTTP response (e.g. 200).
        headers: A dictionary of key-value pairs representing the HTTP headers
            in the response.
        data: The data payload of the HTTP response.
    """

    yaml_tag = 'u!HttpResponse'

    def __init__(self, response_code, headers, data):
        self.response_code = response_code
        self.headers = headers
        self.data = data

    def __eq__(self, other):
        if not other:
            return False
        return all(((self.response_code == other.response_code),
                    (self.headers == other.headers), (self.data == other.data)))

    def __ne__(self, other):
        return not self.__eq__(other)


def parse_yaml(yaml_contents):
    """Parses a YAML string, deserializing any HttpResponse objects.

    Args:
        yaml_contents: The YAML string to parse.

    Returns:
        The parsed contents of the YAML string.

    Raises:
        MissingFieldError: The YAML contained an HttpResponse object without all
            of its fields.
    """
    yaml.add_constructor(HttpResponse.yaml_tag, _http_response_constructor)
    return yaml.load(yaml_contents)


def _http_response_constructor(loader, node):
    """Inner method to define a parsing constructor for HttpResponse.

    Constructs a parsing constructor for HttpResponse. See:
    http://pyyaml.org/wiki/PyYAMLDocumentation for details.

    Args:
        loader: PyYAML loader instance.
        node: PyYAML node instance.

    Returns:
        Populated HttpResponse instance.

    Raises:
        MissingFieldError: The YAML contained an HttpResponse object without all
            of its fields.
    """
    values = loader.construct_mapping(node)
    try:
        response_code = values['response_code']
    except KeyError:
        raise MissingFieldError('response_code')
    try:
        headers = values['headers']
    except KeyError:
        raise MissingFieldError('headers')
    try:
        data = values['data']
    except KeyError:
        raise MissingFieldError('data')
    return HttpResponse(response_code, headers, data)

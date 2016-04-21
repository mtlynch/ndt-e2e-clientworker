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
import BaseHTTPServer


class FakeMLabNsServer(BaseHTTPServer.HTTPServer):
    """A fake implementation of mlab-ns that returns a specified NDT server.

    A fake implementation of mlab-ns that returns a static HTTP response to
    every GET request. The response specifies a caller-defined FQDN. This is
    intended for testing NDT clients that have mlab-ns logic baked in, so if we
    can redirect the call to this fake mlab-ns server, we can control the NDT
    server that the client connects to.

    The HTTP server listens on all available interfaces and chooses a random
    available TCP port to listen on.

    Details on the mlab-ns protocol are available at: http://goo.gl/48S22

    Attributes:
        server_fqdn: FQDN of M-Lab server to specify in mlab-ns response.
        port: Local port that server is listening on.
    """

    def __init__(self, server_fqdn):
        BaseHTTPServer.HTTPServer.__init__(self, ('', 0), _FakeMLabNsHandler)
        self._port = self.server_address[1]
        self._server_fqdn = server_fqdn

    @property
    def server_fqdn(self):
        return self._server_fqdn

    @property
    def port(self):
        return self._port


class _FakeMLabNsHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        """Send an mlab-ns response to all GET requests.

        Send an mlab-ns style JSON response to any GET requests. All fields of
        the response are hardcoded, static values except for the 'fqdn' field,
        which is set based on the hosting server's server_fqdn field.
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # Allow CORS requests, so that we can query the fake mlab-ns server from
        # different origins (e.g. different localhost:port combinations).
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            'ip': ['1.2.3.4'],
            'country': 'US',
            'city': 'Washington_DC',
            'fqdn': self.server.server_fqdn,
            'site': 'iad0t'
        }
        self.wfile.write(json.dumps(response))

    def log_message(self, unused_format, *args):
        """Silence console output."""
        pass

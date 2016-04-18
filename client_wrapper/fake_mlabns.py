import time
import json
import BaseHTTPServer




class FakeMLabNsServer(BaseHTTPServer.HTTPServer):

    def __init__(self, ndt_server_fqdn):
        BaseHTTPServer.HTTPServer.__init__(self, ('', 0), _FakeMLabNsHandler)
        self._port = self.socket.getsockname()[1]
        self._ndt_server_fqdn = ndt_server_fqdn

    @property
    def ndt_server_fqdn(self):
        return self._ndt_server_fqdn

    @property
    def port(self):
        return self._port

class _FakeMLabNsHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'ip': ['1.2.3.4'],
            'country': 'US',
            'city': 'Washington_DC',
            'fqdn': self.server.ndt_server_fqdn,
            'site': 'iad0t'
        }
        self.wfile.write(json.dumps(response))


if __name__ == '__main__':
    httpd = FakeMLabNsServer('iupui.ndt.foo.com')
    print time.asctime(), "Server Starts - :%s" % (HOST_NAME, httpd.port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

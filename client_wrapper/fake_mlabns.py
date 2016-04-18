import time
import BaseHTTPServer

HOST_NAME = ''
PORT_NUMBER = 8123


class FakeMLabNsHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write("""{
            "ip": ["1.2.3.4"],
            "country": "US", '
            "city": "Washington_DC",
            "fqdn": "%s",
            "site": "iad0t"
            }""" % self.server.ndt_server_fqdn)


class FakeMLabNsServer(BaseHTTPServer.HTTPServer):

    def __init__(self, server_address, RequestHandlerClass, ndt_server_fqdn):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.ndt_server_fqdn = ndt_server_fqdn


if __name__ == '__main__':
    httpd = FakeMLabNsServer((HOST_NAME, PORT_NUMBER), FakeMLabNsHandler, 'iupui.ndt.foo.com')
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)

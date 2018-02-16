import sys
import socket

from io import StringIO
from email.utils import formatdate

from grin_wsgi.http.http import Request, Response
from grin_wsgi.http.server import SimpleHTTPServer, \
    ThreadedHTTPServer, MultiprocessingHTTPServer


class WSGIRequestHandler:

    def __init__(self, application):
        self._application = application
        self._response = Response()
        self._request = Request()

    def __call__(self, request):
        self._request.plain_request = request
        env = self._get_environ(self._request)
        response_body = self._application(env, self._start_response)

        self._finish_response(response_body)

    def _get_environ(self, request):
        env = {}

        # Required UWSGI variables
        env['wsgi.input'] = StringIO(request.body)
        env['wsgi.errors'] = sys.stderr

        # Required CGI variables
        env['REQUEST_METHOD'] = request.method
        env['PATH_INFO'] = request.uri
        env['SERVER_NAME'] = socket.getfqdn(request.host)
        env['SERVER_PORT'] = request.port
        env['QUERY_STRING'] = request.query_string
        env['CONTENT_LENGTH'] = request.content_length

        return env

    def _start_response(self, status, response_headers, exc_info=None):
        server_headers = [
            ('Date', formatdate(timeval=None, localtime=False, usegmt=True)),
            ('Server', 'WSGIServer 0.2')
        ]

        self._response.status = status
        self._response.headers = response_headers + server_headers

    def _finish_response(self, response_body):
        self._response.body = response_body
        print('Response: ', self._response.get_response().decode('utf-8'))
        return self._response.get_response()


class WSGIServer:

    http_server_factory = {
        'simple': SimpleHTTPServer,
        'threading': ThreadedHTTPServer,
        'processing': MultiprocessingHTTPServer
    }

    def __init__(self, host, port, application,
                 threads=False, multiprocs=False):
        self._server = self._make_server(host, port, threads, multiprocs)
        self._application = application

    def _make_server(self, host, port, threads, processing):
        server_type = 'simple'
        if threads: server_type = 'threading'
        if processing: server_type = 'processing'

        return self.http_server_factory[server_type](host, port)

    def serve_forever(self):
        request_handler = WSGIRequestHandler(self._application)
        self._server.process_request(request_handler)

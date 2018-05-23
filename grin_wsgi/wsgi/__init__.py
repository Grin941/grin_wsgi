import sys
import socket
import typing

from io import StringIO
from email.utils import formatdate

from grin_wsgi.http import Request, Response, server as http_server


__all__ = ['make_server', 'WSGIRequestHandler', 'WSGIServer']


def make_server(
    host: str,
    port: int,
    application: typing.Callable,
    threading: typing.Optional[bool]=False,
    multiprocessing: typing.Optional[bool]=False,
    wsgiref: typing.Optional[bool]=False
) -> typing.Any:  # pragma: no cover
    """
    Create a new WSGI listening on host and port,
    accepting connections for application.
    You may create either SimpleHTTPServer or
    Threading or Multiprocessing HTTPServer.
    """
    if wsgiref:
        from wsgiref.simple_server import make_server as wsgi_server
    else:
        wsgi_server = WSGIServer

    return wsgi_server(host, port, application, threading, multiprocessing)


class WSGIRequestHandler:  # pragma: no cover
    """
    Create an HTTP handler for the given request,
    client_address (a (host,port) tuple), and server (WSGIServer instance).
    """

    def __init__(
        self,
        application: typing.Callable,
        server_multithread: typing.Optional[bool]=False,
        server_multiprocess: typing.Optional[bool]=False
    ) -> None:

        self._application = application
        self._response = Response()
        self._request = Request()

        self._server_multithread = server_multithread
        self._server_multiprocess = server_multiprocess

    def __call__(
        self,
        request: str
    ) -> bytes:
        """ Process the HTTP request. """
        self._request.plain_request = request
        env = self._get_environ(self._request)
        response_body = self._application(env, self._start_response)

        return self._finish_response(response_body)

    def _get_environ(
        self,
        request: Request
    ) -> typing.Dict[str, typing.Any]:
        """
        Returns a dictionary containing the WSGI environment for a request.
        """
        env = {}

        # Required UWSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO(request.body)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = self._server_multithread
        env['wsgi.multiprocess'] = self._server_multiprocess
        env['wsgi.run_once'] = False

        # Required CGI variables
        env['METHOD'] = request.method
        env['PATH_INFO'] = request.uri
        env['SERVER_NAME'] = socket.getfqdn(request.host)
        env['SERVER_PORT'] = request.port
        env['QUERY_STRING'] = request.query_string
        env['CONTENT_LENGTH'] = request.content_length

        return env

    def _start_response(
        self,
        status: str,
        response_headers: typing.List[typing.Tuple[str, str]],
        exc_info: typing.Optional=None
    ) -> None:
        server_headers = [
            ('Date', formatdate(timeval=None, localtime=False, usegmt=True)),
            ('Server', 'WSGIServer 0.2')
        ]

        self._response.status = status
        self._response.headers = response_headers + server_headers

    def _finish_response(self, response_body):
        self._response.body = response_body
        return self._response.get_response()


class WSGIServer:
    """
    Create a WSGIServer instance.
    """
    http_server_factory = {
        'simple': http_server.SimpleHTTPServer,
        'threading': http_server.ThreadedHTTPServer,
        'processing': http_server.MultiprocessingHTTPServer
    }

    def __init__(
        self,
        host: str,
        port: int,
        application: typing.Callable,
        threads: typing.Optional[bool]=False,
        multiprocs: typing.Optional[bool]=False
    ) -> None:
        self._server = self._make_server(host, port, threads, multiprocs)
        self._application = application

    def _make_server(
        self,
        host: str,
        port: int,
        threads: bool,
        processing: bool
    ) -> typing.Any:
        server_type = 'simple'
        if threads: server_type = 'threading'
        if processing: server_type = 'processing'

        return self.http_server_factory[server_type](host, port)

    def serve_forever(self) -> None:
        """ Handle requests until an explicit shutdown() request. """
        request_handler = WSGIRequestHandler(
            self._application,
            server_multithread=self._server.MULTITHREAD,
            server_multiprocess=self._server.MULTIPROCESS)
        self._server.process_request(request_handler)

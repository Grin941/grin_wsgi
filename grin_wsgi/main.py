import sys
import socket
import threading
import multiprocessing

from io import StringIO
from email.utils import formatdate


class SimpleHTTPServer:

    CONNECTION_QUEUE_LIMIT = 1
    SOCKET_FAMILY = socket.AF_INET
    SOCKET_TYPE = socket.SOCK_STREAM

    def __init__(self, host, port):
        self._serversock = None
        self._create_serversocket(host, port)

    def _create_serversocket(self, host, port):
        self._serversock = socket.socket(self.SOCKET_FAMILY, self.SOCKET_TYPE)
        self._serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._serversock.bind((host, port))

    def process_request(self, request_handler):
        self._serversock.listen(self.CONNECTION_QUEUE_LIMIT)
        while True:
            self._accept(request_handler)

    def _accept(self, request_handler):
        clientsock, address = self._serversock.accept()
        try:
            request = clientsock.recv(1024).decode('utf-8')
            print('Request: ', request)
            if not request: raise
            response = request_handler(request)
            clientsock.sendall(response)
        except Exception:
            clientsock.close()
            return False


class ThreadedHTTPServer(SimpleHTTPServer):

    CONNECTION_QUEUE_LIMIT = 5

    def _accept(self):
        clientsock, address = self._serversock.accept()
        clientsock.settimeout(60)
        threading.Thread(target=self.listen_to_client,
                         args=(clientsock, address))


class MultiprocessingHTTPServer(SimpleHTTPServer):

    CONNECTION_QUEUE_LIMIT = 1

    def _accept(self):
        clientsock, address = self._serversock.accept()
        process = multiprocessing.Process(target=self.listen_to_client,
                                          args=(clientsock, address))
        process.daemon = True
        process.start()


def parse_request_query_string(query_string):
    request_dict = {}
    for key, value in _request_query_string_as_list_of_tuples(query_string):
        if key in request_dict:
            request_dict[key].extend(value)
        else:
            request_dict[key] = value

    return request_dict


# TODO: realize unquote() -> '%20' = ' '
def _request_query_string_as_list_of_tuples(query_string):
    key_value_pairs = []

    request_string_key_value_pairs = query_string.split('&')
    for key_value_pair in request_string_key_value_pairs:
        key, value_set = key_value_pair.split('=')
        key_value_pairs.append((key,
                                value_set.replace('+', ' ').split(';')))

    return key_value_pairs


class Response:

    def __init__(self):
        self._status = None
        self._headers = None
        self._body = None

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, response_status):
        self._status = response_status

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, response_headers):
        # Response headers is a list of tuples
        self._headers = response_headers

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, response_body):
        self._body = response_body

    def get_response(self):
        response = 'HTTP/1.1 {status}\r\n'.format(status=self._status)
        for header in self._headers:
            response += '{0}: {1}\r\n'.format(*header)
        response += '\r\n'
        for data in self._body:
            response += data.decode('utf-8')

        return response.encode('utf-8')


class Request:

    def __init__(self):
        self._plain_request = None
        self.data = None

    def __getattr__(self, name):
        return self.data[name]

    @property
    def plain_request(self):
        return self._plain_request

    @plain_request.setter
    def plain_request(self, plain_request):
        self._parse_request(plain_request)
        self._plain_request = plain_request

    def _parse_request(self, request):
        request_list = request.splitlines()

        request_line = request_list[0]
        host_header = next(filter(lambda x: 'Host:' in x, request_list), '::')
        content_length_header = next(
            filter(lambda x: 'Content-Length:' in x, request_list), ':')

        http_method, uri, http_version = request_line.split()
        host, port = host_header.split(':')[1:]
        content_length = content_length_header.split(':')[1]
        query_string = uri.split('?')[1] if '?' in uri else ''
        body = request_list[-1]

        self.data = {
            'method': http_method,
            'uri': uri,
            'version': http_version,
            'host': host,
            'port': port,
            'content_length': content_length,
            'query_string': query_string,
            'body': body,
        }


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
        self.server = self._make_server(host, port, threads, multiprocs)
        self.application = application

    def _make_server(self, host, port, threads, processing):
        server_type = 'simple'
        if threads: server_type = 'threading'
        if processing: server_type = 'processing'

        return self.http_server_factory[server_type](host, port)

    def serve_forever(self):
        request_handler = WSGIRequestHandler(application)
        self.server.process_request(request_handler)


def make_server(host, port, application,
                threads=False, multiprocs=False):
    return WSGIServer(host, port, application)


def application(
        environ,  # dictionary containing CGI like environment
        start_response
):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    request_method = environ['REQUEST_METHOD']
    request_body = environ['QUERY_STRING'] if request_method == 'GET' else \
        environ['wsgi.input'].read(request_body_size)
    print('Request body: ', request_body)

    print('Parsed: ', parse_request_query_string(str(request_body)))
    response_body = '\n'.join([
        '{} {}'.format(k, v) for k, v in
        sorted(parse_request_query_string(str(request_body)).items())
    ])
    print('Response body: ', response_body)
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body.encode("utf-8")]


def run(host='localhost', port=8051, application=application,
        threads=False, multiprocs=False):
    httpd = make_server(host, port, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=port))
    httpd.serve_forever()

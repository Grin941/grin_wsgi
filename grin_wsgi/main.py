import sys
import socket
import threading
import multiprocessing

from io import StringIO


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
            request = clientsock.recv(1024)
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
        response = b'HTTP/1.1 {status}\r\n'.format(status=self._status)
        for header in self._headers:
            response += b'{0}: {1}\r\n'.format(*header)
        response += b'\r\n'
        for data in self._body:
            response += data

        return response


class WSGIRequestHandler:

    def __init__(self, application):
        self._application = application
        self._response = Response()

    def __call__(self, request):
        env = self._get_environ(request)
        response_body = self.application(env, self._start_response)

        self.finish_response(response_body)

    def _get_environ(self, request):
        env = {}

        request_method, uri, request_version, host, port = \
            self._parse_request(request)

        # Required UWSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        # Required CGI variables
        env['REQUEST_METHOD'] = request_method
        env['PATH_INFO'] = uri
        env['SERVER_NAME'] = socket.getfqdn(host)
        env['SERVER_PORT'] = port

        return env

    def _parse_request(self, request):
        request_list = request.splitlines()
        request_line, host_header = request_list[0:2]

        http_method, uri, http_version = request_line.split()
        host, port = host_header.split(b':')[1:]

        return http_method, uri, http_version, host, port

    def _start_response(self, status, response_headers, exc_info=None):
        server_headers = [
            ('Date', ''),
            ('Server', 'WSGIServer 0.2')
        ]

        self._response.status = status
        self._response.headers = response_headers + server_headers

    def _finish_response(self, response_body):
        self._response.body = response_body
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
    request_method = environ['REQUEST_METHOD']
    if request_method == 'GET':
        request_body = environ['QUERY_STRING']
    else:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError: request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size)

    response_body = '\n'.join([
        '{} {}'.format(k, v) for k, v in
        sorted(parse_request_query_string(str(request_body)).items())
    ])
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


if __name__ == '__main__':
    host, port = 'localhost', 8051
    threads = multiprocs = False

    if len(sys.argv) < 2:
        application = application
        # sys.exit('Provide a WSGI application object as module:callable')
    else:
        app_path = sys.argv[1]
        module, application = app_path.split(':')
        module = __import__(module)
        application = getattr(module, application)
    run(host, port, application, threads, multiprocs)

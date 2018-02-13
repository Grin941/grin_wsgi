import socket
import threading
import multiprocessing


from wsgiref.simple_server import make_server


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


class SimpleHTTPServer:

    CONNECTION_QUEUE_LIMIT = 1

    def __init__(self, host, port):
        self._serversock = None
        self._create_serversocket(host, port)

    def _create_serversocket(self, host, port):
        self._serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._serversock.bind((host, port))

    def listen(self):
        self._serversock.listen(self.CONNECTION_QUEUE_LIMIT)
        while True:
            self.accept()

    def accept(self):
        clientsock, address = self._serversock.accept()
        self.listen_to_client(clientsock, address)

    def listen_to_client(self, clientsock, address):
        while True:
            try:
                request = clientsock.recv(1024)
                if not request: raise
                # TODO: generate Response
                clientsock.send(request)
            except Exception:
                clientsock.close()
                return False


class ThreadedHTTPServer(SimpleHTTPServer):

    CONNECTION_QUEUE_LIMIT = 5

    def accept(self):
        clientsock, address = self._serversock.accept()
        clientsock.settimeout(60)
        threading.Thread(target=self.listen_to_client,
                         args=(clientsock, address))


class MultiprocessingHTTPServer(SimpleHTTPServer):

    CONNECTION_QUEUE_LIMIT = 1

    def accept(self):
        clientsock, address = self._serversock.accept()
        process = multiprocessing.Process(target=self.listen_to_client,
                                          args=(clientsock, address))
        process.daemon = True
        process.start()


def application(
        environ,  # dictionary containing CGI like environment
        start_response  # dictionary containing CGI like environment
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


def run():
    httpd = make_server('localhost', 8051, application)
    httpd.serve_forever()


if __name__ == '__main__':
    run()

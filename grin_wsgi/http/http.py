class Response:

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

    def get_response(self):
        response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
        for header in self.headers:
            response += '{0}: {1}\r\n'.format(*header)
        response += '\r\n'
        for data in self.body:
            response += data.decode('utf-8')

        return response.encode('utf-8')


class Request:

    def __init__(self):
        self._plain_request = None

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

        self.method, self.uri, self.version = request_line.split()
        self.host, self.port = host_header.split(':')[1:]
        self.content_length = content_length_header.split(':')[1]
        self.query_string = self.uri.split('?')[1] if '?' in self.uri else ''
        self.body = request_list[-1]

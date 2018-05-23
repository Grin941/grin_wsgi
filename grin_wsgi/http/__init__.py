import typing

__all__ = ['Response', 'Request']


class Response:
    """ HTTPResponse class.
    Each instance constains such attributes::

    status
        Response status

    headers
        List of tuples containing (Header key, header value)

    body
        Iterable returned by an application() UWSGI callable
    """

    def __setattr__(
        self,
        name: str,
        value: typing.Any
    ) -> None:
        """ Set Response attributes (status, headers, body). """
        super().__setattr__(name, value)

    def get_response(self) -> bytes:
        """ Generate full response string """
        response = f'HTTP/1.1 {self.status}\r\n'
        for header in self.headers:
            http_header_name, http_header_value = header
            response += f'{http_header_name}: {http_header_value}\r\n'
        response += '\r\n'
        for data in self.body:
            response += data.decode('utf-8')

        return response.encode('utf-8')


class Request:
    """ HTTPRequest class.
    Request instance is forming from a plain request string
    passed from a web server.
    Each instance constains such attributes::

    plain_request
        Plain request string passed from a web server

    method
        HttpRequest method: GET, POST, PUT, etc.

    uri
       equest URI

    version
        protocol version

    host
        source client host

    port
        source client port

    content_length
        Content-Length header value

    query_string
        query string for GET method or empty string elsewhere

    body
        empty string for GET request or Request data for a POST request
    """

    def __init__(self) -> None:
        self._plain_request = None

    @property
    def plain_request(self) -> str:
        """ Example: GET /hello/?name=username HTTP/1.1 """
        return self._plain_request

    @plain_request.setter
    def plain_request(
        self,
        plain_request: str
    ) -> None:
        self._parse_request(plain_request)
        self._plain_request = plain_request

    def _parse_request(
        self,
        request: str
    ) -> None:
        request_list = request.splitlines()

        request_line = request_list[0]
        host_header = next(filter(lambda x: 'Host:' in x, request_list), '::')
        content_length_header = next(
            filter(lambda x: 'Content-Length:' in x, request_list),
            ':'
        )

        self.method, self.uri, self.version = request_line.split()
        self.host, self.port = host_header.split(':')[1:]
        self.content_length = content_length_header.split(':')[1]
        self.query_string = self.uri.split('?')[1] if '?' in self.uri else ''
        self.body = request_list[-1]

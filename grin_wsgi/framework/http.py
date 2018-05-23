import typing
import collections


StringIO = typing.TypeVar('StringIO')
HTTP_METHODS = {'GET', 'POST', 'PUT', 'UPDATE'}


class QueryDict(collections.UserDict):
    """ A specialized UserDict which represents a query string.

    A QueryDict can be used to represent GET or POST data.

    QueryDict always contains list values.
    But it will return you a string instead if
    there are anly one value in a list.

    """

    def get(
        self,
        key: typing.Any,
        default: typing.Optional[typing.Any]=None
    ) -> typing.Any:
        try:
            value = self[key]
            if isinstance(value, list) and len(value) == 1:
                return value[0]
            return value
        except KeyError:
            return default


class HttpRequest:
    """ A basic HTTP Request.

    QueryDict is generating from a WSGI environ dictionary
    """

    def __init__(
        self,
        environ: typing.Dict[str, typing.Any]
    ) -> None:
        for k, v in environ.items():
            if 'wsgi.' not in k:  # exclude wsgi env variables
                setattr(self, k.lower(), v)

        self.data = self._get_request_data(environ['wsgi.input'])

    def _get_request_data(
        self,
        wsgi_input: StringIO
    ) -> QueryDict:
        try:
            request_body_size = int(self.content_length)
        except (AttributeError, ValueError):
            request_body_size = 0

        request_body = self.query_string if self.method == 'GET' else \
            wsgi_input.read(request_body_size)

        return self._parse_request_query_string(str(request_body))

    def _parse_request_query_string(
        self,
        query_string: str
    ) -> QueryDict:
        request_dict = QueryDict()
        for k, v in self._request_query_string_as_list_of_tuples(query_string):
            if k in request_dict:
                request_dict[k].extend(v)
            else:
                request_dict[k] = v

        return request_dict

    # TODO: realize unquote() -> '%20' = ' '
    def _request_query_string_as_list_of_tuples(
        self,
        query_string: str
    ) -> typing.List[typing.Tuple[str, typing.List[str]]]:
        key_value_pairs = []

        request_string_key_value_pairs = query_string.split('&')
        for key_value_pair in request_string_key_value_pairs:
            try:
                key, value_set = key_value_pair.split('=')
                key_value_pairs.append((key,
                                        value_set.replace('+', ' ').split(';')
                                        ))
            except ValueError:
                # key_value_pair does not exist (index url)
                pass

        return key_value_pairs


class HttpResponse:
    """ A basic HTTP Request. """

    def __init__(
        self,
        content: typing.Optional[str]='',
        content_type: typing.Optional[str]='text/plain',
        status: typing.Optional[int]=200,
        reason: typing.Optional[str]='OK',
        charset: typing.Optional[str]='utf-8'
    ) -> None:
        self.status = '{} {}'.format(status, reason)
        self.headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(content)))
        ]
        self.body = content.encode(charset)


class HttpResponseRedirect(HttpResponse):
    """ 301 Response """

    def __init__(
        self,
        redirect_url: str,
        content: typing.Optional[str]='Moved Permanently',
        content_type: typing.Optional[str]='text/plain',
        status: typing.Optional[int]=301,
        reason: typing.Optional[str]='MOVED PERMANENTLY',
        charset: typing.Optional[str]='utf-8'
    ) -> None:
        super().__init__(content, content_type, status, reason, charset)

        self.headers.append(('Location', redirect_url))


class HttpResponseNotFound(HttpResponse):
    """ 404 Response """

    def __init__(
        self,
        content: typing.Optional[str]='Sorry, Not Found',
        content_type: typing.Optional[str]='text/plain',
        status: typing.Optional[int]=404,
        reason: typing.Optional[str]='NOT FOUND',
        charset: typing.Optional[str]='utf-8'
    ) -> None:
        super().__init__(content, content_type, status, reason, charset)


class HttpMethodNotAllowed(HttpResponse):
    """ 405 Response """

    def __init__(
        self,
        content: typing.Optional[str]='Sorry, Method not allowed',
        content_type: typing.Optional[str]='text/plain',
        status: typing.Optional[int]=405,
        reason: typing.Optional[str]='NOT ALLOWED',
        charset: typing.Optional[str]='utf-8'
    ) -> None:
        super().__init__(content, content_type, status, reason, charset)


class HttpResponseServerError(HttpResponse):
    """ 500 Response """

    def __init__(
        self,
        content: typing.Optional[str]='Ooops... Server Error',
        content_type: typing.Optional[str]='text/plain',
        status: typing.Optional[int]=500,
        reason: typing.Optional[str]='SERVER Error',
        charset: typing.Optional[str]='utf-8'
    ) -> None:
        super().__init__(content, content_type, status, reason, charset)

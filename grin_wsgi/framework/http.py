import collections


HTTP_METHODS = {'GET', 'POST', 'PUT', 'UPDATE'}


class QueryDict(collections.UserDict):
    """ A specialized UserDict which represents a query string.

    A QueryDict can be used to represent GET or POST data.

    QueryDict always contains list values.
    But it will return you a string instead if
    there are anly one value in a list.

    """

    def get(self, key, default=None):
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

    def __init__(self, environ):
        for k, v in environ.items():
            if 'wsgi.' not in k:  # exclude wsgi env variables
                setattr(self, k.lower(), v)

        self.data = self._get_request_data(environ['wsgi.input'])

    def _get_request_data(self, wsgi_input):
        try:
            request_body_size = int(self.content_length)
        except (AttributeError, ValueError):
            request_body_size = 0

        request_body = self.query_string if self.method == 'GET' else \
            wsgi_input.read(request_body_size)

        return self._parse_request_query_string(str(request_body))

    def _parse_request_query_string(self, query_string):
        request_dict = QueryDict()
        for k, v in self._request_query_string_as_list_of_tuples(query_string):
            if k in request_dict:
                request_dict[k].extend(v)
            else:
                request_dict[k] = v

        return request_dict

    # TODO: realize unquote() -> '%20' = ' '
    def _request_query_string_as_list_of_tuples(self, query_string):
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

    def __init__(self, content='', content_type='text/plain',
                 status=200, reason='OK', charset='utf-8'):
        self.status = '{} {}'.format(status, reason)
        self.headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(content)))
        ]
        self.body = content.encode(charset)


class HttpResponseRedirect(HttpResponse):
    """ 301 Response """

    def __init__(self, redirect_url,
                 content='Moved Permanently', content_type='text/plain',
                 status=301, reason='MOVED PERMANENTLY', charset='utf-8'):
        super().__init__(content, content_type, status, reason, charset)

        self.headers.append(('Location', redirect_url))


class HttpResponseNotFound(HttpResponse):
    """ 404 Response """

    def __init__(self, content='Sorry, Not Found', content_type='text/plain',
                 status=404, reason='NOT FOUND', charset='utf-8'):
        super().__init__(content, content_type, status, reason, charset)


class HttpMethodNotAllowed(HttpResponse):
    """ 405 Response """

    def __init__(self, content='Sorry, Method not allowed',
                 content_type='text/plain',
                 status=405, reason='NOT ALLOWED', charset='utf-8'):
        super().__init__(content, content_type, status, reason, charset)


class HttpResponseServerError(HttpResponse):
    """ 500 Response """

    def __init__(self, content='Ooops... Server Error',
                 content_type='text/plain',
                 status=500, reason='SERVER Error', charset='utf-8'):
        super().__init__(content, content_type, status, reason, charset)

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

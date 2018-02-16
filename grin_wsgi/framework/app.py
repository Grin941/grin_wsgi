import re

from grin_wsgi.framework.http import HttpRequest, \
    HttpResponseNotFound, HttpResponseServerError
from grin_wsgi.framework.urls import urls


def application(
        environ,  # dictionary containing CGI like environment
        start_response
):
    try:
        request = HttpRequest(environ)
        url = request.path_info.lstrip('/')
        for url_params, view in urls:
            match = re.search(url_params, url)
            if match is not None:
                response = view(request)
                break
        else: response = HttpResponseNotFound()
    except Exception:
        response = HttpResponseServerError()

    start_response(response.status, response.headers)
    return [response.body]

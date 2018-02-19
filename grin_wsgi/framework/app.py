import re

from sys import exc_info
from traceback import format_tb

from grin_wsgi.framework.http import HttpRequest, \
    HttpResponseNotFound, HttpResponseServerError, HttpResponseRedirect
from grin_wsgi.framework.urls import urls


def application(
        environ,  # dictionary containing CGI like environment
        start_response
):
    try:
        request = HttpRequest(environ)
        url = request.path_info.lstrip('/')
        for url_params, view in urls:
            # Redirect to the prime resource
            if '{}/'.format(url) in url_params:
                response = HttpResponseRedirect('{}/'.format(url))
                break

            # Find matching view
            match = re.search(url_params, url)
            if match is not None:
                response = view(request)
                break

        else: response = HttpResponseNotFound()
    except Exception:
        e_type, e_value, tb = exc_info()
        traceback = ['Traceback (most recent call last):']
        traceback += format_tb(tb)
        traceback.append('%s: %s' % (e_type.__name__, e_value))
        response = HttpResponseServerError('\n'.join(traceback))

    start_response(response.status, response.headers)
    return [response.body]

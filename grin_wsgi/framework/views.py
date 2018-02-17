import datetime

from grin_wsgi.framework.http import HttpResponse


def index(request):
    now = datetime.datetime.now()
    html = 'It is now {}.'.format(now)
    return HttpResponse(html)


def hello(request):
    name = request.data.get('name', 'Anonymus')
    html = 'Hello, {}!'.format(name)
    return HttpResponse(html)

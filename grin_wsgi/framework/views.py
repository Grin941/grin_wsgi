import datetime

from grin_wsgi.framework.http import HttpResponse


def index(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def hello(request):
    name = request.data.get('name', 'Anonymus')
    html = '<html><body>Hello, {}!</body></html>'.format(name)
    return HttpResponse(html)

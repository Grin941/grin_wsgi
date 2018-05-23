import datetime

from grin_wsgi.framework.http import HttpResponse
from grin_wsgi.framework.app import Project


project = Project()
app = project.register_app(__name__)


@app.route(r'^$')
def index(request):
    html = f'It is now {datetime.datetime.now()}.'
    return HttpResponse(html)


@app.route(r'hello/(.+)$')
@app.route(r'hello/<str:name>/page<int:page>$')
def hello(request, **kwargs):
    name = kwargs.get('name', request.data.get('name', 'Anonymus'))
    page = kwargs.get('page')
    html = f'Hello, {name}!'
    if page is not None:
        html += f' You are on the {page} page.'
    return HttpResponse(html)

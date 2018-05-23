Grin WSGI
=========
[![Build Status](https://travis-ci.org/Grin941/grin_wsgi.svg?branch=master)](https://travis-ci.org/Grin941/grin_wsgi)
[![Coverage by codecov.io](https://codecov.io/gh/Grin941/grin_wsgi/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/gh/Grin941/grin_wsgi?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/83c71f7d66f2ce7962d5/maintainability)](https://codeclimate.com/github/Grin941/grin_wsgi/maintainability)

My WSGI Interface implementation

## Requirements

* Python 3.6

## Installation

```
$ make
```

## Usage

To run built-in test framework app type:
```
$ gwsgi
```

To run your own application you have two options:

* Provide config.ini filepath
```
$ gwsgi --ini /config.ini
```
* Or provide directory and module variables
```
$ gwsgi --chdir /opt/project --module project_name.app
```

For more information type: ```$ gwsgi -h```

Test built-in framework by such requests:
* http://localhost:8051/
* http://localhost:8051/hello/?name=username
* http://localhost:8051/hello/alex/page1

## Config example
```
[gwsgi]
chdir = /opt/project
module = project_name.app
host = localhost
port = 8051
threading = false
processing = false
wsgiref = false
```

## A Minimal Application
```
from grin_wsgi.framework.http import HttpResponse
from grin_wsgi.framework.app import Project


project = Project()
app = project.register_app(__name__)


@app.route(r'hello/(.+)$')
@app.route(r'hello/<str:name>/page<int:page>$')
def hello(request, **kwargs):
    name = kwargs.get('name', request.data.get('name', 'Anonymus'))
    page = kwargs.get('page')
    html = f'Hello, {name}!'
    if page is not None:
        html += f' You are on the {page} page.'
    return HttpResponse(html)
```

## Testing
```
$ PYTHONPATH=. pytest
```

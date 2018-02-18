Grin WSGI
=========
[![Build Status](https://travis-ci.org/Grin941/grin_wsgi.svg?branch=master)](https://travis-ci.org/Grin941/grin_wsgi)
[![Coverage by codecov.io](https://codecov.io/gh/Grin941/grin_wsgi/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/gh/Grin941/grin_wsgi?branch=master)

My WSGI Interface implementation

## Requirements

* Python 3.5 or 3.6

## Installation

```
$ make
```

## Usage

To run built-in framework app type:
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

## Testing
```
$ PYTHONPATH=. pytest
```

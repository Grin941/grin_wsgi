from grin_wsgi.wsgi import WSGIServer
from grin_wsgi.framework.app import application


def make_server(host, port, application,
                threads=False, multiprocs=False):
    return WSGIServer(host, port, application)


def run(host='localhost', port=8051, application=application,
        threads=False, multiprocs=False):
    httpd = make_server(host, port, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=port))
    httpd.serve_forever()

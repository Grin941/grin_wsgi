import argparse

from grin_wsgi.wsgi.wsgi import make_server
from grin_wsgi.framework.app import application
from grin_wsgi import const


def run(host='localhost', port=8051, application=application,
        threads=False, multiprocs=False):
    parser = argparse.ArgumentParser(
        description='Grin WSGI Interface implementation.')
    parser.add_argument('--ini', default=const.INI,
                        help='GWSGI configuration file path.')

    parser.add_argument('--chdir', default=const.CHDIR,
                        help='Your project dir.')
    parser.add_argument('--module', default=const.MODULE,
                        help='wsgi App file')

    parser.add_argument('--host', default=const.HOST, help='Server host.')
    parser.add_argument('--port', type=int, default=const.PORT,
                        help='Server port.')
    parser.add_argument('--threading', action='store_true',
                        help='Do you want to run server in many threads?')
    parser.add_argument('--processing', action='store_true',
                        help='Do you want to run server in many processes?')
    parser.add_argument('--wsgiref', action='store_true',
                        help='Do you want to run wsgiref WSGIServer?')

    parser.add_argument('--test_framework', action='store_true',
                        help='Run built-in framework application for test')
    args = parser.parse_args()

    print('Args', args)

    httpd = make_server(host, port, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=port))
    httpd.serve_forever()

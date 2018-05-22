import argparse
import logging

from grin_wsgi import const
from grin_wsgi.wsgi.config import WSGIConfig
from grin_wsgi.wsgi import make_server


parser = argparse.ArgumentParser(
    description='Grin WSGI Interface implementation.')
parser.add_argument('--ini', default=const.INI,
                    help='GWSGI configuration file path.')

parser.add_argument('--chdir', default=const.CHDIR,
                    help='Your project dir.')
parser.add_argument('--module', default=const.TEST_FRAMEWORK_MODULE,
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


def run():  # pragma: no cover
    """ The ``gwsgi`` command line runner for launching GWSGI """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')
    args = parser.parse_args()
    config = WSGIConfig()
    config.configure_gwsgi(args)
    httpd = make_server(config.host, config.port, config.application,
                        config.threading, config.processing, config.wsgiref)
    logging.debug('WSGIServer: Serving HTTP on port {port} ...\n'.format(
        port=config.port))
    httpd.serve_forever()

import argparse
import logging

from grin_wsgi import const
from grin_wsgi.wsgi import \
    config as wsgi_config, \
    make_server as make_wsgi_server


def parse_user_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Grin WSGI Interface implementation.'
    )
    parser.add_argument(
        '--ini', default=const.INI,
        help='GWSGI configuration file path.'
    )

    parser.add_argument(
        '--chdir', default=const.CHDIR,
        help='Your project dir.'
    )
    parser.add_argument(
        '--module', default=const.TEST_FRAMEWORK_MODULE,
        help='wsgi App file'
    )

    parser.add_argument('--host', default=const.HOST, help='Server host.')
    parser.add_argument(
        '--port', type=int, default=const.PORT,
        help='Server port.'
    )
    parser.add_argument(
        '--threading', action='store_true',
        help='Do you want to run server in many threads?'
    )
    parser.add_argument(
        '--processing', action='store_true',
        help='Do you want to run server in many processes?'
    )
    parser.add_argument(
        '--wsgiref', action='store_true',
        help='Do you want to run wsgiref WSGIServer?'
    )
    return parser.parse_args()


def run() -> None:  # pragma: no cover
    """ The ``gwsgi`` command line runner for launching GWSGI """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    args = parse_user_args()
    config = wsgi_config.WSGIConfig()
    config.configure_gwsgi(args)
    httpd = make_wsgi_server(
        config.host, config.port, config.application,
        config.threading, config.processing, config.wsgiref
    )
    logging.debug(f'WSGIServer: Serving HTTP on port {config.port} ...\n')
    httpd.serve_forever()

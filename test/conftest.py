import pytest
import argparse
import typing

from grin_wsgi import const
from grin_wsgi.wsgi.config import WSGIConfig


@pytest.fixture(scope="module")
def parse_args() -> typing.Callable:
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
    def _parse_args(args):
        return parser.parse_args(args)

    return _parse_args


@pytest.fixture(scope="module")
def config() -> WSGIConfig:
    return WSGIConfig()

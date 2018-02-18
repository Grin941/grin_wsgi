import pytest

from grin_wsgi.main import parser
from grin_wsgi.wsgi.config import WSGIConfig
from grin_wsgi.wsgi import exceptions as gwsgi_exceptions


class TestWSGIConfig:
    def setup(self):
        def _parse_args(args):
            return parser.parse_args(args)

        self.parse_args = _parse_args
        self.config = WSGIConfig()

    def test_parse_ini_if_file_does_not_exist(self):
        args = self.parse_args(['--ini', 'does_not_exist'])
        ini = args.ini

        with pytest.raises(gwsgi_exceptions.ConfigFileDoesNotExist):
            self.config._parse_ini(ini)

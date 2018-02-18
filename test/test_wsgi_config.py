import pytest
import os

from grin_wsgi.main import parser
from grin_wsgi.wsgi.config import WSGIConfig
from grin_wsgi.wsgi import exceptions as gwsgi_exceptions
from grin_wsgi import const as gwsgi_const


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

    def test_parse_ini_with_wrong_section(self, tmpdir):
        ini = tmpdir.join('conf.ini')
        ini.write('[uwsgi]')

        with pytest.raises(gwsgi_exceptions.WrongConfigSectionName):
            self.config._parse_ini(ini.strpath)

    def test_parse_ini_returns_const_value_if_one_was_not_passed_in_config(self, tmpdir):
        port = 8080

        ini = tmpdir.join('conf.ini')
        ini.write(
"""
[gwsgi]
port={port}
""".format(port=port))

        gwsgi_conf = self.config._parse_ini(ini.strpath)
        assert gwsgi_conf[2] == gwsgi_const.HOST
        assert gwsgi_conf[3] == port

    def test_get_application_returns_builtin_framework_application_by_default(self):
        from grin_wsgi.framework.app import application
        assert self.config._get_application('', '') == application

    def test_wsgiref_arg_defines_whether_to_use_builtin_wsgi_server_or_wsgiref(self):
        # wsgiref was passed and stored as True
        args = self.parse_args(['--wsgiref'])
        wsgiref = args.wsgiref
        from wsgiref.simple_server import make_server       
        assert self.config._get_server_handler(wsgiref) == make_server

        # suppose wsgiref was not passed and stored as False
        wsgiref = False
        from grin_wsgi.wsgi.wsgi import make_server
        assert self.config._get_server_handler(wsgiref) == make_server

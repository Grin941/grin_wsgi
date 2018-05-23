import pytest
import os

from grin_wsgi.wsgi import exceptions as gwsgi_exceptions
from grin_wsgi import const as gwsgi_const


def test_parse_ini_if_file_does_not_exist(parse_args, config):
    args = parse_args(['--ini', 'does_not_exist'])
    ini = args.ini

    with pytest.raises(gwsgi_exceptions.ConfigFileDoesNotExist):
        config._parse_ini(ini)

def test_parse_ini_with_wrong_section(tmpdir, config):
    ini = tmpdir.join('conf.ini')
    ini.write('[uwsgi]')

    with pytest.raises(gwsgi_exceptions.WrongConfigSectionName):
        config._parse_ini(ini.strpath)

def test_parse_ini_returns_const_value_if_one_was_not_passed_in_config(tmpdir, config):
    port = 8080

    ini = tmpdir.join('conf.ini')
    ini.write(
"""
[gwsgi]
port={port}
""".format(port=port))

    gwsgi_conf = config._parse_ini(ini.strpath)
    assert gwsgi_conf[2] == gwsgi_const.HOST
    assert gwsgi_conf[3] == port

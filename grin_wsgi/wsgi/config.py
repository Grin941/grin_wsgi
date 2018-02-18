from configparser import ConfigParser
from importlib import import_module

from grin_wsgi import const
from grin_wsgi.wsgi import exceptions as gwsgi_exceptions


class WSGIConfig:

    def configure_gwsgi(self, conf_args):  # pragma: no cover
        ini = conf_args.ini
        if ini:
            (chdir, module,
             host, port,
             threading, processing,
             wsgiref) = self._parse_ini(ini)
        else:
            chdir = conf_args.chdir
            module = conf_args.module
            host = conf_args.host
            port = conf_args.port
            threading = conf_args.threading
            processing = conf_args.processing
            wsgiref = conf_args.wsgiref

        self.application = self._get_application(
            chdir, module)
        self.host = host
        self.port = port
        self.threading = threading
        self.processing = processing
        self.make_server = self._get_server_handler(wsgiref)

    def _parse_ini(self, ini_file_path):
        config = ConfigParser()
        dataset = config.read(ini_file_path)
        if not len(dataset):
            raise gwsgi_exceptions.ConfigFileDoesNotExist(
                'Wrong ini config file path: {0}'.format(ini_file_path))
        # gwsgi is the only section in a file
        try:
            gwsgi_conf = config['gwsgi']
        except KeyError:
            raise gwsgi_exceptions.WrongConfigSectionName(
                'Please set [gwsgi] section in an ini file')

        return (
            gwsgi_conf.get('chdir') or const.CHDIR,
            gwsgi_conf.get('module') or const.TEST_FRAMEWORK_MODULE,
            gwsgi_conf.get('host') or const.HOST,
            gwsgi_conf.getint('port') or const.PORT,
            gwsgi_conf.getboolean('threading') or const.THREADING,
            gwsgi_conf.getboolean('processing') or const.PROCESSING,
            gwsgi_conf.getboolean('wsgiref') or const.WSGIREF,
        )

    def _get_application(self, chdir, module):
        if not all((chdir, module)):
            chdir = const.CHDIR
            module = const.TEST_FRAMEWORK_MODULE
        module = import_module(module, chdir)
        return getattr(module, 'application')

    def _get_server_handler(self, wsgiref):
        if wsgiref:
            from wsgiref.simple_server import make_server
        else:
            from grin_wsgi.wsgi.wsgi import make_server

        return make_server

from configparser import ConfigParser
from importlib import import_module

from grin_wsgi import const


class WSGIConfig:

    def __init__(self, conf_args):
        self._configure_uwsgi(conf_args)

    def _configure_uwsgi(self, conf_args):
        ini = conf_args.ini
        if ini:
            (chdir, module,
             host, port,
             threading, processing,
             wsgiref, test_framework) = self._parse_ini(ini)
        else:
            chdir = conf_args.chdir
            module = conf_args.module
            host = conf_args.host
            port = conf_args.port
            threading = conf_args.threading
            processing = conf_args.processing
            wsgiref = conf_args.wsgiref
            test_framework = conf_args.test_framework

        self.application = self._get_application(
            chdir, module, test_framework)
        self.host = host
        self.port = port
        self.threading = threading
        self.processing = processing
        self.make_server = self._get_server_handler(wsgiref)

    def _parse_ini(ini_file_path):
        config = ConfigParser()
        config.read(ini_file_path)
        # gwsgi is the only section in a file
        try:
            gwsgi_conf = config['gwsgi']
        except KeyError:
            raise Exception('Please set [gwsgi] section in an ini file')

        return (
            gwsgi_conf.get('chdir') or const.CHDIR,
            gwsgi_conf.get('module') or const.TEST_FRAMEWORK_MODULE,
            gwsgi_conf.get('host') or const.HOST,
            gwsgi_conf.getint('port') or const.PORT,
            gwsgi_conf.getboolean('threading') or const.THREADING,
            gwsgi_conf.getboolean('processing') or const.PROCESSING,
            gwsgi_conf.getboolean('wsgiref') or const.WSGIREF,
            gwsgi_conf.getboolean('test_framework') or const.TEST_FRAMEWORK
        )

    def _get_application(self, chdir, module, test_framework):
        if test_framework:
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

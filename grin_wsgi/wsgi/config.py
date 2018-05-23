import typing

from configparser import ConfigParser
from importlib import import_module

from grin_wsgi import const
from grin_wsgi.wsgi import exceptions as gwsgi_exceptions


Namespace = typing.TypeVar('Namespace')


class WSGIConfig:
    """
    Configuration system for GWSGI.

    WSGI configuration
    ------------------

    ini
        fullpath to a configure file with .ini extension.
        If ini parameter is passsed you should not pass
        any other configure parameters, but set them in
        an .ini file

    chdir
        fullpath to a directory containing module with an
        application() callable

    module
        python module containing application() callable

    host
        host to run WSGI server upon

    port
        port to run WSGI server upon

    threading
        if argument is passed, WSGI server would accept
        data in a number of threads

    processing
        if argument is passed, WSGI server would accept
        data in a number of processes

    wsgiref
        if argument is passed, wsgiref WSGI server would
        be running instead og GWSGI server

    ini config file example
    -----------------------
    .. note:: always use [gwsgi] section
        [gwsgi]
        chdir = /opt/project
        module = project_name.app
        host = localhost
        port = 8051
        threading = false
        processing = false
        wsgiref = false
    """

    def configure_gwsgi(
        self,
        conf_args: Namespace
    ) -> None:  # pragma: no cover
        ini = conf_args.ini
        if ini:
            (
                chdir, module,
                host, port,
                threading, processing,
                wsgiref
            ) = self._parse_ini(ini)
        else:
            chdir = conf_args.chdir
            module = conf_args.module
            host = conf_args.host
            port = conf_args.port
            threading = conf_args.threading
            processing = conf_args.processing
            wsgiref = conf_args.wsgiref

        self.application = self._get_application(
            chdir, module
        )
        self.host = host
        self.port = port
        self.threading = threading
        self.processing = processing
        self.wsgiref = wsgiref

    def _parse_ini(
        self,
        ini_file_path: str
    ) -> typing.Tuple[typing.Any]:
        config = ConfigParser()
        dataset = config.read(ini_file_path)
        if not len(dataset):
            raise gwsgi_exceptions.ConfigFileDoesNotExist(
                'Wrong ini config file path: {0}'.format(ini_file_path)
            )
        # gwsgi is the only section in a file
        try:
            gwsgi_conf = config['gwsgi']
        except KeyError:
            raise gwsgi_exceptions.WrongConfigSectionName(
                'Please set [gwsgi] section in an ini file'
            )

        return (
            gwsgi_conf.get('chdir') or const.CHDIR,
            gwsgi_conf.get('module') or const.TEST_FRAMEWORK_MODULE,
            gwsgi_conf.get('host') or const.HOST,
            gwsgi_conf.getint('port') or const.PORT,
            gwsgi_conf.getboolean('threading') or const.THREADING,
            gwsgi_conf.getboolean('processing') or const.PROCESSING,
            gwsgi_conf.getboolean('wsgiref') or const.WSGIREF,
        )

    def _get_application(
        self,
        chdir: str,
        module: str
    ) -> typing.Callable:
        if not all((chdir, module)):
            chdir = const.CHDIR
            module = const.TEST_FRAMEWORK_MODULE
        module = import_module(module, chdir)
        return getattr(module, 'project')

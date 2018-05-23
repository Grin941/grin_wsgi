import typing

from sys import exc_info
from traceback import format_tb

from .http import HttpRequest, \
    HttpResponseServerError, HttpMethodNotAllowed, \
    HttpResponseRedirect, HttpResponseNotFound, \
    HTTP_METHODS
from .urls import UrlRouter


class App:

    def __init__(
        self,
        name: typing.Optional[str]='GrinApp',
        url_prefix: typing.Optional[str]=''
    ) -> None:
        self._name = name
        self._url_router = UrlRouter(url_prefix)

    @property
    def name(self) -> str:
        return self._name

    @property
    def url_router(self) -> UrlRouter:
        return self._url_router

    def route(
        self,
        url_pattern: str,
        required_methods: typing.Optional=None
    ) -> typing.Callable:
        if required_methods is None:
            required_methods = HTTP_METHODS

        def view_decorator(view):
            self._url_router.append(url_pattern, view)

            def view_wrapper(request, *args, **kwargs):
                if request.method not in required_methods:
                    return HttpMethodNotAllowed(
                        f'Sorry, method {request.method} is not allowed'
                    )
                return view(request, *args, **kwargs)
            return view_wrapper
        return view_decorator


class Project:

    def __init__(self) -> None:
        self._dispatcher = {}

    def __contains__(
        self,
        app: App
    ) -> bool:
        return app.name in self._dispatcher

    def register_app(self, *args, **kwargs) -> App:
        app = App(*args, **kwargs)
        if app not in self:
            self._dispatcher[app.name] = app.url_router
            return app
        app_name = app.name
        del app
        raise Exception(f'App {app_name} has already been registered')

    def dispatch(
        self,
        url: str,
        request: HttpRequest
    ) -> typing.Any:
        try:
            url_prefix = url.split('/')[0]
        except IndexError:
            url_prefix = ''

        routers = [
            router for router in self._dispatcher.values() if
            router.url_prefix == url_prefix
        ]
        if len(routers) != 1:
            routers = (
                router for router in self._dispatcher.values() if
                router.url_prefix == ''
            )

        for router in routers:
            view, redirect = router.dispatch(url)
            if redirect:
                # Redirect to the prime resource
                return HttpResponseRedirect(f'{url}/')
            if view is not None:
                return view(request)
        return HttpResponseNotFound()

    def __call__(
        self,
        environ: typing.Dict[str, typing.Any],  # CGI like environment
        start_response: typing.Callable
    ) -> typing.List[str]:
        try:
            request = HttpRequest(environ)
            url = request.path_info.lstrip('/')
            response = self.dispatch(url, request)
        except Exception:
            e_type, e_value, tb = exc_info()
            traceback = ['Traceback (most recent call last):']
            traceback += format_tb(tb)
            traceback.append(f'{e_type.__name__}: {e_value}')
            response = HttpResponseServerError('\n'.join(traceback))

        start_response(response.status, response.headers)
        return [response.body]

import re

from .views import index, hello
from .http import HttpResponseNotFound, HttpResponseRedirect


class UrlRouter:
    def __init__(self, url_prefix=''):
        self._urls = [
            (r'^$', index),
            (r'hello/(.+)$', hello),
            (r'hello/<str:name>/page<int:page>$', hello),
        ]
        self._url_patterns = set()
        self._url_prefix = url_prefix

    @property
    def url_prefix(self):
        return self._url_prefix

    def __add__(self, other):
        pass

    def __contains__(self, url_pattern):
        return f'{self.url_prefix}/{url_pattern}' in self._url_patterns

    def append(self, url_pattern, view):
        if url_pattern not in self:
            self._urls.append(
                (f'{self.url_prefix}/{url_pattern}', view)
            )
            self._url_patterns.add(f'{self.url_prefix}/{url_pattern}')

    @staticmethod
    def _convert_url_pattern_to_regexp(url_pattern):
        """
        Example: <str:name> -> (?P<name>\w+)
        """
        type_mapping = {
            'str': '\w+',
            'int': '\d+'
        }

        pat_type, pat_name = url_pattern.groups()
        pat_type = type_mapping.get(pat_type, '\w+')

        return f'(?P<{pat_name}>{pat_type})'

    def dispatch(self, url, request):
        redirect_url = url.rstrip('/')
        url_converter_pattern = r'<(\w+):(\w+)>'  # <str:name>, for ex.
        for url_pattern, view in self._urls:
            redirect_url_pattern = url_pattern.rstrip('/')
            regex_url_pattern = re.sub(
                url_converter_pattern,
                self._convert_url_pattern_to_regexp,
                redirect_url_pattern
            )

            regexp_parsed_url = re.search(regex_url_pattern, redirect_url)
            if regexp_parsed_url is None:
                # url_pattern didn't match, try the new one
                continue

            view_kwargs = regexp_parsed_url.groupdict()
            if url == redirect_url and url_pattern != redirect_url_pattern:
                # Redirect to the prime resource
                return HttpResponseRedirect(f'{url}/')

            return view(request, **view_kwargs)
        else: return HttpResponseNotFound()

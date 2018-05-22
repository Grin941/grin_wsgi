import re
import functools


class UrlRouter:
    def __init__(self, url_prefix=''):
        self._urls = []
        self._url_patterns = set()
        self._url_prefix = url_prefix

    @property
    def url_prefix(self):
        return self._url_prefix

    def __contains__(self, url_pattern):
        return f'{self.url_prefix}{url_pattern}' in self._url_patterns

    def append(self, url_pattern, view):
        if url_pattern not in self:
            self._urls.append(
                (f'{self.url_prefix}{url_pattern}', view)
            )
            self._url_patterns.add(f'{self.url_prefix}{url_pattern}')

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

    def dispatch(self, url):
        dispatched_view, redirect = None, False
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

            if url == redirect_url and url_pattern != redirect_url_pattern:
                redirect = True
                break

            view_kwargs = regexp_parsed_url.groupdict()
            print('view_kwargs', view_kwargs)
            dispatched_view = functools.partial(view, **view_kwargs)
        return dispatched_view, redirect

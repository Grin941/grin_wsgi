from grin_wsgi.framework.views import index, hello


urls = [
    (r'^$', index),
    (r'hello/?$', hello),
    (r'hello/(.+)$', hello)
]

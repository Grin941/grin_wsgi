import os
from setuptools import setup, find_packages

from grin_wsgi import __version__

# read long description
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()


setup(
    name='grin_wsgi',
    version=__version__,
    description='My WSGI Interface implementation',
    long_description=long_description,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points="""
    [console_scripts]
    grin_wsgi=grin_wsgi.main:run
    """
)

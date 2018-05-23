import os
from setuptools import setup, find_packages

from grin_wsgi import __version__

# read long description
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()


setup(
    name='Grin WSGI framework',
    version=__version__,
    description='My WSGI Interface implementation',
    url='https://github.com/Grin941/grin_wsgi',
    licence='MIT',
    author='Grinenko Alexander',
    author_email='labamifi@gmail.com',
    long_description=long_description,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    extra_require={
        'dev': [
            'pytest',
            'coverage'
        ]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': ['gwsgi=grin_wsgi.cli:run']
    }
)

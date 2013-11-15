from __future__ import print_function
from setuptools import setup
import io
import os

import bugzfeed

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name='bugzfeed',
    version=bugzfeed.__version__,
    url='http://github.com/mozilla/bugzfeed/',
    license='Mozilla Public License 2.0',
    author='Mark Cote',
    install_requires=[
        'mozillapulse',
        'mozlog',
        'tornado',
    ],
    author_email='mcote@mozilla.com',
    description='notification system for Bugzilla',
    long_description=long_description,
    packages=['bugzfeed'],
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'bugzfeed-server = bugzfeed.server:cli'
        ]
    }
)

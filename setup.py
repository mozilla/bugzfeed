from __future__ import print_function

import io
import os
import re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

def find_version(*file_paths):
    version_file = open(os.path.join(os.path.dirname(__file__),
                                     *file_paths)).read()
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README.md')

setup(
    name='bugzfeed',
    version=find_version('bugzfeed', '__init__.py'),
    url='http://github.com/mozilla/bugzfeed/',
    license='Mozilla Public License 2.0',
    author='Mark Cote',
    install_requires=[
        'mozillapulse>=0.80',
        'tornado',
    ],
    author_email='mcote@mozilla.com',
    description='notification system for Bugzilla via WebSockets',
    long_description=long_description,
    packages=['bugzfeed'],
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    entry_points={
        'console_scripts': [
            'bugzfeed-server = bugzfeed.server:cli'
        ]
    }
)

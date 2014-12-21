#!/usr/bin/env python
import io
import os
import re
from setuptools import setup


def _file_open(file_name):
    return io.open(os.path.join(os.path.dirname(__file__), file_name),
                   encoding='utf-8')


def _file_read(file_name):
    with _file_open(file_name) as f_stream:
        return f_stream.read()


def _file_read_lines(file_name):
    with _file_open(file_name) as f_stream:
        return [l.strip() for l in f_stream.readlines()]


def _read_version():
    return re.search("__version__\s*=\s*'([^']+)'\s*",
                     _file_read('chronometer.py')).group(1)


def _read_requirements():
    lines = _file_read_lines('requirements/install.txt')
    return [r for r in (l.split('#', 1)[0].strip() for l in lines) if r]


setup(name='chronometer',
      version=_read_version(),
      description=('Yet another simple time measurement tool for Python'
                   ' with less cruft and more features.'),
      author='Arthur Skowronek',
      author_email='eisensheng@mailbox.org',
      url='https://github.com/eisensheng/chronometer',
      license='MIT License',
      include_package_data=False,
      zip_safe=True,
      install_requires=_read_requirements(),
      long_description=_file_read('README.rst'),
      py_modules=['chronometer', ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System',
          'Topic :: System :: Benchmark',
          'Topic :: Utilities',
      ])

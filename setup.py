#!python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import os, sys
from setuptools import setup, find_packages
from setuptools.command.develop import develop as _develop


# Import the version from the release module
project_name = 'xopgi.backports'
parts = project_name.split('.')
parts[-1] = '_'.join(parts)  # Addons should be ns_named!!!
_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_current_dir, *parts))
from _release import VERSION as version


dev_classifier = 'Development Status :: 4 - Beta'


def safe_read(*paths):
    try:
        with open(os.path.join(_current_dir, *paths), 'rU') as fh:
            return fh.read()
    except (IOError, OSError):
        return ''


class develop(_develop):
    pass

setup(name=project_name,
      version=version,
      description="Merchise's backports from Odoo",
      long_description=safe_read('README.rst'),
      cmdclass={'develop': develop},
      classifiers=[
          # Get from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          dev_classifier,
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      keywords='',
      author='Merchise Autrement and Contributors',
      license='GPLv3+',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'xoeuf',
          'xoutil',
          'openerp',
      ],
      entry_points="""
      [xoeuf.addons]
      xopgi_backports = xopgi.xopgi_backports

      [xoeuf.addons:rules]
      xopgi_backports: openerp < 8.0.
      """,
      )
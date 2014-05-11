#!/usr/bin/env python
# This file is part of Tryton and Nereid.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import re
import os
import ConfigParser
from setuptools import setup


def get_files(root):
    for dirname, dirnames, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirname, filename)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = [
    'trytond_nereid>=3.0.7.0, <3.1',
]
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append(
            'trytond_%s >= %s.%s, < %s.%s' % (
                dep, major_version, minor_version,
                major_version, minor_version + 1
            )
        )
requires.append(
    'trytond >= %s.%s, < %s.%s' %
    (major_version, minor_version, major_version, minor_version + 1)
)

setup(
    name='openlabs_nereid_webshop',
    version=info.get('version'),
    description="Nereid Webshop",
    author="Openlabs Technologies & consulting (P) Limited",
    author_email='info@openlabs.co.in',
    url='http://www.openlabs.co.in',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Tryton',
        'Topic :: Office/Business',
    ],
    packages=[
        'trytond.modules.nereid_webshop',
        'trytond.modules.nereid_webshop.tests',
    ],
    package_dir={
        'trytond.modules.nereid_webshop': '.',
        'trytond.modules.nereid_webshop.tests': 'tests',
    },
    package_data={
        'trytond.modules.nereid_webshop': info.get('xml', [])
        + ['tryton.cfg', 'locale/*.po', 'tests/*.rst']
        + ['i18n/*.pot', 'i18n/pt_BR/LC_MESSAGES/*']
        + list(get_files("templates/"))
        + list(get_files("static/")),
    },
    license='GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    nereid_webshop = trytond.modules.nereid_webshop
    """,
    test_suite='tests.suite',
    test_loader='trytond.test_loader:Loader',
)

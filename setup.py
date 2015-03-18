#!/usr/bin/env python
# This file is part of Tryton and Nereid.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import ConfigParser
import os
import re
import sys
import time
import unittest
from setuptools import setup, Command


def get_files(root):
    for dirname, dirnames, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirname, filename)


def get_required_version(name):
    return '%s >= %s.%s, < %s.%s' % (
        name, major_version, minor_version,
        major_version, minor_version + 1
    )


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class SQLiteTest(Command):
    """
    Run the tests on SQLite
    """
    description = "Run tests on SQLite"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)

        os.environ['TRYTOND_DATABASE_URI'] = 'sqlite://'
        os.environ['DB_NAME'] = ':memory:'

        from tests import suite
        test_result = unittest.TextTestRunner(verbosity=3).run(suite())

        if test_result.wasSuccessful():
            sys.exit(0)
        sys.exit(-1)


class PostgresTest(Command):
    """
    Run the tests on Postgres.
    """
    description = "Run tests on Postgresql"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)

        os.environ['TRYTOND_DATABASE_URI'] = 'postgresql://'
        os.environ['DB_NAME'] = 'test_' + str(int(time.time()))

        from tests import suite
        test_result = unittest.TextTestRunner(verbosity=3).run(suite())

        if test_result.wasSuccessful():
            sys.exit(0)
        sys.exit(-1)


MODULE2PREFIX = {
    'nereid_wishlist': 'openlabs',
    'gift_card': 'openlabs',
    'product_variant_name': 'openlabs',
}

MODULE = "nereid_webshop"
PREFIX = "openlabs"

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
    'pygeoip',
]
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append(
            '%s_%s >= %s.%s, < %s.%s' % (
                MODULE2PREFIX.get(dep, 'trytond'), dep,
                major_version, minor_version, major_version,
                minor_version + 1
            )
        )
requires.append(
    'trytond >= %s.%s, < %s.%s' %
    (major_version, minor_version, major_version, minor_version + 1)
)

setup(
    name='%s_%s' % (PREFIX, MODULE),
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
        'trytond.modules.%s' % MODULE,
        'trytond.modules.%s.tests' % MODULE,
    ],
    package_dir={
        'trytond.modules.%s' % MODULE: '.',
        'trytond.modules.%s.tests' % MODULE: 'tests',
    },
    package_data={
        'trytond.modules.nereid_webshop': info.get('xml', []) +
        ['tryton.cfg', 'locale/*.po', 'tests/*.rst'] +
        ['i18n/*.pot', 'i18n/pt_BR/LC_MESSAGES/*', 'view/*.xml'] +
        list(get_files("templates/")) +
        list(get_files("static/")),
    },
    license='GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    %s = trytond.modules.%s
    """ % (MODULE, MODULE),
    test_suite='tests.suite',
    test_loader='trytond.test_loader:Loader',
    tests_require=[
        'pycountry',
        get_required_version('openlabs_payment_gateway_authorize_net'),
        'cssutils',
    ],
    cmdclass={
        'test': SQLiteTest,
        'test_postgres': PostgresTest,
    },
)

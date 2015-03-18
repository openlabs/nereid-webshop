# -*- coding: utf-8 -*-
"""
    test_views_depends

    Test tryton views and fields dependency.

    :copyright: (C) 2013-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends

DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))


class TestViewsDepends(unittest.TestCase):
    '''
    Test views and depends
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('nereid_webshop')

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('nereid_webshop')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestViewsDepends)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

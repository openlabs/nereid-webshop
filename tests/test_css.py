# -*- coding: utf-8 -*-
"""
    CSS Testing

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from os.path import join
from cssutils import CSSParser

import unittest
import trytond.tests.test_tryton

dir = 'static/css/'


class CSSTest(unittest.TestCase):
    """
    Test case for CSS.
    """

    def validate(self, filename):
        """
        Uses cssutils to validate a css file.
        Prints output using a logger.
        """
        CSSParser(raiseExceptions=True).parseFile(filename, validate=True)

    def test_css(self):
        """
        Test for CSS validation using W3C standards.
        """
        cssfile = join(dir, 'style.css')
        self.validate(cssfile)


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(CSSTest)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

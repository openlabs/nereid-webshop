# -*- coding: utf-8 -*-
"""
    __init__

    Test Suite

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest

import trytond.tests.test_tryton

from .test_views_depends import TestViewsDepends
from .test_invoice import TestDownloadInvoice
from .test_css import CSSTest
from .test_templates import TestTemplates
from .test_gift_card import TestGiftCard
from .test_website import TestWebsite


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(CSSTest),
        unittest.TestLoader().loadTestsFromTestCase(TestViewsDepends),
        unittest.TestLoader().loadTestsFromTestCase(TestDownloadInvoice),
        unittest.TestLoader().loadTestsFromTestCase(TestTemplates),
        unittest.TestLoader().loadTestsFromTestCase(TestGiftCard),
        unittest.TestLoader().loadTestsFromTestCase(TestWebsite),
    ])
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

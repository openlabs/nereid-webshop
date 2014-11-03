# -*- coding: utf-8 -*-
"""
    test_party.py

    TestParty

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import os

from trytond.tests.test_tryton import DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.config import CONFIG
from test_base import BaseTestCase

CONFIG['elastic_search_server'] = os.environ.get(
    'ELASTIC_SEARCH_SERVER', "localhost:9200"
)


class TestParty(BaseTestCase):
    """
    Test Party.
    """

    def test_0030_test_party_search(self):
        """
        Test the search logic
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            # Create 5 parties
            self.Party.create([
                {
                    'name': 'Sharoon Thomas',
                },
                {
                    'name': 'Prakash Pandey',
                },
                {
                    'name': 'Tarun Bhardwaj',
                },
                {
                    'name': 'Rituparna Panda',
                },
                {
                    'name': 'Gaurav Butola',
                },
            ])

            # Test cases for search
            results = self.Party.search([])
            self.assertEqual(len(results), 5 + 4)

            results = self.Party.search([('rec_name', 'ilike', '%thomas%')])
            self.assertEqual(len(results), 1)

            result1 = self.Party.search([
                ('rec_name', 'ilike', '%thomas%'),
                ('rec_name', 'ilike', '%haroon%'),
            ])
            self.assertEqual(len(result1), 1)

            result1 = self.Party.search([('name', 'ilike', '%thomas%')])
            self.assertEqual(len(result1), 1)

            self.Party.search_name('thomas 12345')

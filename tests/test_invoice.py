# -*- coding: utf-8 -*-
"""
    Invoice test suite

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction
from trytond.modules.nereid_cart_b2c.tests.test_product import BaseTestCase


class TestDownloadInvoice(BaseTestCase):

    def setUp(self):

        trytond.tests.test_tryton.install_module(
            'nereid_webshop'
        )
        super(TestDownloadInvoice, self).setUp()

        self.UomCategory = POOL.get('product.uom.category')
        self.Company = POOL.get('company.company')
        self.Account = POOL.get('account.invoice')
        self.AccountLine = POOL.get('account.invoice.line')
        self.Category = POOL.get('product.category')
        self.Node = POOL.get('product.tree_node')

    def create_website(self):
        """
        Creates a website. Since the fields required to make this could
        change depending on modules installed and this is a base test case
        the creation is separated to another method
        """
        node, = self.Node.create([{
            'name': 'root',
            'slug': 'root',
            'type_': 'catalog',
        }])

        return self.NereidWebsite.create([{
            'name': 'localhost',
            'shop': self.shop,
            'company': self.company.id,
            'application_user': USER,
            'default_locale': self.locale_en_us.id,
            'guest_user': self.guest_user,
            'countries': [('add', self.available_countries)],
            'currencies': [('add', [self.usd.id])],
        }])

    def setup_defaults(self):
        """
        Setting up default values.
        """
        super(TestDownloadInvoice, self).setup_defaults()

    def test_0010_download_invoice(self):
        """
        Test to download invoice from a sale
        """
        Address = POOL.get('party.address')

        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            party2, = self.Party.create([{
                'name': 'Registered User',
            }])

            self.registered_user, = self.NereidUser.create([{
                'party': party2.id,
                'display_name': 'Registered User',
                'email': 'example@example.com',
                'password': 'password',
                'company': self.company.id,
            }])

            uom, = self.Uom.search([], limit=1)
            # Create sale
            address, = Address.create([{
                'party': party2.id,
                'name': 'Name',
                'street': 'Street',
                'streetbis': 'StreetBis',
                'zip': 'zip',
                'city': 'City',
                'country': self.available_countries[0].id,
                'subdivision':
                    self.available_countries[0].subdivisions[0].id,
            }])
            sale, = self.Sale.create([{
                'party': party2,
                'company': self.company.id,
                'invoice_address': address.id,
                'shipment_address': address.id,
                'currency': self.usd.id,
                'lines': [
                    ('create', [{
                        'product': self.product1.id,
                        'quantity': 1,
                        'unit': self.template1.sale_uom.id,
                        'unit_price': self.template1.list_price,
                        'description': 'description',
                    }])]
            }])
            self.Sale.quote([sale])
            self.Sale.confirm([sale])
            with Transaction().set_context(company=self.company.id):

                self.Sale.process([sale])
                self.Account.post(sale.invoices)
            with app.test_client() as c:
                # Loged in user tries to download invoice
                self.login(c, 'example@example.com', 'password')
                response = c.get(
                    '/orders/invoice/%s/download' % (sale.invoices[0].id, )
                )
                self.assertEqual(response.status_code, 200)


def suite():
    "Test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestDownloadInvoice)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

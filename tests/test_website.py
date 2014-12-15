'''

    Test Website

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) LTD
    :license: GPLv3, see LICENSE for more details
'''
from decimal import Decimal
from random import choice
import json

from trytond.tests.test_tryton import USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction
from test_base import BaseTestCase


class TestWebsite(BaseTestCase):
    """
    Test case for website.
    """

    def create_test_products(self):
        # Create product templates with products
        self._create_product_template(
            'product 1',
            [{
                'category': self.category.id,
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
            }],
            uri='product-1',
        )
        self._create_product_template(
            'product 2',
            [{
                'category': self.category2.id,
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('20'),
                'cost_price': Decimal('5'),
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
            }],
            uri='product-2',
        )
        self._create_product_template(
            'product 3',
            [{
                'category': self.category3.id,
                'type': 'goods',
                'list_price': Decimal('30'),
                'cost_price': Decimal('5'),
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
            }],
            uri='product-3',
        )
        self._create_product_template(
            'product 4',
            [{
                'category': self.category3.id,
                'type': 'goods',
                'list_price': Decimal('30'),
                'cost_price': Decimal('5'),
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
            }],
            uri='product-4',
        )

    def _create_product_template(
        self, name, vlist, uri, uom=u'Unit', displayed_on_eshop=True
    ):
        """
        Create a product template with products and return its ID

        :param name: Name of the product
        :param vlist: List of dictionaries of values to create
        :param uri: uri of product template
        :param uom: Note it is the name of UOM (not symbol or code)
        :param displayed_on_eshop: Boolean field to display product
                                   on shop or not
        """
        _code_list = []
        code = choice('ABCDEFGHIJK')
        while code in _code_list:
            code = choice('ABCDEFGHIJK')
        else:
            _code_list.append(code)

        for values in vlist:
            values['name'] = name
            values['default_uom'], = self.Uom.search(
                [('name', '=', uom)], limit=1
            )
            values['sale_uom'], = self.Uom.search(
                [('name', '=', uom)], limit=1
            )
            values['products'] = [
                ('create', [{
                    'uri': uri,
                    'displayed_on_eshop': displayed_on_eshop,
                    'code': code,
                }])
            ]
        return self.ProductTemplate.create(vlist)

    def test_0010_sitemap(self):
        """
        Tests the rendering of the sitemap.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            node1, = self.Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
            }])

            node2, = self.Node.create([{
                'name': 'Node2',
                'type_': 'catalog',
                'slug': 'node2',
                'display': 'product.template',
            }])

            node3, = self.Node.create([{
                'name': 'Node3',
                'type_': 'catalog',
                'slug': 'node3',
            }])

            node4, = self.Node.create([{
                'name': 'Node4',
                'type_': 'catalog',
                'slug': 'node4',
            }])

            node5, = self.Node.create([{
                'name': 'Node5',
                'type_': 'catalog',
                'slug': 'node5',
            }])

            self.Node.write([node2], {
                'parent': node1
            })

            self.Node.write([node3], {
                'parent': node1,
            })

            self.Node.write([node4], {
                'parent': node3,
            })

            self.Node.write([node5], {
                'parent': node4,
            })

            with app.test_client() as c:
                rv = c.get('/sitemap')
                self.assertEqual(rv.status_code, 200)

                self.assertIn('Node1', rv.data)
                self.assertIn('Node2', rv.data)
                self.assertIn('Node3', rv.data)
                self.assertIn('Node4', rv.data)

                # Beyond depth of 2, will not show.
                self.assertNotIn('Node5', rv.data)

    def test_0020_search_data(self):
        """
        Tests that the auto-complete search URL returns JSON product data.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                self.create_test_products()

                rv = c.get('/search-auto-complete?q=product')
                self.assertEqual(rv.status_code, 200)

                data = json.loads(rv.data)

                self.assertEquals(data['results'], [])

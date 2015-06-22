# -*- coding: utf-8 -*-
"""
    Test Tree

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from test_base import BaseTestCase
from trytond.tests.test_tryton import USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction


class TestTree(BaseTestCase):
    "Test Tree"

    def test_0010_node_menu_items(self):
        """
        Test to return record of tree node
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            default_node, = self.Node.create([{
                'name': 'root',
                'slug': 'root',
                'type_': 'catalog',
            }])
            node, = self.Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
                'parent': default_node,
            }])

            with app.test_request_context('/'):
                rv = node.get_menu_item(max_depth=10)
            self.assertEqual(rv['title'], node.name)

    def test_0020_get_tree_node_children(self):
        """Test children of tree node"""

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            category, = self.Category.create([{
                'name': 'Test Category',
            }])
            uom, = self.Uom.search([('symbol', '=', 'u')])
            template, = self.ProductTemplate.create([{
                'name': 'Product 1',
                'type': 'goods',
                'category': category.id,
                'default_uom': uom.id,
                'list_price': 5000,
                'cost_price': 4000,
                'description': 'This is product 1',
            }])
            product, = self.Product.create([{
                'template': template.id,
                'code': 'code of product 1',
                'displayed_on_eshop': True,
                'uri': 'test-product',
                'active': True,
            }])

            parent_node, = self.Node.create([{
                'name': 'node1',
                'slug': 'node1',
                'product_as_menu_children': False,
            }])
            child_node1, = self.Node.create([{
                'name': 'node1',
                'slug': 'node1',
                'product_as_menu_children': False,
                'parent': parent_node.id,
            }])
            child_node2, = self.Node.create([{
                'name': 'node2',
                'slug': 'node2',
                'product_as_menu_children': False,
                'parent': parent_node.id,
            }])
            self.ProductNodeRelationship.create([{
                'product': product.id,
                'node': parent_node.id,
                'sequence': 10,
            }])

            with app.test_request_context('/'):
                rv = parent_node.get_menu_item(max_depth=10)
            self.assertEqual(len(rv['children']), 2)

    def test_0030_get_tree_node_children_as_products(self):
        """Test if children of tree node are products"""

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            category, = self.Category.create([{
                'name': 'Test Category',
            }])
            uom, = self.Uom.search([('symbol', '=', 'u')])
            template, = self.ProductTemplate.create([{
                'name': 'Product 1',
                'type': 'goods',
                'category': category.id,
                'default_uom': uom.id,
                'list_price': 5000,
                'cost_price': 4000,
                'description': 'This is product 1',
            }])
            product, = self.Product.create([{
                'template': template.id,
                'code': 'code of product 1',
                'displayed_on_eshop': True,
                'uri': 'test-product',
                'active': True,
            }])
            node1, = self.Node.create([{
                'name': 'node1',
                'slug': 'node1',
                'product_as_menu_children': True,
            }])
            self.ProductNodeRelationship.create([{
                'product': product.id,
                'node': node1.id,
                'sequence': 10,
            }])

            with app.test_request_context('/'):
                rv = node1.get_menu_item(max_depth=10)
            self.assertEqual(len(rv['children']), 1)

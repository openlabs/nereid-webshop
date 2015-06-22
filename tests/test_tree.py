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

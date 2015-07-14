# -*- coding: utf-8 -*-
'''
    Tree Node

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
'''
from trytond.pool import PoolMeta
from trytond.model import fields

__all__ = ['Node']
__metaclass__ = PoolMeta


class Node:
    __name__ = "product.tree_node"

    product_as_menu_children = fields.Boolean('Product as menu children?')

    def get_menu_item(self, max_depth):
        """
        Return dictionary with serialized node for menu item
        {
            title: <display name>,
            link: <url>,
            record: <instance of record> # if type_ is `record`
        }
        """
        res = {
            'record': self,
            'title': self.name,
            'link': self.get_absolute_url(),
            'image': self.image,
        }
        if max_depth:
            res['children'] = self.get_children(max_depth=max_depth - 1)

        return res

    def get_children(self, max_depth):
        """
        Return serialized menu_item for current treenode
        """
        if self.product_as_menu_children:
            return [
                child.get_menu_item(max_depth=max_depth - 1)
                for child in self.get_products()
            ]
        else:
            return [
                child.get_menu_item(max_depth=max_depth - 1)
                for child in self.children
            ]

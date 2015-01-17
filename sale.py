# -*- coding: utf-8 -*-
"""
    Invoice

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool
from nereid import abort

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'

    def ga_purchase_data(self, **kwargs):
        '''
        Return a dictionary that can be JSON serialised as expected by
        google analytics as a purchase confirmation
        '''
        return {
            'id': self.reference,
            'revenue': str(self.total_amount),
            'tax': str(self.tax_amount),
        }

    def _add_or_update(self, product_id, quantity, action='set'):
        """
        Raise 400 if someone tries to add gift card to cart using
        add_to_cart method
        """
        Product = Pool().get('product.product')

        if Product(product_id).is_gift_card:
            abort(400)

        return super(Sale, self)._add_or_update(product_id, quantity, action)

    def _get_email_template_paths(self):
        """
        Returns a tuple of the form:
        (html_template, text_template)
        """
        return (
            'nereid_webshop/templates/emails/sale-confirmation-html.jinja',
            'nereid_webshop/templates/emails/sale-confirmation-text.jinja'
        )

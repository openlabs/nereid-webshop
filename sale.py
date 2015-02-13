# -*- coding: utf-8 -*-
"""
    Invoice

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool
from nereid import abort

__all__ = ['Sale', 'SaleLine']
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


class SaleLine:
    __name__ = 'sale.line'

    def add_to(self, sale):
        """
        Copy sale line to new sale. and handle case of gift_card
        """
        SaleLine_ = Pool().get('sale.line')

        if not self.product.is_gift_card:
            return super(SaleLine, self).add_to(sale)

        values = {
            'product': self.product.id,
            'sale': sale.id,
            'type': self.type,
            'unit': self.unit.id,
            'quantity': self.quantity,
            'sequence': self.sequence,
            'description': self.description,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'message': self.message,
            'gc_price': self.gc_price,
            'unit_price': self.unit_price
        }
        return SaleLine_(**values)

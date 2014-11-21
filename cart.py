# -*- coding: utf-8 -*-
"""
    cart.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool


__all__ = ['Cart']
__metaclass__ = PoolMeta


class Cart:
    __name__ = 'nereid.cart'

    @classmethod
    def _login_event_handler(cls, user=None):
        """
        Handle the case when cart has a line with gift card product
        """
        SaleLine = Pool().get('sale.line')

        # Find the guest cart in current session
        guest_cart = cls.find_cart(None)

        if not guest_cart:  # pragma: no cover
            return

        # There is a cart
        if guest_cart.sale and guest_cart.sale.lines:
            to_cart = cls.open_cart(True)
            # Transfer lines from one cart to another
            for from_line in guest_cart.sale.lines:
                if not from_line.product.is_gift_card:
                    to_line = to_cart.sale._add_or_update(
                        from_line.product.id, from_line.quantity
                    )
                else:
                    values = {
                        'product': from_line.product.id,
                        'sale': to_cart.sale.id,
                        'type': from_line.type,
                        'unit': from_line.unit.id,
                        'quantity': from_line.quantity,
                        'sequence': from_line.sequence,
                        'description': from_line.description,
                        'recipient_email': from_line.recipient_email,
                        'recipient_name': from_line.recipient_name,
                        'message': from_line.message,
                        'gc_price': from_line.gc_price,
                        'unit_price': from_line.unit_price
                    }
                    to_line = SaleLine(**values)
                    to_line.save()

        # Clear and delete the old cart
        guest_cart._clear_cart()

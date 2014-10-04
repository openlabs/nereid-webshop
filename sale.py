# -*- coding: utf-8 -*-
"""
    Invoice

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.pool import PoolMeta

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

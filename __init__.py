# -*- coding: utf-8 -*-
'''

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from trytond.pool import Pool
from webshop import WebShop


def register():
    Pool.register(
        WebShop,
        module='nereid_webshop', type_='model'
    )

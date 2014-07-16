# -*- coding: utf-8 -*-
'''

    :copyright: (c) 2013-14 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from trytond.pool import Pool
from webshop import WebShop, BannerCategory, Banner, Article
from product import Product
from invoice import Invoice


def register():
    Pool.register(
        WebShop,
        BannerCategory,
        Banner,
        Article,
        Product,
        Invoice,
        module='nereid_webshop', type_='model'
    )

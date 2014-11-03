# -*- coding: utf-8 -*-
'''

    :copyright: (c) 2013-14 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from trytond.pool import Pool
from party import Party, Address
from webshop import WebShop, BannerCategory, Banner, Article, Website
from product import Product
from invoice import Invoice
from sale import Sale
from shipment import ShipmentOut


def register():
    Pool.register(
        Party,
        WebShop,
        BannerCategory,
        Banner,
        Article,
        Product,
        Invoice,
        Address,
        ShipmentOut,
        Sale,
        Website,
        module='nereid_webshop', type_='model'
    )

# -*- coding: utf-8 -*-
'''
    product

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from trytond.pool import Pool, PoolMeta


__all__ = ['Product']

__metaclass__ = PoolMeta


class Product:
    "Product extension for Nereid"
    __name__ = "product.product"

    def get_default_image(self, name):
        "Returns default product image"
        ModelData = Pool().get('ir.model.data')

        images = self.get_images()
        if images:
            return images[0].id
        else:
            return ModelData.get_id("nereid_webshop", "mystery_box")

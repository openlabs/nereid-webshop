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

        # Get default image from default_image_set of product template
        # or product variant.
        if self.use_template_images:
            if self.template.default_image_set:
                return self.template.default_image_set.image.id
        elif self.default_image_set:
            return self.default_image_set.image.id

        # Fallback condition if there is no default_image_set defined
        images = self.get_images()
        if images:
            return images[0].id
        else:
            return ModelData.get_id("nereid_webshop", "mystery_box")

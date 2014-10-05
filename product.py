# -*- coding: utf-8 -*-
'''
    product

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from trytond.pool import Pool, PoolMeta
from jinja2.filters import do_striptags
from nereid import request


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

    def ga_product_data(self, **kwargs):
        '''
        Return a dictionary of the product information as expected by Google
        Analytics

        Other possible values for kwargs include

        :param list: The name of the list in which this impression is to be
                     recorded
        :param position: Integer position of the item on the view
        '''
        rv = {
            'id': self.code or unicode(self.id),
            'name': self.name,
            'category': self.category and self.category.name or None,
        }
        rv.update(kwargs)
        return rv

    def json_ld(self, **kwargs):
        '''
        Returns a JSON serializable dictionary of the product with the Product
        schema markup.

        See: http://schema.org/Product

        Any key value pairs passed to kwargs overwrites default information.
        '''
        sale_price = self.sale_price(1)

        return {
            "@context": "http://schema.org",
            "@type": "Product",

            "name": self.name,
            "sku": self.code,
            "description": do_striptags(self.description),
            "offers": {
                 "@type": "Offer",
                 "availability": "http://schema.org/InStock",
                 "price": str(sale_price),
                 "priceCurrency": request.nereid_currency.code,
            },
            "image": self.default_image.transform_command().thumbnail(
                500, 500, 'a').url(_external=True),
            "url": self.get_absolute_url(_external=True),
        }

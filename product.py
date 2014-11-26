# -*- coding: utf-8 -*-
'''
    product

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from decimal import Decimal

from trytond.pool import Pool, PoolMeta
from jinja2.filters import do_striptags
from werkzeug.exceptions import NotFound

from nereid import jsonify, flash, request, url_for, route, redirect, \
    render_template, abort
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('gift_card')

from forms import GiftCardForm


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

    @classmethod
    @route('/product/<uri>')
    @route('/product/<path:path>/<uri>')
    def render(cls, uri, path=None):
        """
        Render gift card template if product is of type gift card
        """
        render_obj = super(Product, cls).render(uri, path)

        if not isinstance(render_obj, NotFound) \
                and render_obj.context['product'].is_gift_card:
            # Render gift card
            return redirect(
                url_for('product.product.render_gift_card', uri=uri)
            )
        return render_obj

    @classmethod
    @route('/gift-card/<uri>', methods=['GET', 'POST'])
    def render_gift_card(cls, uri):
        """
        Add gift card as a new line in cart
        Request:
            'GET': Renders gift card page
            'POST': Buy Gift Card
        Response:
            'OK' if X-HTTPRequest
            Redirect to shopping cart if normal request
        """
        SaleLine = Pool().get('sale.line')
        Cart = Pool().get('nereid.cart')

        try:
            product, = cls.search([
                ('displayed_on_eshop', '=', True),
                ('uri', '=', uri),
                ('template.active', '=', True),
                ('is_gift_card', '=', True)
            ], limit=1)
        except ValueError:
            abort(404)

        form = GiftCardForm(product)

        if form.validate_on_submit():
            cart = Cart.open_cart(create_order=True)

            # Code to add gift card as a line to cart
            values = {
                'product': product.id,
                'sale': cart.sale.id,
                'type': 'line',
                'sequence': 10,
                'quantity': 1,
                'unit': None,
                'description': None,
                'recipient_email': form.recipient_email.data,
                'recipient_name': form.recipient_name.data,
                'message': form.message.data,
            }
            values.update(SaleLine(**values).on_change_product())

            # Here 0 means the default option to enter open amount is
            # selected
            if form.selected_amount.data != 0:
                values.update({'gc_price': form.selected_amount.data})
                values.update(SaleLine(**values).on_change_gc_price())
            else:
                values.update({'unit_price': Decimal(form.open_amount.data)})

            order_line = SaleLine(**values)
            order_line.save()

            message = 'Gift Card has been added to your cart'
            if request.is_xhr:  # pragma: no cover
                return jsonify(message=message)

            flash(_(message), 'info')
            return redirect(url_for('nereid.cart.view_cart'))

        return render_template(
            'catalog/gift-card.html', product=product, form=form
        )

    def get_absolute_url(self, **kwargs):
        """
        Return gift card URL if product is a gift card
        """
        if self.is_gift_card:
            return url_for(
                'product.product.render_gift_card', uri=self.uri, **kwargs
            )
        return super(Product, self).get_absolute_url(**kwargs)

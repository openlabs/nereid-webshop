# -*- coding: utf-8 -*-
"""
    forms.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from flask_wtf import Form
from wtforms import TextField, TextAreaField, SelectField, DecimalField, \
    validators
from wtforms.validators import ValidationError
from nereid import abort

from trytond.pool import Pool


class GiftCardForm(Form):
    """
    A form for purchasing gift cards
    """

    recipient_name = TextField('Recipient Name', [validators.Required(), ])
    recipient_email = TextField(
        'Recipient Email', [validators.Required(), validators.Email()]
    )
    message = TextAreaField('Message')
    selected_amount = SelectField('Amount', choices=[], coerce=int)
    open_amount = DecimalField('Amount')

    def __init__(self, product, *args, **kwargs):
        super(GiftCardForm, self).__init__(*args, **kwargs)
        Product = Pool().get('product.product')

        if not isinstance(product, Product):
            abort(400)

        try:
            self.gc_product, = Product.search([
                ('id', '=', product.id),
                ('template.is_gift_card', '=', True)
            ], limit=1)
        except ValueError as e:
            e.message = 'Expected Gift Card, Got %s' % (product.rec_name)
            raise

        if not self.gc_product.allow_open_amount:
            self.selected_amount.validators.append(validators.Required())
            self.fill_choices()
        else:
            self.selected_amount.validators.append(validators.optional())
            self.open_amount.validators.append(validators.Required())

    def fill_choices(self):
        self.selected_amount.choices = [
            (p.id, p.price) for p in self.gc_product.gift_card_prices
        ]

    def validate_open_amount(form, field):
        if not form.gc_product.allow_open_amount:
            return

        if field.data not in range(
                form.gc_product.gc_min, form.gc_product.gc_max + 1):
            raise ValidationError(
                "Amount between %s and %s is allowed." % (
                    form.gc_product.gc_min, form.gc_product.gc_max
                )
            )

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

    recipient_name = TextField('Recipient Name', [validators.Optional()])
    recipient_email = TextField('Recipient Email')
    message = TextAreaField('Message', [validators.Optional()])
    selected_amount = SelectField('Select Amount', choices=[], coerce=int)
    open_amount = DecimalField('Amount', default=0)

    def __init__(self, product, *args, **kwargs):
        super(GiftCardForm, self).__init__(*args, **kwargs)
        Product = Pool().get('product.product')

        if not isinstance(product, Product):
            abort(400)

        try:
            self.gc_product, = Product.search([
                ('id', '=', product.id),
                ('is_gift_card', '=', True)
            ], limit=1)
        except ValueError as e:
            e.message = 'Expected Gift Card, Got %s' % (product.rec_name)
            raise

        self.fill_choices()

        if self.gc_product.gift_card_delivery_mode in ['virtual', 'combined']:
            self.recipient_email.validators = [
                validators.Required(), validators.Email()
            ]
        else:
            self.recipient_email.validators = [
                validators.Optional(), validators.Email()
            ]

    def fill_choices(self):
        choices = []
        if self.gc_product.allow_open_amount:
            choices = [(0, 'Set my Own')]

        self.selected_amount.choices = choices + [
            (p.id, p.price) for p in self.gc_product.gift_card_prices
        ]

    def validate_open_amount(form, field):
        if not form.gc_product.allow_open_amount:
            return

        if (form.selected_amount.data == 0) and not (
            form.gc_product.gc_min <= field.data <= form.gc_product.gc_max
        ):
            raise ValidationError(
                "Amount between %s and %s is allowed." % (
                    form.gc_product.gc_min, form.gc_product.gc_max
                )
            )

# -*- coding: utf-8 -*-
'''
    shipment

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from functools import partial

from trytond.model import ModelView, Workflow
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction
from trytond.config import CONFIG
from trytond.report.report import Report

from jinja2 import Environment, PackageLoader
from nereid import render_email
from babel.numbers import format_currency


__metaclass__ = PoolMeta

__all__ = ['ShipmentOut']


class ShipmentOut:
    __name__ = 'stock.shipment.out'

    def get_shipment_message(self, env):
        """
        Generates email message for shipment.

        :param env: Environment instance to get html and text templates
        """
        # Generic message, downstream modules can modify.
        subject = "Order Shipped"

        html_template = env.get_template('shipment_alert_mail.html')
        text_template = env.get_template('shipment_alert_mail.txt')

        return render_email(
            CONFIG['smtp_default_from_email'], self.customer.email, subject,
            html_template=html_template,
            text_template=text_template,
            currencyformat=partial(
                format_currency, locale=Transaction().language
            ),
            formatLang=lambda *args, **kargs: Report.format_lang(
                *args, **kargs
            ),
            shipment=self,
        )

    def send_shipment_alert(self):
        """Alert user about shipment status.
        """
        EmailQueue = Pool().get('email.queue')
        ModelData = Pool().get('ir.model.data')
        Group = Pool().get('res.group')

        if self.delivery_mode != 'ship' or not self.customer.email:
            return

        group_id = ModelData.get_id(
            "nereid_webshop", "shipment_notification_group"
        )
        recepients = [self.customer.email] + filter(
            None, map(lambda user: user.email, Group(group_id).users)
        )

        message = self.get_shipment_message(Environment(loader=PackageLoader(
            'trytond.modules.nereid_webshop', 'emails'
        )))

        EmailQueue.queue_mail(
            CONFIG['smtp_default_from_email'],
            recepients,
            message.as_string()
        )

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def done(cls, shipments):
        """Mark shipment done and send an alert to user.
        """
        super(ShipmentOut, cls).done(shipments)

        for shipment in shipments:
            shipment.send_shipment_alert()

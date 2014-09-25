# -*- coding: utf-8 -*-
'''
    shipment

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from trytond.model import ModelView, Workflow
from trytond.pool import PoolMeta

__metaclass__ = PoolMeta

__all__ = ['ShipmentOut']


class ShipmentOut:
    __name__ = 'stock.shipment.out'

    def send_shipment_alert(self):
        """Alert user about shipment status.
        """
        # XXX: Not implemented yet
        return

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def done(cls, shipments):
        """Mark shipment done and send an alert to user.
        """
        super(ShipmentOut, cls).done(shipments)

        for shipment in shipments:
            shipment.send_shipment_alert()

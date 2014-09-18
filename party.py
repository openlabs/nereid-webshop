# -*- coding: utf-8 -*-
'''
    party

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
import logging

from trytond.pool import PoolMeta, Pool
from trytond.modules.nereid.party import AddressForm
from trytond.config import CONFIG
from nereid import request

__metaclass__ = PoolMeta
__all__ = ['Address']

geoip = None
try:
    from pygeoip import GeoIP
except ImportError:
    logging.error("pygeoip is not installed")
else:
    path = CONFIG.get('geoip_data_path')
    if path:
        geoip = GeoIP(path)


class WebshopAddressForm(AddressForm):
    """Custom address form for webshop
    """
    def get_default_country(self):
        """Get the default country based on geoip data.
        """
        if not geoip:
            return None

        Country = Pool().get('country.country')
        try:
            country, = Country.search([
                ('code', '=', geoip.country_code_by_addr(request.remote_addr))
            ])
        except ValueError:
            return None
        return country

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):

        # While choices can be assigned after the form is constructed, default
        # cannot be. The form's data is picked from the first available of
        # formdata, obj data, and kwargs.
        # Once the data has been resolved, changing the default won't do
        # anything.
        default_country = self.get_default_country()
        if default_country:
            kwargs.setdefault('country', default_country.id)

        super(WebshopAddressForm, self).__init__(
            formdata, obj, prefix, **kwargs
        )


class Address:
    __name__ = 'party.address'

    @classmethod
    def get_address_form(cls, address=None):
        """
        Return an initialised Address form that can be validated and used to
        create/update addresses

        :param address: If an active record is provided it is used to autofill
                        the form.
        """
        if address:
            form = WebshopAddressForm(
                request.form,
                name=address.name,
                street=address.street,
                streetbis=address.streetbis,
                zip=address.zip,
                city=address.city,
                country=address.country and address.country.id,
                subdivision=address.subdivision and address.subdivision.id,
                email=address.party.email,
                phone=address.party.phone
            )
        else:
            address_name = "" if request.nereid_user.is_anonymous() else \
                request.nereid_user.display_name
            form = WebshopAddressForm(request.form, name=address_name)

        return form

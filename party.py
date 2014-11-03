# -*- coding: utf-8 -*-
'''
    party

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
import os
import re
import logging
from wtforms import TextField, validators
from pyes import BoolQuery, QueryStringQuery

from trytond.pool import PoolMeta, Pool
from trytond.modules.nereid.party import AddressForm
from trytond.config import CONFIG
from nereid import request, current_app

from trytond.modules.nereid_checkout.i18n import _

__metaclass__ = PoolMeta
__all__ = ['Address']

ZIP_RE = re.compile(r'(\d{5})')

geoip = None
try:
    from pygeoip import GeoIP
except ImportError:
    logging.error("pygeoip is not installed")
else:
    path = os.environ.get('GEOIP_DATA_PATH', CONFIG.get('geoip_data_path'))
    if path:
        geoip = GeoIP(path)


class WebshopAddressForm(AddressForm):
    """Custom address form for webshop
    """

    phone = TextField(_('Phone'), [validators.Required(), ])

    def get_default_country(self):
        """Get the default country based on geoip data.
        """
        if not geoip:
            return None

        Country = Pool().get('country.country')
        try:
            current_app.logger.debug(
                "GeoIP lookup for remote address: %s" % request.remote_addr
            )
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


class Party:
    __name__ = 'party.party'

    def elastic_search_json(self):
        """
        Return a JSON serializable dictionary
        """
        return {
            'id': self.id,
            'name': self.rec_name,
            'code': self.code,
            'addresses': [{
                'full_address': address.full_address
            } for address in self.addresses],
            'contact_mechanisms': [{
                'type': mech.type,
                'value': mech.value,
            } for mech in self.contact_mechanisms],

        }

    @classmethod
    def search_name(cls, search_phrase, limit=100, fields=None):
        """
        Search on elasticsearch server for the given search phrase
        """
        config = Pool().get('elasticsearch.configuration')(1)

        # Create connection with elastic server
        conn = config.get_es_connection()

        search_phrase = search_phrase.replace('%', '')

        # Search the query string in all fields
        query = BoolQuery(
            should=[
                QueryStringQuery(search_phrase, default_field='name'),
                QueryStringQuery(search_phrase, default_field='name.partial'),
                QueryStringQuery(search_phrase, default_field='name.metaphone'),
            ]
        )

        # Handle the zip codes specially
        zip_codes = ZIP_RE.findall(search_phrase)
        if filter(None, zip_codes):
            query.add_should(
                QueryStringQuery(
                    ' '.join(zip_codes),
                    default_field='addresses.full_address', boost=4
                )
            )

        # TODO: Handle fields
        return conn.search(
            query,
            doc_types=[config.make_type_name('party.party')],
            size=limit
        )

    @classmethod
    def search(
            cls, domain, offset=0, limit=None, order=None, count=False,
            query=False):
        """
        Plug elastic search in to efficiently search queries which meet the
        full text search criteria.
        """
        logger = Pool().get('elasticsearch.configuration').get_logger()

        if not domain:
            return super(Party, cls).search(
                domain, offset, limit, order, count
            )

        for clause in domain:
            if clause and clause[0] != 'rec_name':
                return super(Party, cls).search(
                    domain, offset, limit, order, count, query,
                )
        else:
            # gets executed only if the search is for records with
            # rec_name only. This cannot be implemented on search_rec_name
            # because a query on the GTK client for "tom sawyer" would
            # return a two clause domain and search_rec_name will get
            # called twice
            search_phrase = ' '.join([c[2] for c in filter(None, domain)])
            results = [
                r.id for r in
                cls.search_name(search_phrase, limit=limit, fields=["id"])
            ]
            if not results:
                logger.info(
                    "Search for %s resulted in no results" % search_phrase
                )
                # If the server returned nothing, we might as well
                # fallback on trytond
                results = super(Party, cls).search(
                    domain, offset, limit, order, count, query,
                )
                logger.info(
                    "Search for %s resulted in tryton yielded: %d results" % (
                        search_phrase, len(results)
                    )
                )
            return results


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
                phone=address.phone_number and address.phone_number.value
            )
        else:
            address_name = "" if request.nereid_user.is_anonymous() else \
                request.nereid_user.display_name
            form = WebshopAddressForm(request.form, name=address_name)

        return form

    @classmethod
    def create(cls, vlist):
        """
        Create a record in elastic search on create for party

        :param vlist: List of dictionaries of fields with values
        """
        IndexBacklog = Pool().get('elasticsearch.index_backlog')

        addresses = super(Address, cls).create(vlist)
        IndexBacklog.create_from_records([a.party for a in addresses])
        return addresses

    @classmethod
    def write(cls, addresses, values, *args):
        """
        Create a record in elastic search on write for the party
        """
        IndexBacklog = Pool().get('elasticsearch.index_backlog')
        rv = super(Address, cls).write(addresses, values, *args)
        IndexBacklog.create_from_records([a.party for a in addresses])
        return rv

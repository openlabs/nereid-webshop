# -*- coding: utf-8 -*-
'''
    website

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
import os

from flask.helpers import send_from_directory
from trytond.model import ModelSQL
from nereid import current_app


__all__ = ['WebShop']

#: Get the static folder. The static folder also
#: goes into the site packages
STATIC_FOLDER = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)
    ), 'static'
)


class WebShop(ModelSQL):
    "website"
    __name__ = "nereid.webshop"

    @classmethod
    def send_static_file(self, filename):
        """Function used internally to send static files from the static
        folder to the browser.
        """
        cache_timeout = current_app.get_send_file_max_age(filename)
        return send_from_directory(
            STATIC_FOLDER, filename,
            cache_timeout=cache_timeout
        )

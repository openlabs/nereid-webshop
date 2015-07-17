# -*- coding: utf-8 -*-
"""
    static_file

    :copyright: (c) 2015 by Fulfil.IO Inc.
    :license: see LICENSE for details.
"""
import os
from trytond.pool import PoolMeta, Pool

__all__ = ['NereidStaticFile']
__metaclass__ = PoolMeta


class NereidStaticFile:
    "Static files for Nereid"
    __name__ = "nereid.static.file"

    def get_file_binary(self, name):
        '''
        Getter for the binary_file field. This fetches the file from the
        file system, coverts it to buffer and returns it.
        :param name: Field name
        :return: File buffer
        '''
        ModelData = Pool().get('ir.model.data')
        try:
            mystery_box_id = ModelData.get_id("nereid_webshop", "mystery_box")
        except Exception:
            mystery_box_id = None

        if self.id == mystery_box_id:
            # XXX: This is default webshop image that need to be replaced
            # by binary content of product no image. Ugly hack ;)
            # Can't find provision to store binary file in xml.
            location = os.path.join(
                os.path.dirname(__file__), 'static/images/no-product-image.png'
            )
            with open(location, 'rb') as file_reader:
                return buffer(file_reader.read())
        return super(NereidStaticFile, self).get_file_binary(name)

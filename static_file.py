# -*- coding: utf-8 -*-
"""
    static_file

    :copyright: (c) 2015 by Fulfil.IO Inc.
    :license: see LICENSE for details.
"""
import os
from trytond.pool import PoolMeta

__all__ = ['NereidStaticFile']
__metaclass__ = PoolMeta


class NereidStaticFile:
    "Static files for Nereid"
    __name__ = "nereid.static.file"

    def _set_file_binary(self, value):
        """
        Setter for static file that stores file in file system
        :param value: The value to set
        """
        if self.name == 'no-product-image.png' and \
                value == 'binary-default-image':
            # XXX: This is default webshop image that need to be replaced
            # by binary content of product no image. Ugly hack ;)
            # Can't find provision to store binary file in xml.
            value = open(os.path.join(
                os.path.dirname(__file__), 'static/images/no-product-image.png'
            )).read()
        super(NereidStaticFile, self)._set_file_binary(value)

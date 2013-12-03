#!/usr/bin/env python
import os

from nereid import Nereid
from werkzeug.contrib.sessions import FilesystemSessionStore
from nereid.contrib.locale import Babel
from nereid.sessions import Session

CWD = os.path.abspath(os.path.dirname(__file__))

CONFIG = dict(

    # The name of database
    DATABASE_NAME='webshop',

    # Tryton Config file path
    TRYTON_CONFIG='../../etc/trytond.conf',

    # If the application is to be configured in the debug mode
    DEBUG=False,

    # Load the template from FileSystem in the path below instead of the
    # default Tryton loader where templates are loaded from Database
    TEMPLATE_LOADER_CLASS='nereid.templating.FileSystemLoader',
    TEMPLATE_SEARCH_PATH='.',

    # The location where the translations of this template are stored
    TRANSLATIONS_PATH='i18n',
)

# Create a new application
app = Nereid(static_folder='%s/static/' % CWD, static_url_path='/static')

# Update the configuration with the above config values
app.config.update(CONFIG)

# Initialise the app, connect to cache and backend
app.initialise()

# Setup the filesystem cache
app.session_interface.session_store = FilesystemSessionStore(
    '/tmp', session_class=Session
)

Babel(app)


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0')

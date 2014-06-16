"""
    fabfile

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import os
import getpass

import requests
from fabric.tasks import execute
from fabric.api import sudo, cd, prefix, run, env
from fabric.decorators import hosts

# Forward the SSH agent so that git pull works
env.forward_agent = True
env.use_ssh_config = True

hipchat_notification_token = open(
    os.path.expanduser('~/.hipchat-token')
).read().replace('\n', '')


def notify_hipchat(
        message, from_='deployer', color='gray', room_id='352564',
        message_format="text", notify=False):
    """
    Send the given message to hipchat room
    """
    rv = requests.post(
        "https://api.hipchat.com/v1/rooms/message?format=json"
        "&auth_token=%s" % (hipchat_notification_token),
        data={
            'room_id': room_id,
            'from': from_,
            'message': message,
            'message_format': message_format,
            'notify': notify and 1 or 0,
            'color': color,
        }
    )
    return rv


def _update_schema(database, module=None):
    "Run trytond and update schema for given database"
    if module:
        run(
            'trytond -c etc/trytond.conf -u %s -d %s' % (
                module, database
            )
        )
    else:
        run('trytond -c etc/trytond.conf -u nereid_webshop -d %s' % database)


@hosts('%s@demo.openlabs.us' % getpass.getuser())
def deploy_staging(schema_update=False):
    "Deploy to staging"
    notify_hipchat("Beginning deployment", from_="Staging")
    root_path = '/opt/webshop_demo'
    sudo('chmod -R g+rw %s' % root_path)

    with cd(root_path):
        with prefix("source %s/bin/activate" % root_path):
            with cd('nereid-webshop'):
                run('git fetch')
                run('git checkout origin/develop')
                run('python setup.py install')

            if schema_update:
                execute(_update_schema, 'webshop')

            notify_hipchat("Restarting services", from_="Staging")
            sudo('bin/supervisorctl restart all')


@hosts('%s@demo.openlabs.us' % getpass.getuser())
def update_module(module):
    "Deploy to staging"
    notify_hipchat("Updating module", from_="Staging")
    root_path = '/opt/webshop-demo'
    sudo('chmod -R g+rw %s' % root_path)

    with cd(root_path):
        with prefix("source %s/bin/activate" % root_path):
            with cd(module):
                run('git fetch')
                run('git checkout origin/develop')
                run('python setup.py install')

            execute(_update_schema, 'webshop', module.replace('-', '_'))

            notify_hipchat("Restarting services", from_="Staging")
            sudo('bin/supervisorctl restart all')


@hosts('%s@demo.openlabs.us' % getpass.getuser())
def update_documentation():
    """
    Update the documentation on the current host.

    This method is host agnostic
    """
    root_path = '/opt/webshop-demo'

    with cd(root_path):
        with prefix("source %s/bin/activate" % root_path):
            run('pip install sphinx_rtd_theme')
            with cd('nereid-webshop'):
                run('python setup.py build_sphinx')

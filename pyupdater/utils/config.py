# --------------------------------------------------------------------------
# Copyright 2014 Digital Sapphire Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------
import logging
import os

from pyupdater import settings

log = logging.getLogger(__name__)


class Loader(object):
    """Loads &  saves config file
    """

    def __init__(self, db):
        self.cwd = os.getcwd()
        self.db = db
        self.password = os.environ.get(settings.USER_PASS_ENV)
        self.config_key = settings.CONFIG_DB_KEY_APP_CONFIG

    def load_config(self):
        """Loads config from database

            Returns (obj): Config object
        """
        config_data = self.db.load(self.config_key)
        config_data.DATA_DIR = os.getcwd()
        return config_data

    def save_config(self, obj):
        """Saves config file to pyiupdater database

        Args:

            obj (obj): config object
        """
        log.info('Saving Config')
        self.db.save(self.config_key, obj)
        log.info('Config saved')
        self.write_config_py(obj)
        log.info('Wrote client config')

    def write_config_py(self, obj):
        """Writes client config to client_config.py

        Args:

            obj (obj): config object
        """
        filename = os.path.join(self.cwd, settings.USER_CLIENT_CONFIG_FILENAME)
        attr_str_format = "    {} = '{}'\n"
        attr_format = "    {} = {}\n"
        with open(filename, u'w') as f:
            f.write(u'class ClientConfig(object):\n')
            if hasattr(obj, u'APP_NAME') and obj.APP_NAME is not None:
                f.write(attr_str_format.format(u'APP_NAME', obj.APP_NAME))
                log.debug(u'Wrote APP_NAME to client config')
            if hasattr(obj, u'COMPANY_NAME') and obj.COMPANY_NAME is not None:
                f.write(attr_str_format.format(u'COMPANY_NAME',
                        obj.COMPANY_NAME))
                log.debug(u'Wrote COMPANY_NAME to client config')
            if hasattr(obj, u'UPDATE_URLS') and obj.UPDATE_URLS is not None:
                f.write(attr_format.format(u'UPDATE_URLS', obj.UPDATE_URLS))
                log.debug(u'Wrote UPDATE_URLS to client config')
            if hasattr(obj, u'PUBLIC_KEYS') and obj.PUBLIC_KEYS is not None:
                f.write(attr_format.format(u'PUBLIC_KEYS', obj.PUBLIC_KEYS))
                log.debug(u'Wrote PUBLIC_KEYS to client config')


class PyiUpdaterConfig(dict):
    u"""Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.

    You can define the configuration options in the
    module that calls :meth:`from_object`.  It is also possible to tell it
    to use the same module and with that provide the configuration values
    just before the call.

    Loading from modules, only uppercase keys are added to the config.
    This makes it possible to use lowercase values in the config file for
    temporary values that are not added to the config or to define the config
    keys in the same file that implements the application.
    """

    def __init__(self, obj=None):
        super(PyiUpdaterConfig, self).__init__(dict())
        if obj is not None:
            self.from_object(obj)

    def from_object(self, obj):
        u"""Updates the values from the given object

        Args:

            obj (instance): Object with config attributes

        Objects are classes.

        Just the uppercase variables in that object are stored in the config.
        Example usage::

            from yourapplication import default_config
            app.config.from_object(default_config())
        """
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def update_config(self, obj):
        u"""Proxy method to update self

        Args:

            obj (instance): config object
        """
        self.from_object(obj)
        if self.get(u'APP_NAME') is None:
            self[u'APP_NAME'] = settings.GENERIC_APP_NAME
        if self.get(u'COMPANY_NAME') is None:
            self[u'COMPANY_NAME'] = settings.GENERIC_COMPANY_NAME

    def __str__(self):
        return dict.__repr__(self)

    def __unicode__(self):
        pass

    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, dict.__repr__(self))


# This is the default config used
class SetupConfig(object):
    """Default config object
    """
    # If left None "Not_So_TUF" will be used
    APP_NAME = None

    # Company/Your name
    COMPANY_NAME = None

    # Public Keys used by your app to verify update data
    # REQUIRED
    PUBLIC_KEYS = None

    # List of urls to ping for updates
    # REQUIRED
    UPDATE_URLS = None

    # Support for patch updates
    UPDATE_PATCHES = True

    # Upload Setup
    OBJECT_BUCKET = None

    SSH_REMOTE_DIR = None
    SSH_HOST = None
    SSH_USERNAME = None

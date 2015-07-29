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
from __future__ import unicode_literals

import logging
import os

from pyupdater import settings

log = logging.getLogger(__name__)


# Used to transistion from pickle data to plain json
class TransistionDict(dict):
    def __init__(self, *args, **kwargs):
        super(TransistionDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def from_object(self, obj):
        """Updates the values from the given object

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
        if self.get('APP_NAME') is None:
            self['APP_NAME'] = settings.GENERIC_APP_NAME
        if self.get('COMPANY_NAME') is None:
            self['COMPANY_NAME'] = settings.GENERIC_COMPANY_NAME


class Loader(object):
    """Loads &  saves config file
    """

    def __init__(self, db):
        self.cwd = os.getcwd()
        self.db = db
        self.password = os.environ.get(settings.USER_PASS_ENV)
        self.config_key = settings.CONFIG_DB_KEY_APP_CONFIG

    def _convert_obj_to_dict(self, obj):
        config = {}
        if obj is not None:
            for k, v in obj.__dict__.items():
                config[k] = v
        return config

    def load_config(self):
        """Loads config from database

            Returns (obj): Config object
        """
        config_data = self.db.load(self.config_key)
        if isinstance(config_data, dict) is False:
            config_data = self._convert_obj_to_dict(config_data)
        backwards_compat_config = TransistionDict()
        for k, v in config_data.items():
            backwards_compat_config[k] = v
        backwards_compat_config.DATA_DIR = os.getcwd()
        return backwards_compat_config

    def save_config(self, obj):
        """Saves config file to pyupdater database

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
        with open(filename, 'w') as f:
            f.write('class ClientConfig(object):\n')
            if hasattr(obj, 'APP_NAME') and obj.APP_NAME is not None:
                f.write(attr_str_format.format('APP_NAME', obj.APP_NAME))
                log.debug('Wrote APP_NAME to client config')
            if hasattr(obj, 'COMPANY_NAME') and obj.COMPANY_NAME is not None:
                f.write(attr_str_format.format('COMPANY_NAME',
                        obj.COMPANY_NAME))
                log.debug('Wrote COMPANY_NAME to client config')
            if hasattr(obj, 'UPDATE_URLS') and obj.UPDATE_URLS is not None:
                f.write(attr_format.format('UPDATE_URLS', obj.UPDATE_URLS))
                log.debug('Wrote UPDATE_URLS to client config')
            if hasattr(obj, 'PUBLIC_KEYS') and obj.PUBLIC_KEYS is not None:
                f.write(attr_format.format('PUBLIC_KEYS', obj.PUBLIC_KEYS))
                log.debug('Wrote PUBLIC_KEYS to client config')


# This is the default config used
SetupConfig = {
    # If left None "Not_So_TUF" will be used
    'APP_NAME': settings.GENERIC_APP_NAME,

    # Company/Your name
    'COMPANY_NAME': settings.GENERIC_APP_NAME,

    # Support for patch updates
    'UPDATE_PATCHES': True
    }

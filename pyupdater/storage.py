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
import json
import logging
import os
import pickle

from pyupdater import settings


log = logging.getLogger(__name__)


class Storage(object):

    def __init__(self, data_dir=None):
        """Loads & saves config file to file-system

            Args:

                config_dir (str): Path to directory where config will be stored
        """
        if data_dir is None:
            data_dir = os.getcwd()
        config_dir = os.path.join(data_dir, settings.CONFIG_DATA_FOLDER)
        log.debug('Config Dir: {}'.format(config_dir))
        if not os.path.exists(config_dir):
            log.info('Creating config dir')
            os.makedirs(config_dir)
        self.filename = os.path.join(config_dir, settings.CONFIG_FILE_USER)
        if not os.path.exists(self.filename):
            with open(self.filename, u'w') as f:
                f.write('{}')
        log.debug('Config DB: {}'.format(self.filename))

    def save(self, key, value):
        """Saves key & value to database

        Args:

            key (str): used to retrieve value from database

            value (obj): python object to store in database

        """
        if isinstance(key, unicode) is True:
            log.debug('Key Name: {}'.format(key))
            log.debug('Key type: {}'.format(type(key)))
            key = str(key)

        with open(self.filename, u'r') as f:
            db = json.loads(f.read())

        db[key] = pickle.dumps(value, 2)

        with open(self.filename, u'w') as f:
            f.write(json.dumps(db, indent=2, sort_keys=True))

    def load(self, key):
        """Loads value for given key

            Args:

                key (str): The key associated with the value you want
                form the database.

            Returns:

                Object if exists or else None
        """
        if isinstance(key, unicode) is True:
            log.debug('Key Name: {}'.format(key))
            log.debug('Key type: {}'.format(type(key)))
            key = str(key)

        with open(self.filename, u'r') as f:
            db = json.loads(f.read())

        value = db.get(key)
        if value is not None:
            value = pickle.loads(value)
        return value

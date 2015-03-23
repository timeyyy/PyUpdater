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
        u"""Loads & saves config file to file-system

            Args:

                config_dir (str): Path to directory where config will be stored
        """
        if data_dir is None:
            data_dir = os.getcwd()
        self.config_dir = os.path.join(data_dir, settings.CONFIG_DATA_FOLDER)
        log.debug(u'Config Dir: {}'.format(self.config_dir))
        self.filename = os.path.join(self.config_dir,
                                     settings.CONFIG_FILE_USER)
        log.debug(u'Config DB: {}'.format(self.filename))
        self.db = None
        self.sync_threshold = 3
        self.count = 0

    def load_db(self):
        if not os.path.exists(self.config_dir):
            log.info(u'Creating config dir')
            os.makedirs(self.config_dir)

        if not os.path.exists(self.filename):
            self.db = {}
            log.debug(u'Created new config data file')
        else:
            try:
                with open(self.filename, u'r') as f:
                    self.db = json.loads(f.read())
            except ValueError:
                log.error(u'Invalid config data file. Saving as '
                          u'{}.old'.format(self.filename))
                self.db = {}
                log.debug(u'Created new config data file')
        self.sync_db()

    def sync_db(self):
        if self.count >= self.sync_threshold:
            self._sync_db()
            self.count = 0
        self.count += 1

    def _sync_db(self):
        if self.db is None:
            self.load_db()
        if os.path.exists(self.config_dir):
            log.debug('Syncing db to filesystem')
            with open(self.filename, u'w') as f:
                f.write(json.dumps(self.db, indent=2, sort_keys=True))

    def save(self, key, value):
        u"""Saves key & value to database

        Args:

            key (str): used to retrieve value from database

            value (obj): python object to store in database

        """
        if self.db is None:
            self.load_db()

        if isinstance(key, unicode) is True:
            log.debug(u'Key Name: {}'.format(key))
            log.debug(u'Key type: {}'.format(type(key)))
            key = str(key)

        self.db[key] = pickle.dumps(value)

    def load(self, key):
        u"""Loads value for given key

            Args:

                key (str): The key associated with the value you want
                form the database.

            Returns:

                Object if exists or else None
        """
        if self.db is None:
            self.load_db()

        if isinstance(key, unicode) is True:
            log.debug(u'Key Name: {}'.format(key))
            log.debug(u'Key type: {}'.format(type(key)))
            key = str(key)

        value = self.db.get(key)
        if value is not None:
            value = pickle.loads(value)
        return value

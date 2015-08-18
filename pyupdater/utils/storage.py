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

import json
import logging
import os
import pickle

from pyupdater import settings


log = logging.getLogger(__name__)


class Storage(object):

    def __init__(self, data_dir=None):
        """Loads & saves config file to file-system.

            Args:

                config_dir (str): Path to directory where config will be stored
        """
        if data_dir is None:
            data_dir = os.getcwd()
        self.config_dir = os.path.join(data_dir, settings.CONFIG_DATA_FOLDER)
        if not os.path.exists(self.config_dir):
            log.info('Creating config dir')
            os.mkdir(self.config_dir)
        log.debug('Config Dir: {}'.format(self.config_dir))
        self.filename = os.path.join(self.config_dir,
                                     settings.CONFIG_FILE_USER)
        log.debug('Config DB: {}'.format(self.filename))
        self.db = None
        self.sync_threshold = 3
        self.count = 0

    def load_db(self):
        "Loads database into memory."
        if not os.path.exists(self.filename):
            self.db = {}
            log.debug('Created new config data file')
        else:
            try:
                with open(self.filename, 'r') as f:
                    self.db = json.loads(f.read())
            except ValueError:
                log.error('Invalid config data file. Saving as '
                          '{}.old'.format(self.filename))
                self.db = {}
                log.debug('Created new config data file')
        self.sync_db()

    def sync_db(self):
        "Sync updates of in memory database back to database on disk."
        if self.count >= self.sync_threshold:
            self._sync_db()
            self.count = 0
        self.count += 1

    def _sync_db(self):
        if self.db is None:
            self.load_db()
        log.debug('Syncing db to filesystem')
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.db, indent=4, sort_keys=True))

    def _export(self):
        with open('export.db', 'w') as f:
            f.write(json.dumps(self.db))

    def save(self, key, value):
        """Saves key & value to database

        Args:

            key (str): used to retrieve value from database

            value (obj): python object to store in database

        """
        if self.db is None:
            self.load_db()

        if isinstance(key, unicode) is True:
            log.debug('Key Name: {}'.format(key))
            log.debug('Key type: {}'.format(type(key)))
            key = str(key)

        self.db[key] = value

    def load(self, key):
        """Loads value for given key

            Args:

                key (str): The key associated with the value you want
                form the database.

            Returns:

                Object if exists or else None
        """
        if self.db is None:
            self.load_db()

        if isinstance(key, unicode) is True:
            log.debug('Key Name: {}'.format(key))
            log.debug('Key type: {}'.format(type(key)))
            key = str(key)

        data = self.db.get(key)
        if data is not None:
            try:
                data = pickle.loads(data)
            except:
                log.debug('Not pickle data')
                pass
            try:
                data = json.loads(data)
            except Exception as err:
                log.debug(self.db.get(key))
                log.debug(err, exc_info=True)
        return data

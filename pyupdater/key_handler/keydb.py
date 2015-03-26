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
import time

from pyupdater import settings

log = logging.getLogger(__name__)


class KeyDB(object):
    u"""Handles finding, sorting, getting meta-data, moving packages.

    Kwargs:

        data_dir (str): Path to directory containing key.db

        load (bool):

            Meaning:

                True: Load db on initialization

                False: Do not load db on initialization
    """

    def __init__(self, db, load=False):
        self.db = db
        self.data = None
        if load is True:
            self.load()

    def add_key(self, public, private, key_type='ed25519'):
        u"""Adds key pair to database

        Args:

            public (str): Public key

            private (str): Private key

            key_type (str): The type of key pair. Default ed25519
        """
        _time = time.time()
        if self.data is None:
            self.load()
        num = len(self.data) + 1
        data = {
            u'date': _time,
            u'public': public,
            u'private': private,
            u'revoked': False,
            u'key_type': key_type,
        }
        log.info('Adding public key to db. {}'.format(len(public)))
        self.data[num] = data
        self.save()

    def get_public_keys(self):
        u"Returns a list of all valid public keys"
        return self._get_keys(u'public')

    def get_private_keys(self):
        u"Returns a list of all valid private keys"
        return self._get_keys(u'private')

    def _get_keys(self, key):
        if self.data is None:
            self.load()
        order = []
        keys = []
        for k, v in self.data.items():
            if v[u'revoked'] is False:
                order.append(int(k))
            else:
                log.debug(u'Revoked key'.format(len(k)))
        order = sorted(order)
        for o in order:
            try:
                data = self.data[o]
                log.debug(u'Got key data')
                pub_key = data[key]
                keys.append(pub_key)
                log.debug(u'Got public key')
            except KeyError:  # pragma: no cover
                log.debug(u'Key error')
                continue
        return keys

    def get_revoked_key(self):
        u"Returns most recent revoked key pair"
        keys = []
        for k, v in self.data.items():
            if v[u'revoked'] is True:
                keys.append(int(k))
        if len(keys) >= 1:
            key = sorted(keys)[-1]
            info = self.data[key]
        else:
            info = None
        return info

    def revoke_key(self, count=1):
        u"""Revokes key pair

        Args:

            count (int): The number of keys to revoke. Oldest first
        """
        keys = map(str, self.data.keys())
        keys = sorted(keys)
        log.debug(u'Collecting keys'.format(keys))
        c = 0
        for k in keys:
            if c >= count:
                break
            k = int(k)
            if self.data[k][u'revoked'] is False:
                self.data[k][u'revoked'] = True
                log.debug(u'Revoked key')
                c += 1
        self.save()

    def load(self):
        u"Loads data from key.db"
        self.data = self.db.load(settings.CONFIG_DB_KEY_KEYS)
        if self.data is None:
            log.info('Key.db file not found creating new')
            self.data = dict()

    def save(self):
        u"Saves data to key.db"
        log.debug(u'Saving keys...')
        self.db.save(settings.CONFIG_DB_KEY_KEYS, self.data)
        log.debug(u'Saved keys...')

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
from __future__ import print_function

from pyupdater import settings
from pyupdater.key_handler.keydb import KeyDB
from pyupdater.utils import lazy_import


@lazy_import
def gzip():
    import gzip
    return gzip


@lazy_import
def json():
    import json
    return json


@lazy_import
def logging():
    import logging
    return logging


@lazy_import
def os():
    import os
    return os


@lazy_import
def shutil():
    import shutil
    return shutil


@lazy_import
def ed25519():
    import ed25519
    return ed25519


@lazy_import
def six():
    import six
    return six


log = logging.getLogger(__name__)


class KeyHandler(object):
    """KeyHanlder object is used to manage keys used for signing updates

    Kwargs:

        app (obj): Config object to get config values from

        db (dict): Framework metadata
    """

    def __init__(self, app=None, db=None):
        self.key_encoding = 'base64'
        if app is not None:
            self.init_app(app, db)

    def init_app(self, obj, db):
        """Sets up client with config values from obj

        Args:

            obj (instance): config object
        """
        # Copies and sets all needed config attributes
        # for this object
        self.app_name = obj.get(u'APP_NAME')
        self.private_key_name = self.app_name + u'.pem'
        self.public_key_name = self.app_name + u'.pub'
        data_dir = obj.get(u'DATA_DIR', os.getcwd())
        self.db = db
        self.config_dir = os.path.join(data_dir, u'.pyiupdater')
        self.keysdb = KeyDB(db)
        self.data_dir = os.path.join(data_dir, settings.USER_DATA_FOLDER)
        self.deploy_dir = os.path.join(self.data_dir, u'deploy')
        self.version_file = os.path.join(self.deploy_dir,
                                         settings.VERSION_FILE)

    def make_keys(self, count=3):
        """Makes public and private keys for signing and verification

        Kwargs:

            count (bool): The number of keys to create.
        """
        log.info(u'Creating {} keys'.format(count))
        c = 0
        while c < count:
            self._make_keys()
            c += 1

    def _make_keys(self):
        # Makes a set of private and public keys
        # Used for authentication
        self.keysdb.load()
        privkey, pubkey = ed25519.create_keypair()
        pri = privkey.to_ascii(encoding=self.key_encoding)
        pub = pubkey.to_ascii(encoding=self.key_encoding)
        self.keysdb.add_key(pub, pri)

    def sign_update(self):
        """Signs version file with private key

        Proxy method for :meth:`_add_sig`
        """
        # Loads private key
        # Loads version file to memory
        # Signs Version file
        # Writes version file back to disk
        self._add_sig()

    def get_public_keys(self):
        """Returns (object): Public Key
        """
        self.keysdb.load()
        return self.keysdb.get_public_keys()

    def get_recent_revoked_key(self):
        self.keysdb.load()
        return self.keysdb.get_revoked_key()

    def print_public_keys(self):
        """Prints public key data to console"""
        keys = self.get_public_key()
        print(u'Public Key:\n{}\n\n'.format(keys))

    def revoke_key(self, count):
        self.keysdb.revoke_key(count)
        self.make_keys(count)

    def _load_private_keys(self):
        # Loads private key
        log.debug(u'Loading private key')
        return self.keysdb.get_private_keys()

    def _add_sig(self):
        # Adding new signature to version file
        private_keys = self._load_private_keys()
        # Just making sure we have a least 2 keys so when revoke is
        # called we have a fall back
        if len(private_keys) < 2:
            self.make_keys()
        private_keys = self._load_private_keys()

        update_data = self._load_update_data()
        if u'sigs' in update_data:
            log.debug(u'Removing signatures from version file')
            del update_data[u'sigs']
        update_data_str = json.dumps(update_data, sort_keys=True)

        signatures = list()
        for p in private_keys:
            if six.PY2 is True and isinstance(p, unicode) is True:
                log.debug('Got type: {}'.format(type(p)))
                p = str(p)
            log.debug(u'Key type: {}'.format(type(p)))
            privkey = ed25519.SigningKey(p, encoding=self.key_encoding)
            sig = privkey.sign(six.b(update_data_str),
                               encoding=self.key_encoding)
            log.debug('Sig: {}'.format(sig))
            signatures.append(sig)

        og_data = json.loads(update_data_str)
        update_data = og_data.copy()
        update_data[u'sigs'] = signatures
        log.info(u'Adding sig to update data')
        self._write_update_data(og_data, update_data)

    def _write_update_data(self, data, version):
        # Write version file to disk
        self.db.save(settings.CONFIG_DB_KEY_VERSION_META, data)
        log.debug(u'Saved version meta data')

        with gzip.open(self.version_file, u'wb') as f:
            f.write(json.dumps(version, indent=2, sort_keys=True))
        log.info(u'Created gzipped version manifest in deploy dir')

    def _load_update_data(self):
        log.debug(u"Loading version data")
        update_data = self.db.load(settings.CONFIG_DB_KEY_VERSION_META)
        if update_data is None:
            update_data = {}
            log.error(u'Version meta data not found')
            self.db.save(settings.CONFIG_DB_KEY_VERSION_META, update_data)
            log.info(u'Created new version meta data')
        log.debug(u'Version file loaded')
        return update_data

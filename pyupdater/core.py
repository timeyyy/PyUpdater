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
import os

from pyupdater.key_handler import KeyHandler
from pyupdater.package_handler import PackageHandler
from pyupdater.uploader import Uploader
from pyupdater.utils.config import PyUpdaterConfig
from pyupdater.utils.storage import Storage


class Core(object):
    """Processes, signs & uploads updates

        Kwargs:

            config (obj): config object
    """
    def __init__(self, config=None, db=None):
        self.config = PyUpdaterConfig()
        # Important to keep this before updating config
        if config is not None:
            self.update_config(config, db)

    def update_config(self, config, db):
        u"""Updates internal config

        Args:

            config (obj): config object
        """
        if not hasattr(config, u'DATA_DIR'):
            config.DATA_DIR = None
        if config.DATA_DIR is None:
            config.DATA_DIR = os.getcwd()

        if db is None:
            self.db = Storage(config.DATA_DIR)
        else:
            self.db = db
        self.config.update_config(config)
        self._update(self.config, self.db)

    def _update(self, config, db):
        self.kh = KeyHandler(config, db)
        self.ph = PackageHandler(config, db)
        self.up = Uploader(config)

    def setup(self):
        u"""Sets up root dir with required PyUpdater folders
        """
        self.ph.setup()

    def process_packages(self):
        u"""Creates hash for updates & adds information about update to
        version file
        """
        self.ph.process_packages()

    def set_uploader(self, requested_uploader):
        u"""Sets upload destination

        Args:

            requested_uploader (str): upload service. i.e. s3, scp
        """
        self.up.set_uploader(requested_uploader)

    def upload(self):
        u"""Uploads files in deploy folder
        """
        self.up.upload()

    def make_keys(self, count=3):
        u"""Creates signing keys
        """
        self.kh.make_keys(count)

    def revoke_key(self, count):
        self.kh.revoke_key(count)

    def get_recent_revoked_key(self):
        return self.kh.get_recent_revoked_key()

    def sign_update(self):
        u"Signs version file with signing key"
        self.kh.sign_update()

    def get_public_keys(self):
        u"Returns public key"
        return self.kh.get_public_keys()

    def print_public_key(self):
        u"Prints public key to console"
        self.kh.print_public_key()

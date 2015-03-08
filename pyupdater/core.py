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
from pyupdater.config import PyiUpdaterConfig
from pyupdater.key_handler import KeyHandler
from pyupdater.package_handler import PackageHandler
from pyupdater.uploader import Uploader


class Core(object):
    """Processes, signs & uploads updates

        Kwargs:

            config (obj): config object
    """

    def __init__(self, config=None):
        self.config = PyiUpdaterConfig()
        if config is not None:
            self.update_config(config)

    def update_config(self, config):
        """Updates internal config

        Args:

            config (obj): config object
        """
        self.config.update_config(config)
        self._update(self.config)

    def _update(self, config):
        self.kh = KeyHandler(config)
        self.ph = PackageHandler(config)
        self.up = Uploader(config)

    def setup(self):
        """Sets up root dir with required PyiUpdater folders
        """
        self.ph.setup()

    def process_packages(self):
        """Creates hash for updates & adds information about update to
        version file
        """
        self.ph.process_packages()

    def set_uploader(self, requested_uploader):
        """Sets upload destination

        Args:

            requested_uploader (str): upload service. i.e. s3, scp
        """
        self.up.set_uploader(requested_uploader)

    def upload(self):
        """Uploads files in deploy folder
        """
        self.up.upload()

    def make_keys(self, count=3):
        """Creates signing keys
        """
        self.kh.make_keys(count)

    def revoke_key(self, count):
        self.kh.revoke_key(count)

    def get_recent_revoked_key(self):
        return self.kh.get_recent_revoked_key()

    def sign_update(self):
        "Signs version file with signing key"
        self.kh.sign_update()

    def get_public_keys(self):
        "Returns public key"
        return self.kh.get_public_keys()

    def print_public_key(self):
        "Prints public key to console"
        self.kh.print_public_key()

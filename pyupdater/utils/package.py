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

from pyupdater.utils import (parse_platform,
                             Version,
                             )
from pyupdater.utils.exceptions import UtilsError, VersionError

log = logging.getLogger(__name__)


class Patch(object):
    """Holds information for patch file.

    Args:

        patch_info (dict): patch information
    """

    def __init__(self, patch_info):
        self.dst_path = patch_info.get('dst')
        self.patch_name = patch_info.get('patch_name')
        self.dst_filename = patch_info.get('package')
        self.ready = self._check_attrs()

    def _check_attrs(self):
        if self.dst_path is not None:
            # Cannot create patch if destination file is missing
            if not os.path.exists(self.dst_path):
                return False
        # Cannot create patch if destination file is missing
        else:
            return False
        # Cannot create patch if name is missing
        if self.patch_name is None:
            return False
        # Cannot create patch is destination filename is missing
        if self.dst_filename is None:
            return False
        return True


class Package(object):
    """Holds information of update file.

    Args:

        filename (str): name of update file
    """

    def __init__(self, filename):
        self.name = None
        self.version = None
        self.filename = filename
        self.file_hash = None
        self.platform = None
        self.info = dict(status=False, reason='')
        self.patch_info = {}
        # seems to produce the best diffs.
        # Tests on homepage: https://github.com/JMSwag/PyUpdater
        # Zip doesn't keep +x permissions. Only using gz for now.
        self.supported_extensions = ['.zip', '.gz']
        # ToDo: May need to add more files to ignore
        self.ignored_files = ['.DS_Store', ]
        self.extract_info(filename)

    def extract_info(self, package):
        """Gets version number, platform & hash for package.

        Args:

            package (str): filename
        """
        if not os.path.exists(package):
            msg = 'Package does not exists'
            log.debug(msg)
            self.info['reason'] = msg
            return
        if package in self.ignored_files:
            msg = 'Ignored file: {}'.format(package)
            log.debug(msg)
            self.info['reason'] = msg
            return
        if os.path.splitext(package)[1].lower() not in \
                self.supported_extensions:
            msg = 'Not a supported archive format: {}'.format(package)
            self.info['reason'] = msg
            log.warning(msg)
            return

        log.info('Extracting update archive info for: {}'.format(package))
        try:
            self.version = str(Version(package))
        except (UtilsError, VersionError):
            msg = 'Package version not formatted correctly'
            self.info['reason'] = msg
            log.error(msg)
            return

        try:
            self.platform = parse_platform(package)
        except UtilsError:
            msg = 'Package platform not formatted correctly'
            self.info['reason'] = msg
            log.error(msg)
            return

        self.name = self._parse_package_name(package)
        self.info['status'] = True
        log.info('Info extraction complete')

    def _parse_package_name(self, package):
        # Returns package name from update archive name
        log.debug('Package name: {}'.format(package))
        ext = os.path.splitext(package)[1]
        # Removes file extension
        if ext == '.zip':
            log.debug('Removed ".zip"')
            package = package[:-4]
        elif ext == '.gz':
            log.debug('Removed ".tar.gz"')
            package = package[:-7]
        # Changes appname-platform-version to appname
        # ToDo: May need to update if support for app names with
        #       hyphens in them are requested. Example "My-App"
        return package.split('-')[0]

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

try:
    import bsdiff4
except ImportError:
    bsdiff4 = None

from pyupdater.client.downloader import FileDownloader
from pyupdater import settings
from pyupdater.utils import (get_package_hashes,
                             EasyAccessDict,
                             lazy_import,
                             Version)
from pyupdater.utils.exceptions import PatcherError

if bsdiff4 is None:
    from pyupdater.utils import bsdiff4_py as bsdiff4

log = logging.getLogger(__name__)


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.paths
    import jms_utils.system
    return jms_utils


platform_ = jms_utils.system.get_system()


class Patcher(object):
    """Downloads, verifies, and patches binaries

    Kwargs:

        name (str): Name of binary to patch

        json_data (dict): Info dict with all package meta data

        current_version (str): Version number of currently installed binary

        highest_version (str): Newest version available

        update_folder (str): Path to update folder to place updated binary in

        update_urls (list): List of urls to use for file download

        verify (bool) Meaning:

            True: Verify https connection

            False: Don't verify https connection
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get(u'name')
        self.json_data = kwargs.get(u'json_data')
        self.star_access_update_data = EasyAccessDict(self.json_data)
        self.current_version = Version(kwargs.get(u'current_version'))
        self.highest_version = kwargs.get(u'highest_version')
        self.update_folder = kwargs.get(u'update_folder')
        self.update_urls = kwargs.get(u'update_urls', [])
        self.verify = kwargs.get(u'verify', True)
        self.progress_hooks = kwargs.get(u'progress_hooks', [])
        self.patch_data = []
        self.patch_binary_data = []
        self.og_binary = None
        # ToDo: Update tests with linux archives.
        # Used for testing.
        self.plat = kwargs.get(u'platform', platform_)
        self.current_filename = kwargs.get(u'current_filename')
        self.current_file_hash = kwargs.get(u'current_file_hash')

        file_info = self._current_file_info(self.name,
                                            self.current_version)
        if self.current_filename is None:
            self.current_filename = file_info['filename']
        if self.current_file_hash is None:
            self.current_file_hash = file_info['file_hash']

    def start(self):
        "Starts patching process"

        log.debug(u'Starting patch updater...')
        # Check hash on installed binary to begin patching
        binary_check = self._verify_installed_binary()
        if not binary_check:
            log.debug(u'Binary check failed...')
            return False
        # Getting all required patch meta-data
        all_patches = self._get_patch_info(self.name)
        if all_patches is False:
            log.debug(u'Cannot find all patches...')
            return False

        # Download and verify patches in 1 go
        download_check = self._download_verify_patches()
        if download_check is False:
            log.debug(u'Patch check failed...')
            return False

        try:
            self._apply_patches_in_memory()
        except PatcherError:
            return False
        else:
            try:
                self._write_update_to_disk()
            except PatcherError:
                return False
        # Looks like all is well
        return True

    def _verify_installed_binary(self):
        # Verifies currently installed binary against known hash
        log.debug(u'Checking for current installed binary to patch')

        # I just really like using this ChDir context
        # manager.  Even sent the developer a cup of coffee
        with jms_utils.paths.ChDir(self.update_folder):
            if not os.path.exists(self.current_filename):
                log.debug(u'Cannot find binary to patch')
                return False

            installed_file_hash = get_package_hashes(self.current_filename)
            if self.current_file_hash != installed_file_hash:
                log.debug(u'Binary hash mismatch')
                return False
            with open(self.current_filename, u'rb') as f:
                self.og_binary = f.read()
            os.remove(self.current_filename)
        log.debug(u'Binary found and verified')
        return True

    # We will take all versions.  Then append any version
    # thats greater then the current version to the list
    # of needed patches.
    def _get_patch_info(self, name):
        # Taking the list of needed patches and extracting the
        # patch data from it. If any loop fails, will return False
        # and start full binary update.
        log.debug(u'Getting patch meta-data')
        required_patches = self._get_required_patches(name)

        for p in required_patches:
            info = {}
            plat_key = '{}*{}*{}*{}'.format(settings.UPDATES_KEY, name,
                                            str(p), self.plat)
            plat_info = self.star_access_update_data.get(plat_key)

            try:
                info[u'patch_name'] = plat_info[u'patch_name']
                info[u'patch_urls'] = self.update_urls
                info[u'patch_hash'] = plat_info[u'patch_hash']
                self.patch_data.append(info)
            except KeyError:
                log.error(u'Missing required patch meta-data')
                return False
        return True

    def _get_required_patches(self, name):
        needed_patches = []
        try:
            # Get list of Version objects initialized with keys
            # from update manifest
            versions = map(Version,
                           self.json_data[settings.UPDATES_KEY][name].keys())
        except KeyError:
            log.debug(u'No updates found in updates dict')

        # Ensuring we apply patches in correct order
        versions = sorted(versions)
        log.debug(u'getting required patches')
        for i in versions:
            if i > self.current_version:
                needed_patches.append(i)
        # Used to guarantee patches are only added once
        return list(set(needed_patches))

    def _download_verify_patches(self):
        # Downloads & verifies all patches
        log.debug('Downloading patches')
        downloaded = 0
        total = len(self.patch_data)
        for p in self.patch_data:
            fd = FileDownloader(p[u'patch_name'], p[u'patch_urls'],
                                p[u'patch_hash'], self.verify)

            data = fd.download_verify_return()
            if data is not None:
                self.patch_binary_data.append(data)
                downloaded += 1
                status = {u'total': total,
                          u'downloaed': downloaded,
                          u'status': u'downloading'}
                self._call_progress_hooks(status)
            else:
                return False
        status = {u'total': total,
                  u'downloaed': downloaded,
                  u'status': u'finished'}
        self._call_progress_hooks(status)
        return True

    def _call_progress_hooks(self, data):
        for ph in self.progress_hooks:
            ph(data)

    def _apply_patches_in_memory(self):
        # Applies a sequence of patches in memory
        log.debug(u'Applying patches')
        # Beginning the patch process
        self.new_binary = self.og_binary
        for i in self.patch_binary_data:
            try:
                self.new_binary = bsdiff4.patch(self.new_binary, i)
                log.debug(u'Applied patch successfully')
            except Exception as err:
                log.debug(err, exc_info=True)
                log.error(err)
                raise PatcherError(u'Patch failed to apply')

    def _write_update_to_disk(self):
        # Writes updated binary to disk
        log.debug('Writing update to disk')

        filename_key = '{}*{}*{}*{}*{}'.format(settings.UPDATES_KEY, self.name,
                                               self.highest_version,
                                               self.plat,
                                               u'filename')
        # Getting filename to create on filesystem
        filename = self.star_access_update_data.get(filename_key)
        if filename is None:
            raise PatcherError('Filename missing in version file')

        with jms_utils.paths.ChDir(self.update_folder):
            try:
                with open(filename, u'wb') as f:
                    f.write(self.new_binary)
            except IOError:
                # Removes file if it somehow got created
                if os.path.exists(filename):
                    os.remove(filename)
                log.error(u'Failed to open file for writing')
                raise PatcherError(u'Failed to open file for writing')
            else:
                file_info = self._current_file_info(self.name,
                                                    self.highest_version)

                new_file_hash = file_info['file_hash']
                log.debug(u'checking file hash match')
                if new_file_hash != get_package_hashes(filename):
                    log.error(u'File hash does not match')
                    os.remove(filename)
                    raise PatcherError(u'Patched file hash bad checksum')
            log.debug('Wrote update file')

    def _current_file_info(self, name, version):
        # Returns filename and hash for given name and version
        info = {}
        plat_key = '{}*{}*{}*{}'.format(settings.UPDATES_KEY, name,
                                        version, self.plat)
        plat_info = self.star_access_update_data.get(plat_key)

        try:
            filename = plat_info[u'filename']
        except Exception as err:
            log.debug(str(err))
            filename = ''
        log.debug(u'Current filename: {}'.format(filename))
        info[u'filename'] = filename

        try:
            file_hash = plat_info[u'file_hash']
        except Exception as err:
            log.debug(str(err))
            file_hash = ''
        info[u'file_hash'] = file_hash
        log.debug('Current file_hash {}'.format(file_hash))
        return info

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
from pyupdater.client.downloader import FileDownloader
from pyupdater.client.patcher import Patcher
from pyupdater.exceptions import ClientError, UtilsError, VersionError
from pyupdater import settings
from pyupdater.utils import (get_filename,
                             get_hash,
                             get_highest_version,
                             get_mac_dot_app_dir,
                             lazy_import,
                             Version)


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
def sys():
    import sys
    return sys


@lazy_import
def tarfile():
    import tarfile
    return tarfile


@lazy_import
def warnings():
    import warnings
    return warnings


@lazy_import
def zipfile():
    import zipfile
    return zipfile


@lazy_import
def certifi():
    import certifi
    return certifi


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.paths
    import jms_utils.system
    return jms_utils


log = logging.getLogger(__name__)


class LibUpdate(object):
    """Used to update library files used by an application

    Args:

        data (dict): Info dict
    """

    def __init__(self, data):
        self.updates_key = settings.UPDATES_KEY
        self.update_urls = data.get(u'update_urls')
        self.name = data.get(u'name')
        self.version = data.get(u'version')
        self.easy_data = data.get(u'easy_data')
        # Raw form of easy_data
        self.json_data = data.get(u'json_data')
        self.data_dir = data.get(u'data_dir')
        self.platform = data.get(u'platform')
        self.app_name = data.get(u'app_name')
        self.progress_hooks = data.get(u'progress_hooks')
        self.update_folder = os.path.join(self.data_dir,
                                          settings.UPDATE_FOLDER)
        self.verify = data.get(u'verify', True)
        self.current_app_dir = os.path.dirname(sys.argv[0])

    def is_downloaded(self):
        if self.name is None:
            return False
        return self._is_downloaded(self.name)

    def download(self):
        """Will download the package update that was referenced
        with check update.

        Proxy method for :meth:`_patch_update` & :meth:`_full_update`.

        Returns:

            (bool) Meanings:

                True - Download successful

                False - Download failed
        """
        status = False
        if self.name is not None:
            # Tested elsewhere
            if self._is_downloaded(self.name) is True:  # pragma: no cover
                status = True
            else:
                log.info(u'Starting patch download')
                patch_success = self._patch_update(self.name, self.version)
                # Tested elsewhere
                if patch_success:  # pragma: no cover
                    status = True
                    log.info(u'Patch download successful')
                else:
                    log.error(u'Patch update failed')
                    log.info(u'Starting full download')
                    update_success = self._full_update(self.name)
                    if update_success:
                        status = True
                        log.info(u'Full download successful')
                    else:  # Tested elsewhere
                        log.error(u'Full download failed')
        # Removes old versions, of update being checked, from
        # updates folder.  Since we only start patching from
        # the current binary this shouldn't be a problem.
        self._remove_old_updates()
        return status

    def extract(self):
        """Will extract archived update and leave in update folder.
            If updating a lib you can take over from there. If updating
            an app this call should be followed by :meth:`restart` to
            complete update.

            Proxy method for :meth:`_extract_update`.

            Returns:

                (bool) Meanings:

                    True - Install successful

                    False - Install failed
        """
        if jms_utils.system.get_system() == u'win':  # Tested elsewhere
            log.warning('Only supported on Unix like systems')
            return False
        try:
            self._extract_update()
        except ClientError as err:
            log.error(str(err))
            log.debug(str(err), exc_info=True)
            return False
        return True

    def _extract_update(self):
        with jms_utils.paths.ChDir(self.update_folder):
            platform_name = self.name
            if sys.platform == u'win32' and self.name == self.app_name:
                # We only add .exe to app executable.  Not libs or dll
                log.debug(u'Adding .exe to filename for windows main '
                          'app udpate.')
                platform_name += u'.exe'

            latest = get_highest_version(self.name, self.platform,
                                         self.easy_data)
            filename = get_filename(self.name, latest, self.platform,
                                    self.easy_data)
            if not os.path.exists(filename):
                log.error('File does not exists')
                raise ClientError(u'File does not exists')

            log.info(u'Extracting Update')
            archive_ext = os.path.splitext(filename)[1].lower()
            if archive_ext == u'.gz':
                try:
                    with tarfile.open(filename, u'r:gz') as tfile:
                        # Extract file update to current
                        # directory.
                        tfile.extractall()
                except Exception as err:  # pragma: no cover
                    log.error(err)
                    log.debug(str(err), exc_info=True)
                    raise ClientError(u'Error reading gzip file')
            elif archive_ext == u'.zip':
                try:
                    with zipfile.ZipFile(filename, u'r') as zfile:
                        # Extract update file to current
                        # directory.
                        zfile.extractall()
                except Exception as err:  # pragma: no cover
                    log.error(str(err))
                    log.debug(str(err), exc_info=True)
                    raise ClientError(u'Error reading zip file')
            else:
                raise ClientError(u'Unknown filetype')

    def _is_downloaded(self, name):
        latest = get_highest_version(name, self.platform, self.easy_data)

        filename = get_filename(name, latest, self.platform, self.easy_data)

        hash_key = u'{}*{}*{}*{}*{}'.format(self.updates_key, name,
                                            latest, self.platform,
                                            u'file_hash')
        _hash = self.easy_data.get(hash_key)
        with jms_utils.paths.ChDir(self.update_folder):
            if not os.path.exists(filename):
                return False
            with open(filename, u'rb') as f:
                data = f.read()
            if _hash == get_hash(data):
                return True
            else:
                return False

    def _patch_update(self, name, version):  # pragma: no cover
        # Updates the binary by patching
        #
        # Args:
        #    name (str): Name of file to update
        #
        #     version (str): Current version number of file to update
        #
        # Returns:
        #    (bool) Meanings::
        #
        #        True - Either already up to date or patched successful
        #
        #        False - Either failed to patch or no base binary to patch

        log.info(u'Starting patch update')
        filename = get_filename(name, version, self.platform, self.easy_data)
        log.debug('Archive filename: {}'.format(filename))
        if filename is None:
            log.warning(u'Make sure version numbers are correct. '
                        u'Possible TRAP!')
            return False
        latest = get_highest_version(name, self.platform,
                                     self.easy_data)
        # Just checking to see if the zip for the current version is
        # available to patch If not we'll just do a full binary download
        if not os.path.exists(os.path.join(self.update_folder, filename)):
            log.warning(u'{} got deleted. No base binary to start patching '
                        'form'.format(filename))
            return False

        p = Patcher(name=name, json_data=self.json_data,
                    current_version=version, highest_version=latest,
                    update_folder=self.update_folder,
                    update_urls=self.update_urls, verify=self.verify,
                    progress_hooks=self.progress_hooks)

        # Returns True if everything went well
        # If False is returned then we will just do the full
        # update.
        return p.start()

    def _full_update(self, name):
        # Updates the binary by downloading full update
        #
        # Args:
        #    name (str): Name of file to update
        #
        #    version (str): Current version number of file to update
        #
        # Returns:
        #    (bool) Meanings::
        #
        #       True - Update Successful
        #
        #       False - Update Failed
        log.info(u'Starting full update')
        latest = get_highest_version(name, self.platform, self.easy_data)

        filename = get_filename(name, latest, self.platform, self.easy_data)

        hash_key = u'{}*{}*{}*{}*{}'.format(self.updates_key, name,
                                            latest, self.platform,
                                            u'file_hash')
        _hash = self.easy_data.get(hash_key)

        with jms_utils.paths.ChDir(self.update_folder):
            log.info(u'Downloading update...')
            fd = FileDownloader(filename, self.update_urls,
                                _hash, self.verify, self.progress_hooks)
            result = fd.download_verify_write()
            if result:
                log.info(u'Download Complete')
                return True
            else:  # pragma: no cover
                log.error(u'Failed To Download Latest Version')
                return False

    def _remove_old_updates(self):
        # Removes old updates from cache. Patch updates
        # start from currently installed version.

        # ToDo: Better filename comparison
        #       Please chime in if this is sufficient
        #       Will remove todo if so...
        temp = os.listdir(self.update_folder)
        try:
            filename = get_filename(self.name, self.version,
                                    self.platform, self.easy_data)
        except KeyError:  # pragma: no cover
            filename = u'0.0.0'

        if filename is None:
            filename = u'0.0.0'
        try:
            current_version = Version(filename)
            current_version_str = str(current_version)
        except (UtilsError, VersionError):  # pragma: no cover
            log.warning(u'Cannot parse version info')
            current_version = Version('0.0.0')
            current_version_str = str(current_version)
        log.debug('Current verion: {}'.format(current_version_str))
        with jms_utils.paths.ChDir(self.update_folder):
            for t in temp:
                try:
                    t_versoin_str = str(Version((t)))
                except UtilsError:  # pragma: no cover
                    log.warning(u'Cannot parse version info')
                    t_versoin_str = u'0.0.0'
                log.debug('Old version: {}'.format(t_versoin_str))
                t_version = Version(t_versoin_str)
                if self.name in t and t_version < current_version:
                    log.info(u'Removing old update: {}'.format(t))
                    os.remove(t)


class AppUpdate(LibUpdate):
    """Used to update library files used by an application

    Args:

        data (dict): Info dict
    """

    def __init__(self, data):
        super(AppUpdate, self).__init__(data)

    def extract_restart(self):
        """Will extract the update, overwrite the current app,
        then restart the app using the updated binary.

        On windows Proxy method for :meth:`_extract_update` &
        :meth:`_win_overwrite_app_restart`

        On unix Proxy method for :meth:`_extract_update`,
        :meth:`_overwrite_app` & :meth:`_restart`
        """
        try:
            self._extract_update()

            if jms_utils.system.get_system() == u'win':
                self._win_overwrite_app_restart()
            else:
                self._overwrite_app()
                self._restart()
        except ClientError as err:
            log.error(str(err))
            log.debug(str(err), exc_info=True)

    def restart(self):
        """Will overwrite old binary with updated binary and
        restart using the updated binary. Not supported on windows.

        Proxy method for :meth:`_overwrite_app` & :meth:`_restart`.
        """
        if jms_utils.system.get_system() == u'win':
            log.warning(u'Only supported on Unix like systems')
            return
        try:
            self._overwrite_app()
            self._restart()
        except ClientError as err:
            log.error(str(err))
            log.debug(str(err), exc_info=True)

    def _overwrite_app(self):
        # Unix: Overwrites the running applications binary,
        #       then starts the updated binary in the currently
        #       running applications process memory.
        if jms_utils.system.get_system() == u'mac':
            if self.current_app_dir.endswith('MacOS') is True:
                log.debug('Looks like we\'re dealing with a Mac Gui')
                temp_dir = get_mac_dot_app_dir(self.current_app_dir)
                self.current_app_dir = temp_dir

        app_update = os.path.join(self.update_folder, self.name)
        if not os.path.exists(app_update):
            app_update += u'.app'
        log.debug(u'Update Location'
                  ':\n{}'.format(os.path.dirname(app_update)))
        log.debug(u'Update Name: {}'.format(os.path.basename(app_update)))

        current_app = os.path.join(self.current_app_dir, self.name)
        if not os.path.exists(current_app):
            current_app += u'.app'
        log.debug(u'Current App location:\n\n{}'.format(current_app))
        if os.path.exists(current_app):
            if os.path.isfile(current_app):
                os.remove(current_app)
            else:
                shutil.rmtree(current_app, ignore_errors=True)

        log.debug(u'Moving app to new location')
        shutil.move(app_update, os.path.dirname(current_app))

    def _restart(self):
        # Oh yes i did just pull that new binary into
        # the currently running process and kept it pushing
        # like nobody's business. Windows what???
        log.info(u'Restarting')
        current_app = os.path.join(self.current_app_dir, self.name)
        if jms_utils.system.get_system() == u'mac':
            if not os.path.exists(current_app):
                current_app += u'.app'
                mac_app_binary_dir = os.path.join(current_app, u'Contents',
                                                  u'MacOS')
                file_ = os.listdir(mac_app_binary_dir)
                # We are making an assumption here that only 1
                # executable will be in the MacOS folder.
                current_app = os.path.join(mac_app_binary_dir, file_[0])
                log.debug('Mac .app exe path: {}'.format(current_app))

        os.execv(current_app, [self.name])

    def _win_overwrite_app_restart(self):
        # Windows: Moves update to current directory of running
        #          application then restarts application using
        #          new update.
        # Pretty much went through this work to show love to
        # all platforms.  But sheeeeesh!
        exe_name = self.name + u'.exe'
        current_app = os.path.join(self.current_app_dir, exe_name)
        log.debug('Current app location: {}'.format(current_app))
        updated_app = os.path.join(self.update_folder, exe_name)
        log.debug('Update location: {}'.format(updated_app))

        bat = os.path.join(self.current_app_dir, u'update.bat')
        with open(bat, u'w') as batfile:
            batfile.write(u"""
@echo off
echo Updating to latest version...
ping 127.0.0.1 -n 5 -w 1000 > NUL
move /Y "{}" "{}" > NUL
echo restarting...
start "" "{}"
DEL "%~f0"
""".format(updated_app, current_app, current_app))
        log.info(u'Starting update batch file')
        os.startfile(bat)
        sys.exit(0)

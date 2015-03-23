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
from pyupdater import settings, __version__
from pyupdater.client.downloader import FileDownloader
from pyupdater.client.updates import AppUpdate, LibUpdate
from pyupdater.config import PyiUpdaterConfig
from pyupdater.utils import (convert_to_list,
                             EasyAccessDict,
                             get_highest_version,
                             gzip_decompress,
                             lazy_import,
                             Version)


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
def appdirs():
    import appdirs
    return appdirs


@lazy_import
def certifi():
    import certifi
    return certifi


@lazy_import
def ed25519():
    import ed25519
    return ed25519


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.app
    import jms_utils.logger
    import jms_utils.paths
    import jms_utils.system
    return jms_utils


@lazy_import
def six():
    import six
    return six


log = logging.getLogger(__name__)

if os.path.exists(os.path.join(jms_utils.paths.app_cwd, u'pyu.log')):
    ch = logging.FileHandler(os.path.join(jms_utils.paths.app_cwd,
                             u'pyu.log'))
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(jms_utils.logger.log_format_string())
    log.addHandler(ch)
log.debug('Version {}'.format(__version__))


class Client(object):
    """Used on client side to update files

    Kwargs:

        obj (instance): config object

        refresh (bool) Meaning:

            True: Refresh update manifest on object initialization

            False: Don't refresh update manifest on object initialization

        call_back (func): Used for download progress
    """

    def __init__(self, obj=None, refresh=False, call_back=None, test=False):
        self.name = None
        self.version = None
        self.json_data = None
        self.verified = False
        self.ready = False
        self.progress_hooks = []
        if call_back is not None:
            self.progress_hooks.append(call_back)
        if obj is not None:
            self.init_app(obj, refresh, test)

    def init_app(self, obj, refresh=False, test=False):
        """Sets up client with config values from obj

        Args:

            obj (instance): config object

        """
        # Used to add missing required information
        # i.e. APP_NAME
        pyi_config = PyiUpdaterConfig(obj)
        config = pyi_config.copy()

        self.FROZEN = jms_utils.app.FROZEN
        # Grabbing config information
        update_url = config.get(u'UPDATE_URL')
        update_urls = config.get(u'UPDATE_URLS')

        # Here we combine all urls & add trailing / if one isn't present
        self.update_urls = self._sanatize_update_url(update_url, update_urls)
        self.app_name = config.get(u'APP_NAME', u'PyiUpdater')
        self.company_name = config.get(u'COMPANY_NAME', u'Digital Sapphire')
        if test:
            self.data_dir = obj.DATA_DIR
            self.platform = 'mac'
        else:
            self.data_dir = appdirs.user_data_dir(self.app_name,
                                                  self.company_name,
                                                  roaming=True)
            self.platform = jms_utils.system.get_system()
        self.update_folder = os.path.join(self.data_dir,
                                          settings.UPDATE_FOLDER)
        self.public_keys = convert_to_list(config.get(u'PUBLIC_KEYS'),
                                           default=list())
        if len(self.public_keys) == 0:
            log.warning(u'May have passed an incorrect'
                        u'data type to PUBLIC_KEYS')

        # Ensuring only one occurrence of a public key is present
        self.public_keys = list(set(self.public_keys))
        self.verify = config.get(u'VERIFY_SERVER_CERT', True)
        self.version_file = settings.VERSION_FILE

        self._setup()
        if refresh is True:
            self.refresh()

    def refresh(self):
        """Will download and verify your updates version file.

        Proxy method from :meth:`_get_update_manifest`.
        """
        try:
            self._get_update_manifest()
        except Exception as err:
            log.debug(str(err), exc_info=True)
            log.error(str(err))

    def update_check(self, name, version):
        try:
            return self._update_check(name, version)
        except Exception as err:
            log.error('Update check failed: {}'.format(str(err)))
            log.debug(str(err), exc_info=True)
            return None

    def _update_check(self, name, version):
        """
        Will try to patch binary if all check pass.  IE hash verified
        signature verified.  If any check doesn't pass then falls back to
        full update

        Args:

            name (str): Name of file to update

            version (str): Current version number of file to update

        Returns:

            (bool) Meanings:

                True - Update Successful

                False - Update Failed
        """
        self.name = name
        version = Version(version)
        self.version = str(version)

        app = False
        if self.ready is False:
            log.warning('No update manifest found')
            return None
        if self.FROZEN is True and self.name == self.app_name:
            app = True
        # Checking if version file is verified before
        # processing data contained in the version file.
        # This was done by self._get_update_manifest()
        if self.verified is False:
            log.error('Failed version file verification')
            return None
        log.info(u'Checking for {} updates...'.format(name))

        # If None is returned self._get_highest_version could
        # not find the supplied name in the version file
        latest = get_highest_version(name, self.platform,
                                     self.easy_data)
        if latest is None:
            return None
        latest = Version(latest)
        log.debug('Current vesion: {}'.format(str(version)))
        log.debug('Latest version: {}'.format(str(latest)))
        log.debug('Update Truth: {}'.format(latest >= version))
        if latest <= version:
            log.info(u'{} already updated to the latest version'.format(name))
            return None
        # Hey, finally made it to the bottom!
        # Looks like its time to do some updating
        log.info(u'Update available')
        data = {
            u'update_urls': self.update_urls,
            u'name': self.name,
            u'version': self.version,
            u'easy_data': self.easy_data,
            u'json_data': self.json_data,
            u'data_dir': self.data_dir,
            u'platform': self.platform,
            u'app_name': self.app_name,
            u'verify': self.verify,
            u'progress_hooks': self.progress_hooks,
            }
        # Return update object with which handles downloading,
        # extracting updates
        if app is True:
            # AppUpdate objects also has methods to restart
            # the app with the new version
            return AppUpdate(data)
        else:
            return LibUpdate(data)

    def add_call_back(self, cb):
        self.progress_hooks.append(cb)

    # Here we attempt to read the manifest from the filesystem
    # in case of no Internet connection
    def _get_manifest_filesystem(self):
        with jms_utils.paths.ChDir(self.data_dir):
            if not os.path.exists(self.version_file):
                log.warning('No version file on file system')
                return None
            else:
                log.info('Found version file on file system')
                try:
                    with open(self.version_file, u'rb') as f:
                        data = f.read()
                    log.info('Loaded version file from file system')
                except Exception as err:
                    log.error('Failed to load version file from file '
                              u'system')
                    log.debug(str(err), exc_info=True)
                    data = None

                return gzip_decompress(data)

    # Downloading the manifest. If successful also writes it to file-system
    def _download_manifest(self):
        log.info('Downloading online version file')
        try:
            fd = FileDownloader(self.version_file, self.update_urls,
                                verify=self.verify)
            data = fd.download_verify_return()
            try:
                decompressed_data = gzip_decompress(data)
            except IOError:
                log.error('Failed to decompress gzip file')
                raise
            log.info('Version file download successful')
            self._write_manifest_2_filesystem(decompressed_data)
            return decompressed_data
        except Exception as err:
            log.error('Version file download failed')
            log.debug(str(err), exc_info=True)
            return None

    def _write_manifest_2_filesystem(self, data):
        with jms_utils.paths.ChDir(self.data_dir):
            log.debug('Writing version file to disk')
            with gzip.open(self.version_file, u'wb') as f:
                f.write(data)

    def _get_update_manifest(self):
        #  Downloads & Verifies version file signature.
        log.info(u'Loading version file...')

        data = self._download_manifest()
        if data is None:
            data = self._get_manifest_filesystem()

        try:
            log.debug('Data type: {}'.format(type(data)))
            self.json_data = json.loads(data)
            # Ready to check for updates.
            # If json fails to load self.ready will stay false
            # which will cause _update_check to exit early
            self.ready = True
        except ValueError as err:
            log.debug(str(err), exc_info=True)
            log.error(u'Json failed to load: ValueError')
        except Exception as err:
            # Catch all for debugging purposes.
            # If seeing this line come up a lot in debug logs
            # please open an issue on github or submit a pull request
            log.error(str(err))
            log.debug(str(err), exc_info=True)

        # Setting to default dict to not raise any errors
        # in _verify_sig
        if self.json_data is None:
            self.json_data = {}

        self.json_data = self._verify_sig(self.json_data)

        self.easy_data = EasyAccessDict(self.json_data)
        log.debug('Version Data:\n{}'.format(str(self.easy_data)))

    def _verify_sig(self, data):
        # Checking to see if there is a sig in the version file.
        if u'sigs' in data.keys():
            signatures = data[u'sigs']
            log.debug(u'Deleting sigs from update data')
            del data[u'sigs']

            # After removing the signatures we turn the json data back
            # into a string to use as data to verify the sig.
            update_data = json.dumps(data, sort_keys=True)

            # Attempting to verify signature of version file by
            # looping through public keys and testing. If found
            # will break out of the loop
            for pk in self.public_keys:
                log.debug(u'Public Key: {}'.format(pk))
                for s in signatures:
                    log.debug(u'Signature: {}'.format(s))
                    # I added this try/except block because sometimes a
                    # None value in json_data would find its way down here.
                    # Hopefully i fixed it by return right under the Exception
                    # block above.  But just in case will leave anyway.
                    try:
                        pub_key = ed25519.VerifyingKey(pk, encoding='base64')
                        pub_key.verify(s, update_data, encoding='base64')
                    except Exception as err:
                        log.error(str(err))
                    else:
                        log.info(u'Version file verified')
                        self.verified = True
                        break
                if self.verified is True:
                    # No longer need to iterate through public keys
                    break
            else:
                log.warning(u'Version file not verified')

        else:
            log.warning(u'Version file not verified, no signature found')

        return data

    def _setup(self):
        # Sets up required directories on end-users computer
        # to place verified update data
        # Very safe director maker :)
        log.info(u'Setting up directories...')
        dirs = [self.data_dir, self.update_folder]
        for d in dirs:
            if not os.path.exists(d):
                log.info(u'Creating directory: {}'.format(d))
                os.makedirs(d)

    def _sanatize_update_url(self, url, urls):
        _urls = []
        # Making sure final output is a list
        if isinstance(urls, list):
            _urls += urls
        elif isinstance(url, tuple):
            _urls += list(url)
        elif isinstance(urls, six.string_types):
            log.warning(u'UPDATE_URLS value should only be a list.')
            _urls.append(urls)
        else:
            log.warning(u'UPDATE_URLS should be type "{}" got '
                        u'"{}"'.format(type([]), type('')))

        sanatized_urls = []
        # Adds trailing slash to end of url if not already provided.
        # Doing this so when requesting online resources we only
        # need to add the resouce name to the end of the request.
        for u in _urls:
            if not u.endswith(u'/'):
                sanatized_urls.append(u + u'/')
            else:
                sanatized_urls.append(u)
        # Removing duplicates
        return list(set(sanatized_urls))

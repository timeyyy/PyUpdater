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
import sys
import time

from pyupdater.exceptions import UploaderError, UploaderPluginError
from pyupdater import settings
from pyupdater.utils import (lazy_import,
                             remove_dot_files)

log = logging.getLogger(__name__)


@lazy_import
def stevedore():
    import stevedore
    import stevedore.extension
    return stevedore


ns = settings.UPLOAD_PLUGIN_NAMESPACE


class Uploader(object):
    """Uploads updates to configured servers.  SSH, SFTP, S3
    Will automatically pick the correct uploader depending on
    what is configured thorough the config object

    Sets up client with config values from obj

        Args:

            obj (instance): config object
    """
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    # ToDo: Remove in v1.0
    def init_app(self, obj):
        self.init(obj)

    def init(self, obj):
        """Sets up client with config values from obj

        Args:

            obj (instance): config object
        """
        data_dir = obj.get(u'DATA_DIR', os.getcwd())
        self.data_dir = os.path.join(data_dir, settings.USER_DATA_FOLDER)
        self.deploy_dir = os.path.join(self.data_dir, u'deploy')
        self.ssh_remote_dir = obj.get(u'SSH_REMOTE_DIR')
        self.ssh_host = obj.get(u'SSH_HOST')
        self.ssh_username = obj.get(u'SSH_USERNAME')
        self.object_bucket = obj.get(u'OBJECT_BUCKET')
        self.uploader = None
        self.test = False

        # Extension Manager
        self.mgr = stevedore.extension.ExtensionManager(namespace=ns)

    def upload(self):
        """Proxy function that calls the upload method on the received uploader
        Only calls the upload method if an uploader is set.
        """
        if self.uploader is not None:
            self.uploader.deploy_dir = self.deploy_dir
            try:
                self.uploader.upload()
            except Exception as err:  # pragma: no cover
                log.error('Failed to upload: {}'.format(str(err)))
                log.debug(str(err), exc_info=True)
                sys.exit(str(err))
        else:
            raise UploaderError(u'Must call set_uploader first', expected=True)

    def set_uploader(self, requested_uploader):
        """Returns an uploader object. 1 of S3, SCP, SFTP.
        SFTP uploaders not supported at this time.

        Args:

            requested_uploader (string): Either s3 or scp

        Returns:

            object (instance): Uploader object
        """
        if isinstance(requested_uploader, str) is False:
            raise UploaderError(u'Must pass str to set_uploader',
                                expected=True)

        try:
            plugin = self.mgr[requested_uploader]
        except KeyError:
            log.debug(u'EP CACHE: {}'.format(self.mgr.ENTRY_POINT_CACHE))
            raise UploaderPluginError(u'Requested uploader is not installed',
                                      expected=True)
        except Exception as err:  # pragma: no cover
            log.debug(u'EP CACHE: {}'.format(self.mgr.ENTRY_POINT_CACHE))
            log.error(str(err))
            log.debug(str(err), exc_info=True)
            raise UploaderError(u'Requested uploader is not installed',
                                expected=True)

        self.uploader = plugin.plugin()
        msg = u'Requested uploader: {}'.format(requested_uploader)
        log.debug(msg)
        try:
            files = os.listdir(self.deploy_dir)
        except OSError:
            files = []
        files = remove_dot_files(files)
        self.uploader.init(object_bucket=self.object_bucket,
                           ssh_username=self.ssh_username,
                           ssh_remote_dir=self.ssh_remote_dir,
                           ssh_host=self.ssh_host,
                           files=files)


class BaseUploader(object):
    """Base Uploader.  All uploaders should subclass
    this base class
    """
    def __init__(self):
        self.failed_uploads = []
        self.deploy_dir = None

    def init(self, **kwargs):
        """Used to pass file list & any other config options set during
        repo setup.

        Kwargs:

            files (list): List of files to upload

            object_bucket (str): AWS/Dream Objects/Google Storage Bucket

            ssh_remote_dir (str): Full path on remote machine
                                 to place updates

            ssh_username (str): user account of remote server uploads

            ssh_host (str): Remote host to connect to for server uploads
        """
        raise NotImplementedError(u'Must be implemented in subclass.')

    def upload(self):
        """Uploads all files in file_list"""
        self.files_completed = 1
        self.file_count = self._get_filelist_count()
        for f in self.file_list:
            msg = u'\n\nUploading: {}' .format(f)
            msg2 = u' - File {} of {}\n'.format(self.files_completed,
                                                self.file_count)
            print(msg + msg2)
            complete = self.upload_file(f)
            if complete:
                log.debug('{} uploaded successfully'.format(f))
                self.files_completed += 1
            else:
                log.debug(u'{} failed to upload.  will retry'.format(f))
                self.failed_uploads.append(f)
        if len(self.failed_uploads) > 0:
            self._retry_upload()
        if len(self.failed_uploads) < 1:
            print(u"\nUpload Complete")
            time.sleep(3)
            return True
        else:
            print(u'The following files were not uploaded')
            for i in self.failed_uploads:
                log.error(u'{} failed to upload'.format(i))
                print(i)
            return False

    def _retry_upload(self):
        # Takes list of failed downloads and tries to re upload them
        retry = self.failed_uploads[:]
        self.failed_uploads = []
        failed_count = len(retry)
        count = 1
        for f in retry:
            msg = u'\n\nRetyring: {} - File {} of {}\n'.format(f,
                                                               count,
                                                               failed_count)
            print(msg)
            complete = self.upload_file(f)
            if complete:
                log.debug(u'{} uploaded on retry'.format(f))
                count += 1
            else:
                self.failed_uploads.append(f)
        if len(self.failed_uploads) >= 1:
            print(u'\nThe following files failed to upload...')
            for f in self.failed_uploads:
                print(f)
            time.sleep(3)
            return False
        else:
            print('\nUpload complete')
            return True

    def connect(self):
        # Connects to service
        raise NotImplementedError(u'Must be implemented in subclass.')

    def upload_file(self, filename):
        # """Uploads file to remote repository

        # Args:
        #     filename (str): file to upload

        # Returns:
        #     (bool) Meaning::

        #         True - Upload Successful

        #         False - Upload Failed
        # """
        raise NotImplementedError('Must be implemented in subclass.')

    def _get_filelist_count(self):
        return len(self.file_list)

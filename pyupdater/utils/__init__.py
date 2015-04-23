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
import sys

from pyupdater import settings
from pyupdater.utils.exceptions import UtilsError, VersionError

log = logging.getLogger(__name__)


def lazy_import(func):
    """Decorator for declaring a lazy import.

    This decorator turns a function into an object that will act as a lazy
    importer.  Whenever the object's attributes are accessed, the function
    is called and its return value used in place of the object.  So you
    can declare lazy imports like this:

        @lazy_import
        def socket():
            import socket
            return socket

    The name "socket" will then be bound to a transparent object proxy which
    will import the socket module upon first use.

    The syntax here is slightly more verbose than other lazy import recipes,
    but it's designed not to hide the actual "import" statements from tools
    like pyinstaller or grep.
    """
    try:
        f = sys._getframe(1)
    except Exception:  # pragma: no cover
        namespace = None
    else:
        namespace = f.f_locals
    return _LazyImport(func.func_name, func, namespace)


class _LazyImport(object):
    """Class representing a lazy import."""

    def __init__(self, name, loader, namespace=None):
        self._pyiu_lazy_target = _LazyImport
        self._pyiu_lazy_name = name
        self._pyiu_lazy_loader = loader
        self._pyiu_lazy_namespace = namespace

    def _pyiu_lazy_load(self):
        if self._pyiu_lazy_target is _LazyImport:
            self._pyiu_lazy_target = self._pyiu_lazy_loader()
            ns = self._pyiu_lazy_namespace
            if ns is not None:
                try:
                    if ns[self._pyiu_lazy_name] is self:
                        ns[self._pyiu_lazy_name] = self._pyiu_lazy_target
                except KeyError:  # pragma: no cover
                    pass

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if self._pyiu_lazy_target is _LazyImport:
                self._pyiu_lazy_load()
            return getattr(self._pyiu_lazy_target, attr)

    def __nonzero__(self):  # pragma: no cover
        if self._pyiu_lazy_target is _LazyImport:
            self._pyiu_lazy_load()
        return bool(self._pyiu_lazy_target)


@lazy_import
def bz2():
    import bz2
    return bz2


@lazy_import
def getpass():
    import getpass
    return getpass


@lazy_import
def gzip():
    import gzip
    return gzip


@lazy_import
def hashlib():
    import hashlib
    return hashlib


@lazy_import
def os():
    import os
    return os


@lazy_import
def re():
    import re
    return re


@lazy_import
def shutil():
    import shutil
    return shutil


@lazy_import
def StringIO():
    import StringIO
    return StringIO


@lazy_import
def subprocess():
    import subprocess
    return subprocess


@lazy_import
def tarfile():
    import tarfile
    return tarfile


@lazy_import
def time():
    import time
    return time


@lazy_import
def zipfile():
    import zipfile
    return zipfile


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.system
    import jms_utils.terminal
    return jms_utils


@lazy_import
def six():
    import six
    import six.moves
    return six


def check_repo():
    repo = True
    if not os.path.exists(settings.CONFIG_DATA_FOLDER):
        log.warning('PyiUpdater config data folder is missing')
        repo = False
    if repo is False:
        log.error('Not a PyiUpdater repo: must init first.')
        sys.exit(1)


def convert_to_list(data, default=None):
    if isinstance(data, list):
        return data
    if isinstance(data, tuple):
        return list(data)
    if isinstance(data, six.string_types):
        return [data]
    log.debug('Got type: {}'.format(type(data)))
    log.warning(u'Using default value of {}'.format(type(default)))
    return default


def get_filename(name, version, platform, easy_data):
        """Gets full filename for given name & version combo

        Args:

           name (str): name of file to get full filename for

           version (str): version of file to get full filename for

           easy_data (dict): data file to search

        Returns:

           (str) Filename with extension
        """
        filename_key = u'{}*{}*{}*{}*{}'.format(u'updates', name, version,
                                                platform, u'filename')
        filename = easy_data.get(filename_key)

        log.debug(u"Filename for {}-{}: {}".format(name, version, filename))
        return filename


def get_hash(data):
    hash_ = hashlib.sha256(data).hexdigest()
    log.debug(u'Hash for binary data: {}'.format(hash_))
    return hash_


def get_highest_version(name, plat, easy_data):
    """Parses version file and returns the highest version number.

    Args:

       name (str): name of file to search for updates

       easy_data (dict): data file to search

    Returns:

       (str) Highest version number
    """
    version_key = u'{}*{}*{}'.format(u'latest', name, plat)
    version = easy_data.get(version_key)

    if version is not None:
        log.debug(u'Highest version: {}'.format(version))
    else:
        log.error(u'No updates for "{}" on {} exists'.format(name, plat))
    return version


def get_mac_dot_app_dir(directory):
    """Returns parent directory of mac .app

    Args:

       directory (str): Current directory

    Returns:

       (str): Parent directory of mac .app
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(directory)))


def get_package_hashes(filename):
    log.debug(u'Getting package hashes')
    filename = os.path.abspath(filename)
    with open(filename, u'rb') as f:
        data = f.read()

    _hash = hashlib.sha256(data).hexdigest()
    log.debug(u'Hash for file {}: {}'.format(filename, _hash))
    return _hash


def gzip_decompress(data):
    compressed_file = StringIO.StringIO()
    compressed_file.write(data)
    #
    # Set the file's current position to the beginning
    # of the file so that gzip.GzipFile can read
    # its contents from the top.
    #
    compressed_file.seek(0)
    decompressed_file = gzip.GzipFile(fileobj=compressed_file, mode=u'rb')
    data = decompressed_file.read()
    compressed_file.close()
    decompressed_file.close()
    return data


def setup_appname(config):
    if config.APP_NAME is not None:
        default = config.APP_NAME
    else:
        default = None
    config.APP_NAME = jms_utils.terminal.get_correct_answer(u'Please enter '
                                                            u'app name',
                                                            required=True,
                                                            default=default)


def setup_company(config):
    if config.COMPANY_NAME is not None:
        default = config.COMPANY_NAME
    else:
        default = None
    temp = jms_utils.terminal.get_correct_answer(u'Please enter your comp'
                                                 u'any or name',
                                                 required=True,
                                                 default=default)
    config.COMPANY_NAME = temp


def setup_urls(config):
    url = jms_utils.terminal.get_correct_answer(u'Enter a url to ping for '
                                                u'updates.', required=True)
    config.UPDATE_URLS = [url]
    while 1:
        answer = jms_utils.terminal.ask_yes_no(u'Would you like to add '
                                               u'another url for backup?',
                                               default='no')
        if answer is True:
            url = jms_utils.terminal.get_correct_answer(u'Enter another url.',
                                                        required=True)
            config.UPDATE_URLS.append(url)
        else:
            break


def setup_patches(config):
    config.UPDATE_PATCHES = jms_utils.terminal.ask_yes_no(u'Would you like to '
                                                          u'enable patch upda'
                                                          u'tes?',
                                                          default=u'yes')


def setup_scp(config):
    _temp = jms_utils.terminal.get_correct_answer(u'Enter remote dir',
                                                  required=True)
    config.SSH_REMOTE_DIR = _temp
    config.SSH_HOST = jms_utils.terminal.get_correct_answer(u'Enter host',
                                                            required=True)

    config.SSH_USERNAME = jms_utils.terminal.get_correct_answer(u'Enter '
                                                                u'usernmae',
                                                                required=True)


def setup_object_bucket(config):
    _temp = jms_utils.terminal.get_correct_answer(u'Enter bucket name',
                                                  required=True)
    config.OBJECT_BUCKET = _temp


def setup_uploader(config):
    answer1 = jms_utils.terminal.ask_yes_no(u'Would you like to add scp '
                                            u'settings?', default='no')

    answer2 = jms_utils.terminal.ask_yes_no(u'Would you like to add a '
                                            'bucket?', default='no')

    if answer1:
        setup_scp(config)

    if answer2:
        setup_object_bucket(config)


def initial_setup(config):
    setup_appname(config)
    setup_company(config)
    setup_urls(config)
    setup_patches(config)
    setup_uploader(config)
    return config


def repo_update_attr_urls(config):
    "Updates url to new attribute"
    log.info('Checking for deprecated UPDATE_URL')
    if hasattr(config, u'UPDATE_URLS'):
        if config.UPDATE_URLS is None:
            config.UPDATE_URL = []
        if isinstance(config.UPDATE_URLS, tuple):
            config.UPDATE_URLS = list(config.UPDATE_URLS)
        if isinstance(config.UPDATE_URLS, six.string_types):
            config.UPDATE_URLS = [config.UPDATE_URLS]

    if hasattr(config, u'UPDATE_URL'):
        log.info(u'Updating to UPDATE_URLS')
        if isinstance(config.UPDATE_URL, six.string_types):
            config.UPDATE_URLS.append(config.UPDATE_URL)
        if isinstance(config.UPDATE_URL, list):
            config.UPDATE_URLS += config.UPDATE_URL
        if isinstance(config.UPDATE_URL, tuple):
            config.UPDATE_URLS += list(config.UPDATE_URL)
        del config.UPDATE_URL


def repo_update_remove_attr(config):
    "Removes unused attributes"
    log.info(u'Looking for unused attributes')
    upload_settings = False
    if hasattr(config, u'REMOTE_DIR'):
        log.info(u'Deleting REMOTE_DIR')
        del config.REMOTE_DIR
        upload_settings = True
    if hasattr(config, u'HOST'):
        log.info(u'Deleting HOST')
        del config.HOST
        upload_settings = True
    if hasattr(config, u'USERNAME'):
        log.info(u'Deleting USERNAME')
        del config.USERNAME
        upload_settings = True
    if hasattr(config, u'PASSWORD'):
        log.info(u'Deleting PASSWORD')
        del config.PASSWORD
        upload_settings = True
    if hasattr(config, u'DEBUG'):
        log.info(u'Deleting DEBUG')
        del config.DEBUG
    if upload_settings is True:
        log.info(u'Need uploader settings update')
        setup_uploader(config)


def repo_update(config):
    repo_update_attr_urls(config)
    repo_update_remove_attr(config)


def make_archive(name, version, target):
    u"""Used to make archives of file or dir. Zip on windows and tar.gz
    on all other platforms

    Args:
        name - Name of app. Used to create final archive name

        version - Version of app. Used to create final archive name

        target - name of actual target file or dir.

    Returns:
         (str) - name of archive
    """
    file_dir = os.path.dirname(os.path.abspath(target))
    filename = u'{}-{}-{}'.format(name, jms_utils.system.get_system(), version)
    filename_path = os.path.join(file_dir, filename)

    log.debug(u'starting archive')

    ext = os.path.splitext(target)[1]
    temp_file = name + ext

    # Remove file if it exists. Found during testing...
    if os.path.exists(temp_file):
        log.debug('Removing: {}'.format(temp_file))
        if os.path.isdir(temp_file):
            shutil.rmtree(temp_file, ignore_errors=True)
        else:
            os.remove(temp_file)
    if os.path.isfile(target):
        shutil.copy(target, temp_file)
    else:
        shutil.copytree(target, temp_file)
    # Only use zip on windows. Zip doens't preserve file
    # permissions on nix & mac
    if jms_utils.system.get_system() == u'win':
        ext = u'.zip'
        with zipfile.ZipFile(filename_path + u'.zip', u'w') as zf:
            zf.write(target, temp_file)
    else:
        ext = u'.tar.gz'
        if os.path.isfile(target):
            with tarfile.open(filename_path + u'.tar.gz', u'w:gz') as tar:
                tar.add(target, temp_file)
        else:
            shutil.make_archive(filename, u'gztar', file_dir, temp_file)

    if os.path.exists(temp_file):
        log.debug('Removing: {}'.format(temp_file))
        if os.path.isfile(temp_file):
            os.remove(temp_file)
        else:
            shutil.rmtree(temp_file, ignore_errors=True)
    output_filename = filename + ext
    log.debug(u'Archive output filename: {}'.format(output_filename))
    return output_filename


def parse_platform(name):
        try:
            platform_name = re.compile(u'[macnixwr64]{3,5}').findall(name)[0]
            log.debug(u'Platform name is: {}'.format(platform_name))
        except IndexError:
            raise UtilsError('')

        return platform_name


def pretty_time(sec):
    return time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(sec))


def remove_dot_files(files):
        # Removes hidden files from file list
        new_list = []
        for l in files:
            if not l.startswith(u'.'):
                new_list.append(l)
        return new_list


def run(cmd):
    log.debug(u'Command: {}'.format(cmd))
    exit_code = subprocess.call(cmd)
    return exit_code


def _decode_offt(bytes):
    u"""Decode an off_t value from a string.

    This decodes a signed integer into 8 bytes.  I'd prefer some sort of
    signed vint representation, but this is the format used by bsdiff4.
    """
    if sys.version_info[0] < 3:
        bytes = map(ord, bytes)
    x = bytes[7] & 0x7F
    for b in xrange(6, -1, -1):
        x = x * 256 + bytes[b]
    if bytes[7] & 0x80:
        x = -x
    return x


class bsdiff4_py(object):
    u"""Pure-python version of bsdiff4 module that can only patch, not diff.

    By providing a pure-python fallback, we don't force frozen apps to
    bundle the bsdiff module in order to make use of patches.  Besides,
    the patch-applying algorithm is very simple.
    """
    @staticmethod
    def patch(source, patch):  # pragma: no cover
        #  Read the length headers
        l_bcontrol = _decode_offt(patch[8:16])
        l_bdiff = _decode_offt(patch[16:24])
        #  Read the three data blocks
        e_bcontrol = 32 + l_bcontrol
        e_bdiff = e_bcontrol + l_bdiff
        bcontrol = bz2.decompress(patch[32:e_bcontrol])
        bdiff = bz2.decompress(patch[e_bcontrol:e_bdiff])
        bextra = bz2.decompress(patch[e_bdiff:])
        #  Decode the control tuples
        tcontrol = []
        for i in xrange(0, len(bcontrol), 24):
            tcontrol.append((
                _decode_offt(bcontrol[i:i+8]),
                _decode_offt(bcontrol[i+8:i+16]),
                _decode_offt(bcontrol[i+16:i+24]),
            ))
        #  Actually do the patching.
        #  This is the bdiff4 patch algorithm in slow, pure python.
        source = six.BytesIO(source)
        result = six.BytesIO()
        bdiff = six.BytesIO(bdiff)
        bextra = six.BytesIO(bextra)
        for (x, y, z) in tcontrol:
            diff_data = bdiff.read(x)
            orig_data = source.read(x)
            if sys.version_info[0] < 3:
                for i in xrange(len(diff_data)):
                    result.write(chr((ord(diff_data[i]) +
                                 ord(orig_data[i])) % 256))
            else:
                for i in xrange(len(diff_data)):
                    result.write(bytes([(diff_data[i] + orig_data[i]) % 256]))
            result.write(bextra.read(y))
            source.seek(z, os.SEEK_CUR)
        return result.getvalue()


class EasyAccessDict(object):

    def __init__(self, dict_=None, sep=u'*'):
        self.sep = sep
        if not isinstance(dict_, dict):
            log.debug(u'Did not pass dict')
            self.dict = dict()
            log.debug(u'Loading empty dict')
        else:
            self.dict = dict_

    def get(self, key):
        try:
            layers = key.split(self.sep)
            value = self.dict
            for key in layers:
                value = value[key]
            log.debug(u'Found Key')
            return value
        except KeyError:
            log.debug(u'Key Not Found')
            return None
        except Exception as err:  # pragma: no cover
            log.error(str(err), exc_info=True)
            return None

    # Because I always for get call the get method
    def __call__(self, key):
        return self.get(key)

    def __str__(self):
        return str(self.dict)


class Version(object):

    re_2 = re.compile(u'(?P<major>\d+)\.(?P<minor>\d+)(?P<re'
                      u'lease>[b])?(?P<releaseversion>\d+)?')
    re_3 = re.compile(u'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<'
                      u'patch>\d+)(?P<release>[b])?(?P<rele'
                      u'aseversion>\d+)?')
    re_4 = re.compile(u'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<'
                      u'patch>\d+)\.(?P<release>\d+)\.(?P<re'
                      u'leaseversion>\d+)')

    def __init__(self, version):
        self.version_str = version
        self._parse_version_str(version)

    def _parse_version_str(self, version):
        count = self._quick_sanatize(version)
        try:
            if count == 1:
                version_data = self._major_minor_re(version)
            elif count == 2:
                version_data = self._major_minor_patch_re(version)
            else:
                version_data = self._version_re(version)
        except AssertionError:
            raise VersionError('Cannot parse version')

        self.major = int(version_data.get(u'major', 0))
        self.minor = int(version_data.get(u'minor', 0))
        if u'patch' in version_data.keys():
            self.patch = int(version_data.get(u'patch', 0))
        else:
            self.patch = 0
        release = version_data.get('release')
        if release is None:
            self.release = 2
        elif release == u'b':
            self.release = 1
        elif release == u'a':
            self.release = 0
        else:
            try:
                self.release = int(release)
            except ValueError:
                log.debug('Cannot parse release. Setting as stable')
                self.release = 2

        release_version = version_data.get('releaseversion')
        if release_version is None:
            self.release_version = 0
        else:
            self.release_version = int(release_version)
        self.version_tuple = (self.major, self.minor, self.patch,
                              self.release, self.release_version)

    def _major_minor_re(self, version):
        r = self.re_2.search(version)
        assert r is not None
        return r.groupdict()

    def _major_minor_patch_re(self, version):
        r = self.re_3.search(version)
        assert r is not None
        return r.groupdict()

    def _version_re(self, version):
        r = self.re_4.search(version)
        assert r is not None
        return r.groupdict()

    def _quick_sanatize(self, version):
        log.debug('Version str: {}'.format(version))
        ext = os.path.splitext(version)[1]
        # Handle parsing versin from full filenames
        if ext == u'.zip':
            log.debug('Removed ".zip"')
            version = version[:-4]
        elif ext == u'.gz':
            log.debug('Removed ".tar.gz"')
            version = version[:-7]
        count = version.count('.')
        if count not in [1, 2, 4]:
            msg = (u'Incorrect version format. 1, 2 or 4 dots '
                   u'You have {} dots'.format(count))
            log.error(msg)
            raise VersionError(msg)
        return count

    def __str__(self):
        return '.'.join(map(str, self.version_tuple))

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__,
                               self.version_str)

    def __eq__(self, obj):
        if hasattr(obj, 'version_tuple') is False:
            return False
        return self.version_tuple == obj.version_tuple

    def __ne__(self, obj):
        if hasattr(obj, 'version_tuple') is False:
            return False
        return self.version_tuple != obj.version_tuple

    def __lt__(self, obj):
        if hasattr(obj, 'version_tuple') is False:
            return False
        return self.version_tuple < obj.version_tuple

    def __gt__(self, obj):
        if hasattr(obj, 'version_tuple') is False:
            return False
        return self.version_tuple > obj.version_tuple

    def __le__(self, obj):
        if hasattr(obj, 'version_tuple') is False:
            return False
        return self.version_tuple <= obj.version_tuple

    def __ge__(self, obj):
        if hasattr(obj, 'version_tuple') is False:
            return False
        return self.version_tuple >= obj.version_tuple

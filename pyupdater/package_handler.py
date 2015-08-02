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
from __future__ import unicode_literals

import logging
import multiprocessing
import os
import shutil

try:  # pragma: no cover
    import bsdiff4
except ImportError:  # pragma: no cover
    bsdiff4 = None

from pyupdater import settings
from pyupdater.utils import (EasyAccessDict,
                             get_package_hashes as gph,
                             lazy_import,
                             remove_dot_files
                             )
from pyupdater.utils.exceptions import PackageHandlerError
from pyupdater.utils.package import Package, Patch

log = logging.getLogger(__name__)


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.paths
    return jms_utils


class PackageHandler(object):
    """Handles finding, sorting, getting meta-data, moving packages.

    Kwargs:

        app (instance): Config object

        db (dict): Framework metadata
    """

    data_dir = None

    def __init__(self, app=None, db=None):
        self.config_loaded = False
        if app is not None:
            self.init_app(app, db)

    def init_app(self, obj, db):
        """Sets up client with config values from obj

        Args:

            obj (instance): config object

        """
        self.patches = obj.get('UPDATE_PATCHES', True)
        if self.patches:
            log.debug('Patch support enabled')
            self.patch_support = True
        else:
            log.info('Patch support disabled')
            self.patch_support = False
        data_dir = obj.get('DATA_DIR', os.getcwd())
        self.db = db
        self.data_dir = os.path.join(data_dir, settings.USER_DATA_FOLDER)
        self.files_dir = os.path.join(self.data_dir, 'files')
        self.deploy_dir = os.path.join(self.data_dir, 'deploy')
        self.new_dir = os.path.join(self.data_dir, 'new')
        self.config_dir = os.path.join(os.path.dirname(self.data_dir),
                                       settings.CONFIG_DATA_FOLDER)
        self.config = None
        self.json_data = None

        self.setup()

    def setup(self):
        "Creates working directories & loads json files."
        if self.data_dir is not None:
            self._setup()

    def _setup(self):
        self._setup_work_dirs()
        if self.config_loaded is False:
            self.json_data = self._load_version_file()
            self.config = self._load_config()
            self.config_loaded = True

    def process_packages(self):
        """Gets a list of updates to process.  Adds the name of an
        update to the version file if not already present.  Processes
        all packages.  Updates the version file meta-data. Then writes
        version file back to disk.
        """
        if self.data_dir is None:
            raise PackageHandlerError('Must init first.', expected=True)
        package_manifest, patch_manifest = self._get_package_list()
        patches = self._make_patches(patch_manifest)
        self._cleanup(patch_manifest)
        package_manifest = self._add_patches_to_packages(package_manifest,
                                                         patches)
        self.json_data = self._update_version_file(self.json_data,
                                                   package_manifest)
        self._write_json_to_file(self.json_data)
        self._write_config_to_file(self.config)
        self._move_packages(package_manifest)

    def _setup_work_dirs(self):
        # Sets up work dirs on dev machine.  Creates the following folder
        #    - Data dir
        # Then inside the data folder it creates 3 more folders
        #    - New - for new updates that need to be signed
        #    - Deploy - All files ready to upload are placed here.
        #    - Files - All updates are placed here for future reference
        #
        # This is non destructive
        dirs = [self.data_dir, self.new_dir,
                self.deploy_dir, self.files_dir,
                self.config_dir]
        for d in dirs:
            if not os.path.exists(d):
                log.info('Creating dir: {}'.format(d))
                os.mkdir(d)

    def _load_version_file(self):
        # If version file is found its loaded to memory
        # If no version file is found then one is created.
        json_data = self.db.load(settings.CONFIG_DB_KEY_VERSION_META)
        if json_data is None:  # pragma: no cover
            log.warning('Version file not found')
            json_data = {'updates': {}}
            log.info('Created new version file')
        return json_data

    def _load_config(self):
        # Loads config from db if exists.
        # If config doesn't exists create new one
        config = self.db.load(settings.CONFIG_DB_KEY_PY_REPO_CONFIG)
        if config is None:  # pragma: no cover
            log.info('Creating new config file')
            config = {
                'patches': {}
                }
        return config

    def _get_package_list(self, ignore_errors=True):
        # Adds compatible packages to internal package manifest
        # for futher processing
        # Process all packages in new folder and gets
        # url, hash and some outer info.
        log.info('Getting package list')
        # Clears manifest if sign updates runs more the once without
        # app being restarted
        package_manifest = list()
        patch_manifest = list()
        bad_packages = list()
        with jms_utils.paths.ChDir(self.new_dir):
            # Getting a list of all files in the new dir
            packages = os.listdir(os.getcwd())
            for p in packages:
                # On package initialization we do the following
                # 1. Check for a supported archive
                # 2. get required info: version, platform, hash
                # If any check fails package.info['status'] will be False
                # You can query package.info['reason'] for the reason
                package = Package(p)
                if package.info['status'] is False:
                    # Package failed at something
                    # package.info['reason'] will tell why
                    bad_packages.append(package)
                    continue

                # Add package hash
                package.file_hash = gph(package.filename)
                self.json_data = self._update_file_list(self.json_data,
                                                        package)

                package_manifest.append(package)
                self.config = self._add_package_to_config(package,
                                                          self.config)

                if self.patch_support:
                    # Will check if source file for patch exists
                    # if so will return the path and number of patch
                    # to create. If missing source file None returned
                    path = self._check_make_patch(self.json_data,
                                                  package.name,
                                                  package.platform,
                                                  )
                    if path is not None:
                        log.info('Found source file to create patch')
                        patch_name = package.name + '-' + package.platform
                        src_path = path[0]
                        patch_number = path[1]
                        patch_info = dict(src_path=src_path,
                                          dst_path=os.path.abspath(p),
                                          patch_path=os.path.join(self.new_dir,
                                                                  patch_name),
                                          patch_number=patch_number,
                                          patch_name=patch_name)
                        # ready for patching
                        patch_manifest.append(patch_info)
                    else:
                        log.warning('No source file to patch from')

        # ToDo: Expose this & remove "pragma: no cover" once done
        if ignore_errors is False:  # pragma: no cover
            log.warning('Bad package & reason for being naughty:')
            for b in bad_packages:
                log.warning(b.name, b.info['reason'])
        # End ToDo

        return package_manifest, patch_manifest

    def _add_package_to_config(self, p, data):
        if 'package' not in data.keys():
            data['package'] = {}
            log.info('Initilizing config for packages')
        # First package with current name so add platform and version
        if p.name not in data['package'].keys():
            data['package'][p.name] = {p.platform: p.version}
            log.info('Adding new package to config')
        else:
            # Adding platform and version
            if p.platform not in data['package'][p.name].keys():
                data['package'][p.name][p.platform] = p.version
                log.info('Adding new arch to package-config: '
                         '{}'.format(p.platform))
            else:
                # Getting current version for platform
                value = data['package'][p.name][p.platform]
                # Updating version if applicable
                if p.version > value:
                    log.info('Adding new version to package-config')
                    data['package'][p.name][p.platform] = p.version
        return data

    def _cleanup(self, patch_manifest):
        # Remove old archives
        # were previously used to create patches
        if len(patch_manifest) < 1:
            return
        log.info('Cleaning up files directory')
        for p in patch_manifest:
            if os.path.exists(p['src_path']):
                basename = os.path.basename(p['src_path'])
                log.info('Removing {}'.format(basename))
                os.remove(p['src_path'])

    def _make_patches(self, patch_manifest):
        pool_output = list()
        if len(patch_manifest) < 1:
            return pool_output
        log.info('Starting patch creation')
        try:
            cpu_count = multiprocessing.cpu_count() * 2
        except Exception as err:
            log.debug(str(err), exc_info=True)
            log.warning('Cannot get cpu count from os. Using default 2')
            cpu_count = 2

        pool = multiprocessing.Pool(processes=cpu_count)
        pool_output = pool.map(_make_patch, patch_manifest)
        return pool_output

    def _add_patches_to_packages(self, package_manifest, patches):
        # ToDo: Increase the efficiency of this double for
        #       loop. Not sure if it can be done though
        if patches is not None and len(patches) >= 1:
            log.info('Adding patches to package list')
            for p in patches:
                # Not adding patch that are not complete
                if hasattr(p, 'ready') is False:
                    continue
                # Not adding patch that are not complete
                if hasattr(p, 'ready') and p.ready is False:
                    continue
                for pm in package_manifest:
                    #
                    if p.dst_filename == pm.filename:
                        pm.patch_info['patch_name'] = \
                            os.path.basename(p.patch_name)
                        # Don't try to get hash on a ghost file
                        if not os.path.exists(p.patch_name):
                            p_name = ''
                        else:
                            p_name = gph(p.patch_name)
                        pm.patch_info['patch_hash'] = p_name
                        # No need to keep searching
                        # We have the info we need for this patch
                        break
                    else:
                        log.debug('No patch match found')
        else:
            if self.patch_support is True:
                log.warning('No patches found')
        return package_manifest

    def _update_version_file(self, json_data, package_manifest):
        # Updates version file with package meta-data
        log.info('Adding package meta-data to version manifest')
        easy_dict = EasyAccessDict(json_data)
        for p in package_manifest:
            patch_name = p.patch_info.get('patch_name')
            patch_hash = p.patch_info.get('patch_hash')

            # Converting info to format compatible for version file
            info = {'file_hash': p.file_hash,
                    'filename': p.filename}
            if patch_name and patch_hash:
                info['patch_name'] = patch_name
                info['patch_hash'] = patch_hash

            version_key = '{}*{}*{}'.format(settings.UPDATES_KEY,
                                            p.name, p.version)
            version = easy_dict.get(version_key)
            log.debug('Package Info: {}'.format(version))

            if version is None:
                log.debug('Adding new version to file')

                # First version this package name
                json_data[settings.UPDATES_KEY][p.name][p.version] = {}
                platform_key = '{}*{}*{}*{}'.format(settings.UPDATES_KEY,
                                                    p.name, p.version,
                                                    'platform')

                platform = easy_dict.get(platform_key)
                if platform is None:
                    name_ = json_data[settings.UPDATES_KEY][p.name]
                    name_[p.version][p.platform] = info

            else:
                # package already present, adding another version to it
                log.debug('Appending info data to version file')
                json_data[settings.UPDATES_KEY][p.name][p.version][p.platform] = info

            # Will add each individual platform version update
            # to latest.  Now can update platforms independently
            json_data['latest'][p.name][p.platform] = p.version
        return json_data

    def _write_json_to_file(self, json_data):
        # Writes json data to disk
        log.debug('Saving version meta-data')
        self.db.save(settings.CONFIG_DB_KEY_VERSION_META, json_data)

    def _write_config_to_file(self, json_data):
        log.debug('Saving config data')
        self.db.save(settings.CONFIG_DB_KEY_PY_REPO_CONFIG, json_data)

    def _move_packages(self, package_manifest):
        if len(package_manifest) < 1:
            return
        log.info('Moving packages to deploy folder')
        for p in package_manifest:
            patch = p.patch_info.get('patch_name')
            with jms_utils.paths.ChDir(self.new_dir):
                if patch:
                    if os.path.exists(os.path.join(self.deploy_dir, patch)):
                        os.remove(os.path.join(self.deploy_dir, patch))
                    log.debug('Moving {} to {}'.format(patch,
                              self.deploy_dir))
                    if os.path.exists(patch):
                        shutil.move(patch, self.deploy_dir)

                shutil.copy(p.filename, self.deploy_dir)
                log.debug('Copying {} to {}'.format(p.filename,
                          self.deploy_dir))

                if os.path.exists(os.path.join(self.files_dir, p.filename)):
                    os.remove(os.path.join(self.files_dir, p.filename))
                shutil.move(p.filename, self.files_dir)
                log.debug('Moving {} to {}'.format(p.filename,
                          self.files_dir))

    def _update_file_list(self, json_data, package_info):
        files = json_data[settings.UPDATES_KEY]
        latest = json_data.get('latest')
        if latest is None:
            json_data['latest'] = {}
        file_name = files.get(package_info.name)
        if file_name is None:
            log.debug('Adding {} to file list'.format(package_info.name))
            json_data[settings.UPDATES_KEY][package_info.name] = {}

        latest_package = json_data['latest'].get(package_info.name)
        if latest_package is None:
            json_data['latest'][package_info.name] = {}
        return json_data

    def _check_make_patch(self, json_data, name, platform):
        # Check to see if previous version is available to
        # make patch updates
        # Also calculates patch number
        log.info('Looking for bsdiff')
        if bsdiff4 is None:
            log.warning('Bsdiff is missing. Cannot create patches')
            return None
        log.info('Bsdiff found')
        src_file_path = None
        if os.path.exists(self.files_dir):
            with jms_utils.paths.ChDir(self.files_dir):
                files = os.listdir(os.getcwd())

            files = remove_dot_files(files)
            # No src files to patch from. Exit quickly
            if len(files) == 0:
                return None
            # If latest not available in version file. Exit
            try:
                latest = json_data['latest'][name][platform]
            except KeyError:
                return None
            try:
                l_plat = json_data[settings.UPDATES_KEY][name][latest]
                filename = l_plat[platform]['filename']
            except:
                return None
            src_file_path = os.path.join(self.files_dir, filename)

            try:
                patch_num = self.config['patches'][name]
                self.config['patches'][name] += 1
            except KeyError:
                # If no patch number we will start at 100
                try:
                    patch_num = self.config['boot_strap']
                except KeyError:
                    patch_num = 100
                if 'patches' not in self.config.keys():
                    self.config['patches'] = {}
                if name not in self.config['patches'].keys():
                    self.config['patches'][name] = patch_num + 1
            num = patch_num + 1
            log.debug('Patch Number: {}'.format(num))
            return src_file_path, num
        return None


def _make_patch(patch_info):
    # Does with the name implies. Used with multiprocessing
    patch = Patch(patch_info)

    if patch.ready is True:
        log.debug('Patch source path:{}'.format(patch.src_path))
        log.debug('Patch destination path: {}'.format(patch.dst_path))
        log.info("Creating patch... ")
        log.info("Patch name: {}".format(os.path.basename(patch.patch_name)))
        bsdiff4.file_diff(patch.src_path, patch.dst_path, patch.patch_name)
        base_name = os.path.basename(patch.patch_name)
        log.info('Done creating patch... {}'.format(base_name))
    else:
        log.error('Missing patch attr')
    return patch

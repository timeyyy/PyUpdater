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
import shutil
import sys
import time

from pyupdater import settings
from pyupdater.hooks import get_hook_dir
from pyupdater.utils import (check_repo,
                             lazy_import,
                             make_archive,
                             run,
                             Version)

log = logging.getLogger(__name__)


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.paths
    import jms_utils.system
    return jms_utils


class Builder(object):

    def __init__(self, args, pyi_args):
        check_repo()
        self.args = args
        self.pyi_args = pyi_args

    def build(self):
        start = time.time()
        temp_name = jms_utils.system.get_system()
        app_info = self._check_input_file(self.pyi_args)
        self._setup()
        if app_info[u'type'] == u'spec':
            self._build(self.args, app_info[u'name'])
        else:
            self.spec_file_path = os.path.join(self.spec_dir,
                                               temp_name + u'.spec')
            self._make_spec(self.args, self.pyi_args, temp_name, app_info)
            self._build(self.args)
        self._archive(self.args, temp_name)
        finished = time.time() - start
        log.info(u'Build finished in {:.2f} seconds.'.format(finished))

    def make_spec(self):
        temp_name = jms_utils.system.get_system()
        app_info = self._check_input_file(self.pyi_args)
        self._make_spec(self.args, self.pyi_args, temp_name, app_info,
                        spec_only=True)

    def _setup(self):
        self.pyi_dir = os.path.join(os.getcwd(), settings.USER_DATA_FOLDER)
        self.new_dir = os.path.join(self.pyi_dir, u'new')
        self.build_dir = os.path.join(os.getcwd(), settings.CONFIG_DATA_FOLDER)
        self.spec_dir = os.path.join(self.build_dir, u'spec')
        self.work_dir = os.path.join(self.build_dir, u'work')
        for d in [self.build_dir, self.spec_dir, self.work_dir,
                  self.pyi_dir, self.new_dir]:
            if not os.path.exists(d):
                log.debug(u'Creating directory: {}'.format(d))
                os.mkdir(d)

    def _check_input_file(self, pyi_args):
        verified = False
        for p in pyi_args:
            if p.endswith(u'.py'):
                log.debug(u'Building from python source file: {}'.format(p))
                app_info = {u'type': u'script', u'name': p}
                verified = True
                break
            elif p.endswith(u'.spec'):
                log.debug(u'Building from spec file: {}'.format(p))
                app_info = {u'type': u'spec', u'name': p}
                verified = True
                break
        if verified is False:
            log.error(u'Must pass a python script or spec file')
            sys.exit(1)
        return app_info

    def _make_spec(self, args, pyi_args, temp_name, app_info, spec_only=False):
        log.debug('App Info: {}'.format(app_info))

        if args.console is True or args.nowindowed is True \
                or args._console is True:
            if u'-c' not in pyi_args:
                log.debug('Adding -c to pyi args')
                pyi_args.append(u'-c')
        if args.windowed is True or args.noconsole is True \
                or args._windowed is True:
            if u'-w' not in pyi_args:
                log.debug('Adding -w to pyi args')
                pyi_args.append(u'-w')
        pyi_args.append(u'-F')
        pyi_args.append(u'--name={}'.format(temp_name))
        if spec_only is True:
            log.debug('User generated spec file')
            pyi_args.append(u'--specpath={}'.format(os.getcwd()))
        else:
            pyi_args.append(u'--specpath={}'.format(self.spec_dir))
        hook_dir = get_hook_dir()
        log.debug('Hook directory: {}'.format(hook_dir))
        pyi_args.append(u'--additional-hooks-dir={}'.format(hook_dir))
        pyi_args.append(app_info[u'name'])

        cmd = ['pyi-makespec'] + pyi_args
        log.debug('Make spec cmd: {}'.format(' '.join([c for c in cmd])))
        exit_code = run(cmd)
        if exit_code != 0:
            log.error(u'Spec file creation failed with '
                      u'code: {}'.format(exit_code))
            sys.exit(1)
        else:
            log.info(u'Spec file created.')

    def _build(self, args, spec_file_path=None):
        try:
            Version(args.app_version)
        except Exception as err:  # pragma: no cover
            log.debug(str(err), exc_info=True)
            log.error('Version format incorrect')
            log.error(u"""Valid version numbers: 0.10.0, 1.1b, 1.2.1a3

        Visit url for more info:

            http://semver.org/
                      """)
            sys.exit(1)
        build_args = [u'pyinstaller']
        if args.clean is True:
            build_args.append(u'--clean')
        build_args.append(u'--distpath={}'.format(self.new_dir))
        build_args.append(u'--workpath={}'.format(self.work_dir))
        build_args.append(u'-y')
        if spec_file_path is None:
            build_args.append(self.spec_file_path)
        else:
            build_args.append(spec_file_path)

        log.debug('Build cmd: {}'.format(''.join([b for b in build_args])))
        exit_code = run(build_args)
        if exit_code != 0:
            log.error('Build failed with code: {}'.format(exit_code))
            sys.exit(1)
        else:
            log.info('Build successful')

    def _mac_binary_rename(self, temp_name, app_name):
        bin_dir = os.path.join(temp_name, u'Contents', u'MacOS')
        plist = os.path.join(temp_name, u'Contents', u'Info.plist')
        with jms_utils.paths.ChDir(bin_dir):
            # ToDo: Shouldn't be hard coded. Better solution needed
            os.rename(u'mac', app_name)

        with open(plist, u'r') as f:
            plist_data = f.readlines()

        new_plist_data = []
        for d in plist_data:
            if u'mac' in d:
                new_plist_data.append(d.replace(u'mac', app_name))
            else:
                new_plist_data.append(d)

        with open(plist, u'w') as f:
            for d in new_plist_data:
                f.write(d)

    def _archive(self, args, temp_name):
        # Now archive the file
        with jms_utils.paths.ChDir(self.new_dir):
            if os.path.exists(temp_name + u'.app'):
                log.debug(u'Got mac .app')
                app_name = temp_name + u'.app'
                name = args.app_name
                self._mac_binary_rename(app_name, name)
            elif os.path.exists(temp_name + u'.exe'):
                log.debug(u'Got win .exe')
                app_name = temp_name + u'.exe'
                name = args.app_name
            else:
                app_name = temp_name
                name = args.app_name
            version = args.app_version
            log.debug('Temp Name: {}'.format(temp_name))
            log.debug(u'Appname: {}'.format(app_name))
            log.debug('Version: {}'.format(version))

            # Time for some archive creation!
            file_name = make_archive(name, version, app_name)
            log.debug(u'Archive name: {}'.format(file_name))
            if args.keep is False:
                if os.path.exists(temp_name):
                    log.debug('Removing: {}'.format(temp_name))
                    if os.path.isfile(temp_name):
                        os.remove(temp_name)
                    else:
                        shutil.rmtree(temp_name, ignore_errors=True)
                if os.path.exists(app_name):
                    log.debug('Removing: {}'.format(temp_name))
                    if os.path.isfile(app_name):
                        os.remove(app_name)
                    else:
                        shutil.rmtree(app_name, ignore_errors=True)
        log.info(u'{} has been placed in your new folder\n'.format(file_name))

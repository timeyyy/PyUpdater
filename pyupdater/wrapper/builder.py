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
import optparse
import os
import shutil
import sys
import time

from pyupdater import settings
from pyupdater.hooks import get_hook_dir
from pyupdater.utils import (check_repo,
                             lazy_import,
                             make_archive,
                             Version)

from PyInstaller.main import run as pyi_build
from PyInstaller import makespec as _pyi_makespec
from PyInstaller import build as _pyi_build
from PyInstaller import compat as _pyi_compat
from PyInstaller import log as _pyi_log


log = logging.getLogger(__name__)


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.paths
    import jms_utils.system
    return jms_utils


def pyi_makespec(pyi_args):

    def run_makespec(opts, args):
        # Split pathex by using the path separator
        temppaths = opts.pathex[:]
        opts.pathex = []
        for p in temppaths:
            opts.pathex.extend(p.split(os.pathsep))

        spec_file = _pyi_makespec.main(args, **opts.__dict__)
        log.info('wrote %s' % spec_file)

    parser = optparse.OptionParser(
                                   usage=('%prog [opts] <scriptname> '
                                          '[ <scriptname> ...] | <specfile>'))

    _pyi_makespec.__add_options(parser)
    _pyi_build.__add_options(parser)
    _pyi_log.__add_options(parser)
    _pyi_compat.__add_obsolete_options(parser)

    opts, args = parser.parse_args(pyi_args)
    _pyi_log.__process_options(parser, opts)

    run_makespec(opts, args)


class Builder(object):
    """Wrapper for Pyinstaller with some extras. After building
    executable with pyinstaller, Builder will create an archive
    of the executable.

    Args:

        args (list): Args specific to PyUpdater

        pyi_args (list): Args specific to Pyinstaller
    """

    def __init__(self, args, pyi_args):
        check_repo()
        self.args = args
        self.pyi_args = pyi_args

    # Creates & archives executable
    def build(self):
        start = time.time()
        temp_name = jms_utils.system.get_system()
        # Check for spec file or python script
        app_info = self._check_input_file(self.pyi_args)
        self._setup()
        spec_file_path = os.path.join(self.spec_dir, temp_name + '.spec')

        # Spec file used instead of python script
        if app_info['type'] == 'spec':
            spec_file_path = app_info['name']
        else:
            # Creating spec file from script
            self._make_spec(self.args, self.pyi_args, temp_name, app_info)

        # Build executable
        self._build(self.args, spec_file_path)
        # Archive executable
        self._archive(self.args, temp_name)
        finished = time.time() - start
        log.info('Build finished in {:.2f} seconds.'.format(finished))

    def make_spec(self):
        temp_name = jms_utils.system.get_system()
        app_info = self._check_input_file(self.pyi_args)
        self._make_spec(self.args, self.pyi_args, temp_name, app_info,
                        spec_only=True)

    def _setup(self):
        # Create required directories
        self.pyi_dir = os.path.join(os.getcwd(), settings.USER_DATA_FOLDER)
        self.new_dir = os.path.join(self.pyi_dir, 'new')
        self.build_dir = os.path.join(os.getcwd(), settings.CONFIG_DATA_FOLDER)
        self.spec_dir = os.path.join(self.build_dir, 'spec')
        self.work_dir = os.path.join(self.build_dir, 'work')
        for d in [self.build_dir, self.spec_dir, self.work_dir,
                  self.pyi_dir, self.new_dir]:
            if not os.path.exists(d):
                log.debug('Creating directory: {}'.format(d))
                os.mkdir(d)

    # Ensure that a spec file or python script is present
    def _check_input_file(self, pyi_args):
        verified = False
        for p in pyi_args:
            if p.endswith('.py'):
                log.debug('Building from python source file: {}'.format(p))
                app_info = {'type': 'script', 'name': p}
                verified = True
                break
            elif p.endswith('.spec'):
                log.debug('Building from spec file: {}'.format(p))
                app_info = {'type': 'spec', 'name': p}
                verified = True
                break
        if verified is False:
            log.error('Must pass a python script or spec file')
            sys.exit(1)
        return app_info

    # Take args from PyUpdater then sanatize & combine to be
    # passed to pyinstaller
    def _make_spec(self, args, spec_args, temp_name,
                   app_info, spec_only=False):
        log.debug('App Info: {}'.format(app_info))

        if args.console is True:
            if '-c' not in spec_args:
                log.debug('Adding -c to pyi args')
                spec_args.append('-c')
        if args.windowed is True:
            if '-w' not in spec_args:
                log.debug('Adding -w to pyi args')
                spec_args.append('-w')
        # Ensure that onefile mode is passed
        spec_args.append('-F')
        spec_args.append('--name={}'.format(temp_name))
        if spec_only is True:
            log.debug('User generated spec file')
            spec_args.append('--specpath={}'.format(os.getcwd()))
        else:
            # Place spec file in .pyupdater/spec
            spec_args.append('--specpath={}'.format(self.spec_dir))
        # Use hooks included in PyUpdater package
        hook_dir = get_hook_dir()
        log.debug('Hook directory: {}'.format(hook_dir))
        spec_args.append('--additional-hooks-dir={}'.format(hook_dir))
        spec_args.append(app_info['name'])

        log.debug('Make spec cmd: {}'.format(' '.join([c for c in spec_args])))
        pyi_makespec(spec_args)

    # Actually creates executable from spec file
    def _build(self, args, spec_file_path):
        try:
            Version(args.app_version)
        except Exception as err:  # pragma: no cover
            log.debug(str(err), exc_info=True)
            log.error('Version format incorrect')
            log.error("""Valid version numbers: 0.10.0, 1.1b, 1.2.1a3

        Visit url for more info:

            http://semver.org/
                      """)
            sys.exit(1)
        build_args = []
        if args.clean is True:
            build_args.append('--clean')
        build_args.append('--distpath={}'.format(self.new_dir))
        build_args.append('--workpath={}'.format(self.work_dir))
        build_args.append('-y')
        build_args.append(spec_file_path)

        log.debug('Build cmd: {}'.format(''.join([b for b in build_args])))
        build_args = [str(x) for x in build_args]
        pyi_build(build_args)

    # Updates name of binary from mac to applications name
    def _mac_binary_rename(self, temp_name, app_name):
        bin_dir = os.path.join(temp_name, 'Contents', 'MacOS')
        plist = os.path.join(temp_name, 'Contents', 'Info.plist')
        with jms_utils.paths.ChDir(bin_dir):
            # ToDo: Shouldn't be hard coded. Better solution needed
            os.rename('mac', app_name)

        # We also have to update to ensure app launches correctly
        with open(plist, 'r') as f:
            plist_data = f.readlines()

        new_plist_data = []
        for d in plist_data:
            if 'mac' in d:
                new_plist_data.append(d.replace('mac', app_name))
            else:
                new_plist_data.append(d)

        with open(plist, 'w') as f:
            for d in new_plist_data:
                f.write(d)

    # Creates zip on windows and gzip on other platforms
    def _archive(self, args, temp_name):
        # Now archive the file
        with jms_utils.paths.ChDir(self.new_dir):
            if os.path.exists(temp_name + '.app'):
                log.debug('Got mac .app')
                app_name = temp_name + '.app'
                name = args.app_name
                self._mac_binary_rename(app_name, name)
            elif os.path.exists(temp_name + '.exe'):
                log.debug('Got win .exe')
                app_name = temp_name + '.exe'
                name = args.app_name
            else:
                app_name = temp_name
                name = args.app_name
            version = args.app_version
            log.debug('Temp Name: {}'.format(temp_name))
            log.debug('Appname: {}'.format(app_name))
            log.debug('Version: {}'.format(version))

            # Time for some archive creation!
            file_name = make_archive(name, version, app_name)
            log.debug('Archive name: {}'.format(file_name))
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
        log.info('{} has been placed in your new folder\n'.format(file_name))

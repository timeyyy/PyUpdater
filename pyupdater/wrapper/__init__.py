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
import tarfile

from appdirs import user_log_dir
from jms_utils.logger import log_formatter
from jms_utils.paths import ChDir
from jms_utils.terminal import ask_yes_no
import stevedore


from pyupdater import PyiUpdater, __version__
from pyupdater import settings
from pyupdater.config import Loader, SetupConfig
from pyupdater.exceptions import UploaderError, UploaderPluginError
from pyupdater.storage import Storage
from pyupdater.utils import (check_repo,
                             initial_setup,
                             pretty_time,
                             repo_update,
                             setup_appname,
                             setup_company,
                             setup_urls,
                             setup_patches,
                             setup_scp,
                             setup_object_bucket)
from pyupdater.wrapper.builder import Builder
from pyupdater.wrapper.options import get_parser


CWD = os.getcwd()
log = logging.getLogger()
if os.path.exists(os.path.join(CWD, u'pyu.log')):  # pragma: no cover
    fh = logging.FileHandler(os.path.join(CWD, u'pyu.log'))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(log_formatter())
    log.addHandler(fh)

fmt = logging.Formatter('[%(levelname)s] %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
# sh.setLevel(logging.DEBUG)
sh.setLevel(logging.INFO)
log.addHandler(sh)

db = Storage()
loader = Loader(db)
LOG_DIR = user_log_dir(settings.APP_NAME, settings.APP_AUTHOR)


def clean(args):  # pragma: no cover
    if args.yes is True:
        _clean()

    else:
        answer = ask_yes_no(u'Are you sure you want to remove '
                            u'pyupdater data?', default=u'no')
        if answer is True:
            _clean()
        else:
            log.info(u'Clean canceled.')


def _clean():
    cleaned = False
    if os.path.exists(settings.CONFIG_DATA_FOLDER):
        cleaned = True
        shutil.rmtree(settings.CONFIG_DATA_FOLDER, ignore_errors=True)
        log.info(u'Removed {} folder'.format(settings.CONFIG_DATA_FOLDER))
    if os.path.exists(settings.USER_DATA_FOLDER):
        cleaned = True
        shutil.rmtree(settings.USER_DATA_FOLDER, ignore_errors=True)
        log.info(u'Removed {} folder'.format(settings.USER_DATA_FOLDER))
    if cleaned is True:
        log.info(u'Clean complete...')
    else:
        log.info(u'Nothing to clean...')


def init(args):  # pragma: no cover
    count = args.count
    if count > 10:
        sys.exit(u'Cannot be more then 10')
    if not os.path.exists(os.path.join(settings.CONFIG_DATA_FOLDER,
                          settings.CONFIG_FILE_USER)):
        config = initial_setup(SetupConfig())
        log.info(u'Creating pyu-data dir...')
        pyiu = PyiUpdater(config, db)
        pyiu.setup()
        log.info(u'Making signing keys...')
        pyiu.make_keys(count)
        config.PUBLIC_KEYS = pyiu.get_public_keys()
        loader.save_config(config)
        log.info(u'Setup complete')
    else:
        sys.exit(u'Not an empty PyiUpdater repository')


def keys(args):  # pragma: no cover
    check_repo()
    config = loader.load_config()
    pyiu = PyiUpdater(config, db)
    if args.revoke is not None:
        count = args.revoke
        pyiu.revoke_key(count)
        config.PUBLIC_KEYS = pyiu.get_public_keys()
        key = pyiu.get_recent_revoked_key()
        if key is not None:
            log.info('* Most Recent Revoked Key *')
            log.info('Created: {}'.format(pretty_time(key[u'date'])))
            log.info('Type: {}'.format(key[u'key_type']))
            log.info('Public Key: {}'.format(key[u'public']))
            if args.private is True:
                log.info('Private Key: {}'.format(key[u'private']))
            else:
                log.info(u'Private Key: * Next time to show private key '
                         u'use --show-private *')
    loader.save_config(config)


def _log(args):  # pragma: no cover
    log.info(u'Starting log export')
    og_dir = CWD
    with ChDir(LOG_DIR):
        files = []
        temp_files = os.listdir(CWD)
        log.info(u'Collecting logs')
        for t in temp_files:
            if t.startswith(settings.LOG_FILENAME_DEBUG):
                log.debug('Adding {} to log'.format(t))
                files.append(t)
        log.info(u'Found all logs')
        t = tarfile.open(settings.DEBUG_ARCHIVE, u'w:bz2')
        log.info(u'Compressing logs')
        for f in files:
            log.debug(u'Archiving {}'.format(f))
            t.add(f)
        t.close()
        log.info(u'Log compression complete')
        old_log_zip = os.path.join(og_dir, settings.DEBUG_ARCHIVE)
        if os.path.exists(old_log_zip):
            os.remove(old_log_zip)
        shutil.move(settings.DEBUG_ARCHIVE, og_dir)
    log.info(u'Log export complete')


def pkg(args):  # pragma: no cover
    check_repo()
    pyiu = PyiUpdater(loader.load_config(), db)
    if args.process is False and args.sign is False:
        sys.exit(u'You must specify a command')

    if args.process is True:
        log.info(u'Processing packages...')
        pyiu.process_packages()
        log.info(u'Processing packages complete')
    if args.sign is True:
        log.info(u'Signing packages...')
        pyiu.sign_update()
        log.info(u'Signing packages complete')


def update(args):  # pragma: no cover
    check_repo()
    log.info('Starting repo update')
    config = loader.load_config()
    repo_update(config)
    loader.save_config(config)
    log.info('Reconfig complete')


def setter(args):  # pragma: no cover
    check_repo()
    config = loader.load_config()
    if args.appname is True:
        setup_appname(config)
    if args.company is True:
        setup_company(config)
    if args.urls is True:
        setup_urls(config)
    if args.patches is True:
        setup_patches(config)
    if args.scp is True:
        setup_scp(config)
    if args.s3 is True:
        setup_object_bucket(config)
    loader.save_config(config)
    log.info(u'Settings update complete')


def upload(args):  # pragma: no cover
    check_repo()
    upload_service = args.service
    if upload_service is None:
        log.error('Must provide service name')
        sys.exit(1)

    pyiu = PyiUpdater(loader.load_config(), db)

    try:
        pyiu.set_uploader(upload_service)
    except UploaderError as err:
        log.error(str(err))
        sys.exit(1)
    except UploaderPluginError as err:
        log.debug(str(err))
        mgr = stevedore.ExtensionManager(settings.UPLOAD_PLUGIN_NAMESPACE)
        plugin_names = mgr.names()
        log.debug(u'Plugin names: {}'.format(plugin_names))
        if len(plugin_names) == 0:
            msg = (u'*** No upload plugins instaled! ***\nYou can install the '
                   u'aws s3 plugin with\n$ pip install pyiupdater[s3]\n\nOr '
                   u'the scp plugin with\n$ pip install pyiupdater[scp]')
        else:
            msg = (u'Invalid Uploader\n\nAvailable options:\n'
                   u'{}'.format(' '.join(plugin_names)))
        log.error(msg)
        sys.exit(1)
    try:
        pyiu.upload()
    except Exception as e:
        msg = (u'Looks like you forgot to add USERNAME '
               'and/or REMOTE_DIR')
        log.debug(str(e), exc_info=True)
        log.error(msg)
        sys.exit(1)


def _real_main(args):  # pragma: no cover
    if args is None:
        args = sys.argv[1:]
    parser = get_parser()
    args, pyi_args = parser.parse_known_args(args)
    cmd = args.command
    if cmd == u'build':
        check_repo()
        builder = Builder(args, pyi_args)
        builder.build()
    elif cmd == u'clean':
        clean(args)
        return True
    elif cmd == u'init':
        init(args)
    elif cmd == u'keys':
        keys(args)
    elif cmd == u'log':
        _log(args)
    elif cmd == u'make-spec':
        check_repo()
        builder = Builder(args, pyi_args)
        builder.make_spec()
    elif cmd == u'pkg':
        pkg(args)
    elif cmd == u'settings':
        setter(args)
    elif cmd == u'update':
        update(args)
    elif cmd == u'upload':
        upload(args)
    elif cmd == u'version':
        print('PyiUpdater {}'.format(__version__))
    else:
        log.error(u'Not Implemented')
        sys.exit(1)


def main(args=None):  # pragma: no cover
    exit = 0
    clean = None
    try:
        clean = _real_main(args)
    except KeyboardInterrupt:
        print(u'\n')
        msg = u'Exited by user'
        log.warning(msg)
        exit = 1
    except Exception as err:
        exit = 1
        log.debug(str(err), exc_info=True)
        log.error(str(err))
    if clean is None:
        db._sync_db()
    sys.exit(exit)

if __name__ == u'__main__':  # pragma: no cover
    args = sys.argv[1:]
    main(args)

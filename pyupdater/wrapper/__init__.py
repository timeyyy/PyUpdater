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

import json
import logging
import os
import shutil
import sys
import warnings

from appdirs import user_log_dir
from jms_utils.logger import log_formatter
from jms_utils.paths import ChDir
from jms_utils.terminal import ask_yes_no
import requests
import stevedore


from pyupdater import PyUpdater, __version__
from pyupdater import settings
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
from pyupdater.utils.config import Loader, SetupConfig
from pyupdater.utils.exceptions import UploaderError, UploaderPluginError
from pyupdater.utils.storage import Storage
from pyupdater.wrapper.builder import Builder
from pyupdater.wrapper.options import get_parser


CWD = os.getcwd()
log = logging.getLogger()
if os.path.exists(os.path.join(CWD, 'pyu.log')):  # pragma: no cover
    fh = logging.FileHandler(os.path.join(CWD, 'pyu.log'))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(log_formatter())
    log.addHandler(fh)

fmt = logging.Formatter('[%(levelname)s] %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)

# Used for Development
# sh.setLevel(logging.DEBUG)

sh.setLevel(logging.INFO)
log.addHandler(sh)

LOG_DIR = user_log_dir(settings.APP_NAME, settings.APP_AUTHOR)
log_file = os.path.join(LOG_DIR, settings.LOG_FILENAME_DEBUG)
rfh = logging.handlers.RotatingFileHandler(log_file, maxBytes=35000,
                                           backupCount=2)
rfh.setFormatter(log_formatter())
rfh.setLevel(logging.DEBUG)
log.addHandler(rfh)


def _build(args, pyi_args):
    check_repo()
    builder = Builder(args, pyi_args)
    builder.build()


# Get permission before deleting PyUpdater repo
def clean(args):  # pragma: no cover
    if args.yes is True:
        _clean()

    else:
        answer = ask_yes_no('Are you sure you want to remove '
                            'pyupdater data?', default='no')
        if answer is True:
            _clean()
        else:
            log.info('Clean aborted!')


# Remove all traces of PyUpdater
def _clean():
    cleaned = False
    if os.path.exists(settings.CONFIG_DATA_FOLDER):
        cleaned = True
        shutil.rmtree(settings.CONFIG_DATA_FOLDER, ignore_errors=True)
        log.info('Removed {} folder'.format(settings.CONFIG_DATA_FOLDER))
    if os.path.exists(settings.USER_DATA_FOLDER):
        cleaned = True
        shutil.rmtree(settings.USER_DATA_FOLDER, ignore_errors=True)
        log.info('Removed {} folder'.format(settings.USER_DATA_FOLDER))
    if cleaned is True:
        log.info('Clean complete...')
    else:
        log.info('Nothing to clean...')


# Initialize PyUpdater repo
def init(args):  # pragma: no cover
    db = Storage()
    loader = Loader(db)
    count = args.count
    if count > 10:
        sys.exit('Cannot be more then 10')
    if not os.path.exists(os.path.join(settings.CONFIG_DATA_FOLDER,
                          settings.CONFIG_FILE_USER)):
        config = initial_setup(SetupConfig())
        log.info('Creating pyu-data dir...')
        pyu = PyUpdater(config, db)
        pyu.setup()
        log.info('Making signing keys...')
        pyu.make_keys(count)
        config.PUBLIC_KEYS = pyu.get_public_keys()
        loader.save_config(config)
        log.info('Setup complete')
        db._sync_db()
    else:
        sys.exit('Not an empty PyUpdater repository')


def keys(args):  # pragma: no cover
    if args.yes is True:
        _keys(args)

    else:
        answer = ask_yes_no('Are you sure you want to revoke?',
                            default='no')
        if answer is True:
            _keys(args)
        else:
            log.info('Revoke aborted!')


# Revokes keys
def _keys(args):  # pragma: no cover
    check_repo()
    db = Storage()
    loader = Loader(db)
    config = loader.load_config()
    pyu = PyUpdater(config, db)
    if args.count is not None:
        count = args.count
        pyu.revoke_key(count)
        config.PUBLIC_KEYS = pyu.get_public_keys()
        key = pyu.get_recent_revoked_key()
        if key is not None:
            log.info('* Most Recent Revoked Key *')
            log.info('Created: {}'.format(pretty_time(key['date'])))
            log.info('Type: {}'.format(key['key_type']))
            log.info('Public Key: {}'.format(key['public']))
            if args.private is True:
                log.info('Private Key: {}'.format(key['private']))
            else:
                log.info('Private Key: * Next time to show private key '
                         'use --show-private *')
        loader.save_config(config)
        db._sync_db()


def _make_spec(args, pyi_args):
    check_repo()
    builder = Builder(args, pyi_args)
    builder.make_spec()


def pkg(args):
    check_repo()
    db = Storage()
    loader = Loader(db)
    pyu = PyUpdater(loader.load_config(), db)
    if args.process is False and args.sign is False:
        sys.exit('You must specify a command')

    if args.process is True:
        log.info('Processing packages...')
        pyu.process_packages()
        log.info('Processing packages complete')
    if args.sign is True:
        log.info('Signing packages...')
        pyu.sign_update()
        log.info('Signing packages complete')
    db._sync_db()


def _setting(args):  # pragma: no cover
    check_repo()
    db = Storage()
    loader = Loader(db)
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
    log.info('Settings update complete')
    db._sync_db()


def upload_debug_info(args):  # pragma: no cover
    log.info('Starting log export')

    def _add_file(payload, filename):
        with open(filename, 'r') as f:
            data = f.read()
        payload['files'][filename] = {'content': data}

    def _upload(data):
        log.debug(json.dumps(data, indent=2))
        api = 'https://api.github.com/'
        gist_url = api + 'gists'
        headers = {"Accept": "application/vnd.github.v3+json"}
        r = requests.post(gist_url, headers=headers, data=json.dumps(data))
        try:
            url = r.json()['html_url']
        except Exception as err:
            log.debug(str(err), exc_info=True)
            log.debug(json.dumps(r.json(), indent=2))
            url = None
        return url

    upload_data = {'files': {}}
    with ChDir(LOG_DIR):
        temp_files = os.listdir(os.getcwd())
        if len(temp_files) == 0:
            log.info('No log files to collect')
            return
        log.info('Collecting logs')
        for t in temp_files:
            if t.startswith(settings.LOG_FILENAME_DEBUG):
                log.debug('Adding {} to log'.format(t))
                _add_file(upload_data, t)
        log.info('Found all logs')
        url = _upload(upload_data)
    if url is None:
        log.error('Could not upload debug info to github')
    else:
        log.info('Log export complete')
        log.info(url)


def update(args):  # pragma: no cover
    check_repo()
    db = Storage()
    loader = Loader(db)
    log.info('Starting repo update')
    config = loader.load_config()
    repo_update(config)
    loader.save_config(config)
    log.info('Reconfig complete')
    db._sync_db()


def upload(args):  # pragma: no cover
    error = False
    check_repo()
    db = Storage()
    loader = Loader(db)
    upload_service = args.service
    if upload_service is None:
        log.error('Must provide service name')
        error = True

    if error is False:
        pyu = PyUpdater(loader.load_config(), db)
        try:
            pyu.set_uploader(upload_service)
        except UploaderError as err:
            log.error(str(err))
            error = True
        except UploaderPluginError as err:
            log.debug(str(err))
            error = True
            mgr = stevedore.ExtensionManager(settings.UPLOAD_PLUGIN_NAMESPACE)
            plugin_names = mgr.names()
            log.debug('Plugin names: {}'.format(plugin_names))
            if len(plugin_names) == 0:
                msg = ('*** No upload plugins instaled! ***\nYou can install '
                       'the aws s3 plugin with\n$ pip install PyUpdater'
                       '[s3]\n\nOr the scp plugin with\n$ pip install '
                       'PyUpdater[scp]')
            else:
                msg = ('Invalid Uploader\n\nAvailable options:\n'
                       '{}'.format(' '.join(plugin_names)))
            log.error(msg)
    if error is False:
        try:
            pyu.upload()
        except Exception as e:
            msg = ('Looks like you forgot to add USERNAME '
                   'and/or REMOTE_DIR')
            log.debug(str(e), exc_info=True)
            log.error(msg)
    db._sync_db()


def _real_main(args):  # pragma: no cover
    if args is None:
        args = sys.argv[1:]
    parser = get_parser()
    args, pyi_args = parser.parse_known_args(args)
    cmd = args.command
    if cmd == 'build':
        _build(args, pyi_args)
    elif cmd == 'clean':
        clean(args)
    elif cmd == 'init':
        init(args)
    elif cmd == 'keys':
        keys(args)
    # ToDo: Remove in v1.0
    elif cmd == 'log':
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn('Use "collect-debug-info" ', DeprecationWarning)
        upload_debug_info(args)
    # End to do
    elif cmd == 'collect-debug-info':
        upload_debug_info(args)
    elif cmd == 'make-spec':
        _make_spec(args, pyi_args)
    elif cmd == 'pkg':
        pkg(args)
    elif cmd == 'settings':
        _setting(args)
    elif cmd == 'update':
        update(args)
    elif cmd == 'upload':
        upload(args)
    elif cmd == 'version':
        print('PyUpdater {}'.format(__version__))
    else:
        log.error('Not Implemented')
        sys.exit(1)


def main(args=None):  # pragma: no cover
    try:
        _real_main(args)
    except KeyboardInterrupt:
        print('\n')
        msg = 'Exited by user'
        log.warning(msg)
    except Exception as err:
        log.debug(str(err), exc_info=True)
        log.error(str(err))

if __name__ == '__main__':  # pragma: no cover
    args = sys.argv[1:]
    main(args)

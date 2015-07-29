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
import argparse


def make_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s ')
    return parser


def make_subparser(parser):
    subparsers = parser.add_subparsers(help='commands', dest='command')
    return subparsers


def _build_make_spec_commom(subparser):
    # Start of args override
    # start a clean build
    subparser.add_argument('--clean', help='Clean build. '
                           'Bypass the cache', action="store_true")

    # This will be set to the pyu-data/new directory.
    # When we make the final compressed archive we will look
    # for an exe in that dir.
    subparser.add_argument('-o', '--distpath', help=argparse.SUPPRESS)

    # Will be set to .pyupdater/spec/
    # Trying to keep root dir clean
    subparser.add_argument('--specpath', help=argparse.SUPPRESS)

    # Will be set to .pyupdater/build
    # Trying to keep root dir clean
    subparser.add_argument('--workpath', help=argparse.SUPPRESS)

    # Will be set to platform name i.e. mac, win, nix, nix64, arm\
    # When archiving we will change the name to the value passed to
    # --app-name
    subparser.add_argument('-n', '--name', help=argparse.SUPPRESS)

    # Just capturing these argument.
    # PyUpdater only supports onefile mode at the moment
    subparser.add_argument('-D', '--onedir', action="store_true",
                           help=argparse.SUPPRESS)

    # Just capturing these argument.
    # Will be added later to pyinstaller build command
    subparser.add_argument('-F', '--onefile', action="store_true",
                           help=argparse.SUPPRESS)

    # Just capturing these arguments
    subparser.add_argument('-c', '--console', '--nowindowed',
                           action="store_true", dest='console')

    subparser.add_argument('-w', '--windowed', '--noconsole',
                           action="store_true", help=argparse.SUPPRESS,
                           dest='windowed')

    # Potentially harmful for cygwin on windows
    # ToDo: Maybe do a check for cygwin and disable if cygwin is true
    subparser.add_argument('-s', '--strip', action="store_true",
                           help=argparse.SUPPRESS)
    # End of args override

    # Used by PyiWrapper
    subparser.add_argument('--app-name', dest="app_name", required=True)
    subparser.add_argument('--app-version', dest="app_version",
                           required=True)
    subparser.add_argument('-k', '--keep', dest='keep', action='store_true',
                           help='Won\'t delete update after archiving')


def add_build_parser(subparsers):
    build_parser = subparsers.add_parser('build', help='compiles script '
                                         'or spec file',
                                         usage='%(prog)s <script> [opts]')
    _build_make_spec_commom(build_parser)


def add_make_spec_parser(subparsers):
    make_spec_parser = subparsers.add_parser('make-spec', help='Creates '
                                             'spec file',
                                             usage='%(prog)s <script> '
                                             '[opts]')
    _build_make_spec_commom(make_spec_parser)


def add_clean_parser(subparsers):
    clean_parser = subparsers.add_parser('clean',
                                         help='* WARNING * removes all '
                                         'traces of pyupdater')
    clean_parser.add_argument('-y', '--yes', help='Confirms removal of '
                              'pyu-data & .pyupdater folder',
                              action='store_true')


def add_init_parser(subparsers):
    init_parser = subparsers.add_parser('init', help='initializes a '
                                        'src directory')
    init_parser.add_argument('-c', '--count', help='How many key pairs to '
                             'create. The more keys the better your chances '
                             'are of not having an app lose its ability to '
                             'self update. Default 3',
                             type=int, default=3)


def add_keys_parser(subparsers):
    keys_parser = subparsers.add_parser('keys', help='Manage signing keys')
    keys_parser.add_argument('-c', '--count', help='Revokes oldest signing '
                             'key & adds the same amount of new good key '
                             'pairs to keys db. Verson file will no longer '
                             'be signed by revoked keys. Default 1',
                             type=int, default=1)
    keys_parser.add_argument('--show-private', help='Prints private key to '
                             'console when revoking',
                             action='store_true', dest='private')
    keys_parser.add_argument('-y', '--yes', help='Confirms revoking of key(s)',
                             action='store_true')


def add_debug_parser(subparsers):
    log_parser = subparsers.add_parser('collect-debug-info',
                                       help='Upload debug logs to github '
                                       'gist and return url.')
    log_parser.add_argument('--dummy', help=argparse.SUPPRESS)


def add_package_parser(subparsers):
    package_parser = subparsers.add_parser('pkg', help='Manages creation of '
                                           'file metadata & signing')
    package_parser.add_argument('-P', '--process',
                                help='Adds update metadata to version file',
                                action='store_true', dest='process')

    package_parser.add_argument('-S', '--sign', help='Sign version file',
                                action='store_true', dest='sign')


def add_settings_parser(subparsers):
    settings_parser = subparsers.add_parser('settings', help='Updated '
                                            'config settings')
    settings_parser.add_argument('--app-name',
                                 help='Change app name * Use with Caution *',
                                 action='store_true', dest='appname')
    settings_parser.add_argument('--company',
                                 help='Change company name',
                                 action='store_true')
    settings_parser.add_argument('--urls', help='Change update urls',
                                 action='store_true')
    settings_parser.add_argument('--patches', help='Changed patch support',
                                 action='store_true')
    settings_parser.add_argument('--scp', help='Changed scp settings',
                                 action='store_true')
    settings_parser.add_argument('--s3', help='Changed s3 settings',
                                 action='store_true')


def add_update_parser(subparsers):
    update_parser = subparsers.add_parser('update', help='Updates repo. '
                                          'Should be ran after you update '
                                          'pyupdater')
    update_parser.add_argument('--dummy', help=argparse.SUPPRESS)


def add_upload_parser(subparsers):
    upload_parser = subparsers.add_parser('upload', help='Uploads files')
    upload_parser.add_argument('-s', '--service', help='Where '
                               'updates are stored', dest='service')


def add_version_parser(subparsers):
    version_parser = subparsers.add_parser('version', help='Show version')
    version_parser.add_argument('--dummy', help=argparse.SUPPRESS)


def get_parser():
    parser = make_parser()
    subparsers = make_subparser(parser)
    add_build_parser(subparsers)
    add_clean_parser(subparsers)
    add_debug_parser(subparsers)
    add_init_parser(subparsers)
    add_keys_parser(subparsers)
    add_make_spec_parser(subparsers)
    add_package_parser(subparsers)
    add_settings_parser(subparsers)
    add_update_parser(subparsers)
    add_upload_parser(subparsers)
    add_version_parser(subparsers)
    return parser

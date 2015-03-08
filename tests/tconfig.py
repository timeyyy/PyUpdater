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
import os


class TConfig(object):
    bad_attr = u'bad attr'
    # If left None "Not_So_TUF" will be used
    APP_NAME = u'jms'

    # Directory for updater to place verified updates.
    # If left blank will be place in the users home
    # directory Unix ".Not_So_TUF"
    # windows "Not_So_Tuf"
    APP_DATA_DIR = os.path.join(u'app_data')

    COMPANY_NAME = u'JMS LLC'

    DATA_DIR = None

    # Public Key used by your app to verify update data
    # REQUIRED
    PUBLIC_KEYS = ['yuUGTdPXaQfcv8enzVZrJKrAgyxrU+Bs1vQGlZziGVs']

    # Online repository where you host your packages
    # and version file
    # REQUIRED
    UPDATE_URLS = [u'https://s3-us-west-1.amazonaws.com/pyi-test/']
    UPDATE_PATCHES = True

    # Upload Setup
    REMOTE_DIR = None
    HOST = None

    # server user name/access key id
    USERNAME = None
    # Path to ssh key of server / password / secret access key
    PASSWORD = u'/path/to/ssh/key file'

    VERIFY_SERVER_CERT = True

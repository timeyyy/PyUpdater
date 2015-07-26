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


class TConfig(object):
    bad_attr = 'bad attr'
    # If left None "Not_So_TUF" will be used
    APP_NAME = 'jms'

    COMPANY_NAME = 'JMS LLC'

    DATA_DIR = None

    # Public Key used by your app to verify update data
    # REQUIRED
    PUBLIC_KEYS = ['iBFNlFxQZ17n3SakBmF2fI6dZhrbkdf5GtP9m/wVrTQ',
                   'zj1LPcRgx5I3GcxUHlLtltMAdo8v0P1rCMMZEqZeB9',
                   'QIRqZkFmavnQz4U55kOMIEJQqEx3cWCek0zCTSATb14']

    # Online repository where you host your packages
    # and version file
    # REQUIRED
    UPDATE_URLS = ['https://s3-us-west-1.amazonaws.com/pyupdater-test/']
    UPDATE_PATCHES = True

    # Upload Setup
    REMOTE_DIR = None
    HOST = None

    # server user name/access key id
    USERNAME = None
    # Path to ssh key of server / password / secret access key
    PASSWORD = '/path/to/ssh/key file'

    VERIFY_SERVER_CERT = True

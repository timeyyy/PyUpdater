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
import json
import os

import ed25519
import pytest

pub_key_file = os.path.abspath(os.path.join(u'tests', u'test data',
                               u'jms.pub'))
version_file = os.path.abspath(os.path.join(u'tests', u'test data',
                               u'version.json'))


@pytest.mark.usefixtures('cleandir')
class TestVersionFile(object):

    def test_signature(self):
        with open(version_file, u'r') as f:
            version_data = json.loads(f.read())

        sig = version_data[u'sig']
        del version_data[u'sig']
        version_data = json.dumps(version_data, sort_keys=True)

        with open(pub_key_file, u'r') as pkf:
            public_key = ed25519.VerifyingKey(pkf.read(), encoding='base64')

        public_key.verify(sig, version_data, encoding='base64')

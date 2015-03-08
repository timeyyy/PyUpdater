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
import shutil
import urllib2

import pytest

from pyi_updater.client.patcher import Patcher

TEST_DATA_DIR = os.path.join(os.getcwd(), 'tests', 'test data',
                             'patcher-test-data')

version_file_url = 'https://s3-us-west-1.amazonaws.com/pyi-test/version.json'
json_data = json.loads(urllib2.urlopen(version_file_url).read())

update_data = {
    u'name': u'jms',
    u'json_data': json_data,
    u'current_version': u'0.0.1',
    u'highest_version': u'0.0.3',
    u'update_folder': None,
    u'update_urls': [u'https://s3-us-west-1.amazonaws.com/pyi-test/'],
    u'platform': u'mac',
    }


@pytest.mark.usefixtures("cleandir")
class TestPatcher(object):

    @pytest.fixture
    def setup(self):
        directory = os.getcwd()
        base_binary = os.path.join(TEST_DATA_DIR, u'jms-mac-0.0.1.zip')
        shutil.copy(base_binary, directory)
        return directory

    def test_no_base_binary(self):
        assert os.listdir(os.getcwd()) == []
        data = update_data.copy()
        data[u'update_folder'] = os.getcwd()
        p = Patcher(**data)
        assert p.start() is False

    def test_bad_hash_current_version(self, setup):
        data = update_data.copy()
        data[u'update_folder'] = setup
        data['current_file_hash'] = u'Thisisabadhash'
        p = Patcher(**data)
        assert p.start() is False

    def test_missing_version(self, setup):
        data = update_data.copy()
        data[u'update_folder'] = setup
        data[u'highest_version'] = u'0.0.4'
        p = Patcher(**data)
        assert p.start() is False

    def test_execution(self, setup):
        data = update_data.copy()
        data[u'update_folder'] = setup
        p = Patcher(**data)
        assert p.start() is True

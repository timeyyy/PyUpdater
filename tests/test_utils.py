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

import pytest

from pyupdater.utils import (check_repo,
                             convert_to_list,
                             EasyAccessDict,
                             get_hash,
                             get_mac_dot_app_dir,
                             get_package_hashes,
                             Version
                             )
from pyupdater.utils.exceptions import VersionError


@pytest.mark.usefixtures('cleandir')
class TestUtils(object):

    @pytest.fixture()
    def hasher(self):
        with open('hash-test.txt', 'w') as f:
            f.write('I should find some lorem text' * 123)
        return None

    def test_check_repo_fail(self):
        with pytest.raises(SystemExit):
            check_repo()

    def test_convert_to_list(self):
        assert isinstance(convert_to_list(u'test'), list)
        assert isinstance(convert_to_list((u'test', u'test2')), list)
        assert isinstance(convert_to_list([u'test']), list)

    def test_convert_to_list_default(self):
        assert isinstance(convert_to_list({}, default=[]), list)

    def test_package_hash(self, hasher):
        digest = (u'cb44ec613a594f3b20e46b768c5ee780e0a9b66ac'
                  u'6d5ac1468ca4d3635c4aa9b')
        assert digest == get_package_hashes('hash-test.txt')

    def test_get_hash(self):
        digest = (u'380fd2bf3d78bb411e4c1801ce3ce7804bf5a22d79'
                  u'405d950e5d5c8f3169fca0')
        assert digest == get_hash('Get this hash please')

    def test_get_mac_app_dir(self):
        main = u'Main'
        path = os.path.join(main, u'Contents', u'MacOS', u'app')
        assert get_mac_dot_app_dir(path) == main

    def test_easy_access_dict(self):
        good_data = {'test': True}
        easy = EasyAccessDict()
        assert easy('bad-key') is None
        good_easy = EasyAccessDict(good_data)
        assert good_easy.get('test') is True
        assert good_easy.get('no-test') is None

    def test_version(self):
        v1 = Version('1.1b1')
        v2 = Version('1.1')
        assert v2 > v1
        v3 = Version('1.2.1b1')
        v4 = Version('1.2.1')
        assert v3 < v4
        with pytest.raises(VersionError):
            Version('1')

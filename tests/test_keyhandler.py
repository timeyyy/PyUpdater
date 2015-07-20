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

import os

import pytest

from pyupdater.utils.storage import Storage
from pyupdater.utils.keydb import KeyDB
db = Storage()


# @pytest.mark.usefixtures("cleandir")
# class TestKeyDB(object):

#     def test_add(self):
#         keydb = KeyDB(db, load=True)
#         assert len(os.listdir(os.getcwd())) == 1
#         keydb.add_key('public1', 'private1')
#         keydb.add_key('public2', 'private2')
#         assert len(keydb.get_public_keys()) == 2
#         assert keydb.get_public_keys()[0] == 'public1'
#         assert keydb.get_public_keys()[1] == 'public2'

#     def test_get_revoked_key(self):
#         keydb = KeyDB(db, load=True)
#         assert len(os.listdir(os.getcwd())) == 1
#         assert keydb.get_revoked_key() is None
#         keydb.add_key('public1', 'private1')
#         keydb.add_key('public2', 'private2')
#         assert len(keydb.get_public_keys()) == 2
#         keydb.revoke_key(count=2)
#         assert len(keydb.get_public_keys()) == 0

#     def test_revoking_break(self):
#         keydb = KeyDB(db, load=False)
#         assert len(os.listdir(os.getcwd())) == 1
#         keydb.add_key('public1', 'private1')
#         keydb.add_key('public2', 'private2')
#         assert keydb.get_revoked_key() is None
#         assert len(keydb.get_public_keys()) == 2
#         keydb.revoke_key(count=1)
#         assert len(keydb.get_public_keys()) == 1
#         assert keydb.get_revoked_key()['public'] == 'public1'

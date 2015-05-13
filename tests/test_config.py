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
from pyupdater.utils.config import PyUpdaterConfig


class DevConfig(object):
    TESTING = True
    TEST_LOVE = True
    MORE_INFO = u'No Thanks'
    Bad_Attr = True


class ProdConfig(object):
    TESTING = False
    DEBUG = False
    MORE_INFO = u'Yes Please'


class BasicCofig(object):
    APP_NAME = u'Tester'


def test_dev_config():
    config = PyUpdaterConfig()
    test_config = DevConfig()
    config.from_object(test_config)
    assert config[u'TESTING'] is True


def test_dev_config_bad_attr():
    config = PyUpdaterConfig()
    test_config = DevConfig()
    config.from_object(test_config)
    assert config.get(u'BAD_ATTR', None) is None


def test_prod_config():
    config = PyUpdaterConfig()
    prod_config = ProdConfig()
    config.from_object(prod_config)
    assert config[u'MORE_INFO'] == u'Yes Please'


def test_prod_bad_atter():
    config = PyUpdaterConfig()
    prod_config = ProdConfig()
    config.from_object(prod_config)
    assert config.get(u'DEBUG', None) is not None


def test_config_str():
    config = PyUpdaterConfig()
    config.from_object(BasicCofig())
    assert repr(config) == u"<PyUpdaterConfig {'APP_NAME': u'Tester'}>"

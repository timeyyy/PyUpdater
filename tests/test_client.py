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
from __future__ import print_function
from __future__ import unicode_literals

import json
import os
import shutil
import time

from jms_utils.system import get_system
from jms_utils.paths import ChDir
import pytest

from pyupdater.client import Client
from tconfig import TConfig


@pytest.mark.usefixtures("cleandir", "client")
class TestSetup(object):

    def test_data_dir(self, client):
        assert os.path.exists(client.data_dir)

    def test_new_init(self, client):
        assert client.app_name == 'jms'
        assert client.update_urls[0] == ('https://s3-us-west-1.amazon'
                                         'aws.com/pyupdater-test/')

    def test_no_cert(self, client):
        client.verify = False
        assert client.app_name == 'jms'
        assert client.update_urls[0] == ('https://s3-us-west-1.amazon'
                                         'aws.com/pyupdater-test/')

    def test_bad_pub_key(self, client):
        t_config = TConfig()
        t_config.PUBLIC_KEYS = ['bad key']
        t_config.DATA_DIR = os.getcwd()
        client = Client(t_config, refresh=True, test=True)
        assert client.update_check('jms', '0.0.0') is None

    def test_check_version(self, client):
        assert client.update_check(client.app_name, '6.0.0') is None
        assert client.update_check(client.app_name, '0.0.2') is not None
        client.ready = False
        assert client.update_check(client.app_name, '0.0.2') is None

    def test_callback(self):
        def cb(status):
            print(status)

        def cb2(status):
            raise IndexError

        t_config = TConfig()
        t_config.PUBLIC_KEYS = ['bad key']
        t_config.DATA_DIR = os.getcwd()
        client = Client(t_config, refresh=True, test=True, call_back=cb,
                        callbacks=[cb, cb2])
        client.add_call_back(cb2)
        assert client.update_check('jms', '0.0.0') is None

    def test_manifest_filesystem(self):
        t_config = TConfig()
        t_config.PUBLIC_KEYS = ['bad key']
        t_config.DATA_DIR = os.getcwd()
        client = Client(t_config, refresh=True, test=True)
        filesystem_data = client._get_manifest_filesystem()
        filesystem_data = json.loads(filesystem_data)
        del filesystem_data['sigs']
        assert client.json_data == filesystem_data

    def test_url_str_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URL = 'http://acme.com/update'
        client = Client(t_config, refresh=True, test=True)
        assert isinstance(client.update_urls, list)

    def test_url_list_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URL = ['http://acme.com/update']
        client = Client(t_config, refresh=True, test=True)
        assert isinstance(client.update_urls, list)

    def test_url_tuple_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URL = ('http://acme.com/update')
        client = Client(t_config, refresh=True, test=True)
        assert isinstance(client.update_urls, list)

    def test_urls_str_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = 'http://acme.com/update'
        client = Client(t_config, refresh=True, test=True)
        assert isinstance(client.update_urls, list)

    def test_urls_list_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = ['http://acme.com/update']
        client = Client(t_config, refresh=True, test=True)
        assert isinstance(client.update_urls, list)

    def test_urls_tuple_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = ('http://acme.com/update')
        client = Client(t_config, refresh=True, test=True)
        assert isinstance(client.update_urls, list)


@pytest.mark.usefixtures("cleandir", "client")
class TestDownload(object):

    def test_failed_refresh(self, client):
        client = Client(None, refresh=True, test=True)
        client.data_dir = os.getcwd()
        assert client.ready is False

    def test_https(self, client):
        update = client.update_check(client.app_name, '0.0.1')
        assert update is not None
        assert update.app_name == 'jms'
        temp_name = update.name
        update.name = None
        assert update.is_downloaded() is False
        update.name = temp_name
        assert update.is_downloaded() is False
        assert update.download() is True
        assert update.is_downloaded() is True
        if get_system() != 'win':
            assert update.extract() is True

    def test_async_https(self, client):
        update = client.update_check(client.app_name, '0.0.1')
        assert update is not None
        assert update.app_name == 'jms'
        temp_name = update.name
        update.name = None
        assert update.is_downloaded() is False
        update.name = temp_name
        assert update.is_downloaded() is False
        update.download(async=True)
        count = 0
        while count < 61:
            if update.is_downloaded() is True:
                break
            time.sleep(1)
            count += 1
        assert update.is_downloaded() is True

        if get_system() != 'win':
            assert update.extract() is True

    def test_http(client):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.VERIFY_SERVER_CERT = False
        client = Client(t_config, refresh=True, test=True)
        update = client.update_check(client.app_name, '0.0.1')
        assert update is not None
        assert update.app_name == 'jms'
        assert update.download() is True
        assert update.is_downloaded() is True

    def test_async_http(client):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.VERIFY_SERVER_CERT = False
        client = Client(t_config, refresh=True, test=True)
        update = client.update_check(client.app_name, '0.0.1')
        assert update is not None
        assert update.app_name == 'jms'
        update.download(async=True)
        count = 0
        while count < 61:
            if update.is_downloaded() is True:
                break
            time.sleep(1)
            count += 1
        assert update.is_downloaded() is True

    def test_multipule_async_calls(client):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.VERIFY_SERVER_CERT = False
        client = Client(t_config, refresh=True, test=True)
        update = client.update_check(client.app_name, '0.0.1')
        assert update is not None
        assert update.app_name == 'jms'
        update.download(async=True)
        count = 0
        assert update.download(async=True) is None
        assert update.download() is None
        while count < 61:
            if update.is_downloaded() is True:
                break
            time.sleep(1)
            count += 1
        assert update.is_downloaded() is True


@pytest.mark.usefixtures("cleandir", "client")
class TestExtract(object):

    def test_extract(self, client):
        update = client.update_check('jms', '0.0.1')
        assert update is not None
        assert update.download() is True
        if get_system() != 'win':
            assert update.extract() is True

    def test_extract_no_file(self, client):
        update = client.update_check('jms', '0.0.1')
        assert update is not None
        assert update.download() is True
        with ChDir(update.update_folder):
            files = os.listdir(os.getcwd())
            for f in files:
                if os.path.isfile(f):
                    os.remove(f)
                else:
                    shutil.rmtree(f, ignore_errors=True)
        if get_system() != 'win':
            assert update.extract() is False

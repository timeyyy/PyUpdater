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
from jms_utils.paths import ChDir
from jms_utils.system import get_system

from pyupdater import PyiUpdater
from pyupdater.config import Loader, PyiUpdaterConfig
from pyupdater.wrapper.builder import Builder
from pyupdater.wrapper.options import get_parser
from tconfig import TConfig

cmd = [u'build', u'--app-name', u'myapp', u'--app-version',
       u'0.1.0', u'app.py', u'-F']
cmd2 = [u'build', u'--app-name', u'myapp', u'--app-version',
        u'0.1.1', u'app.py', u'-F']


@pytest.mark.usefixtures('cleandir')
class TestPyiUpdater(object):

    @pytest.fixture
    def pyi(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        pyi = PyiUpdater(t_config)
        return pyi

    def test_dev_dir_none(self):
        updater = PyiUpdaterConfig()
        myconfig = TConfig()
        myconfig.APP_NAME = None
        updater.update_config(myconfig)
        assert updater[u'APP_NAME'] == u'PyUpdater App'

    def test_setup(self):
        data_dir = os.getcwd()
        pyu_data_dir = os.path.join(data_dir, u'pyu-data')
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        pyi = PyiUpdater(t_config)
        pyi.setup()
        assert os.path.exists(pyu_data_dir)
        assert os.path.exists(os.path.join(pyu_data_dir, u'deploy'))
        assert os.path.exists(os.path.join(pyu_data_dir, u'files'))
        assert os.path.exists(os.path.join(pyu_data_dir, u'new'))

    def test_execution(self, pyi):
        archive_name = u'myapp-{}-0.1.0.tar.gz'.format(get_system())
        parser = get_parser()
        data_dir = pyi.config[u'DATA_DIR']
        pyu_data_dir = os.path.join(data_dir, u'pyu-data')
        pyi.setup()
        pyi.make_keys(3)
        with ChDir(data_dir):
            loader = Loader()
            loader.save_config(pyi.config.copy())
            with open(u'app.py', u'w') as f:
                f.write('print "Hello World"')
            args, pyi_args = parser.parse_known_args(cmd)
            b = Builder(args, pyi_args)
            b.build()

        assert os.path.exists(os.path.join(pyu_data_dir, u'new',
                              archive_name))
        pyi.process_packages()
        assert os.path.exists(os.path.join(pyu_data_dir, u'deploy',
                              archive_name))
        assert os.path.exists(os.path.join(pyu_data_dir, u'files',
                              archive_name))
        pyi.sign_update()
        assert os.path.exists(os.path.join(pyu_data_dir, u'deploy',
                              'versions.gz'))
        assert os.path.exists(os.path.join(pyu_data_dir, u'deploy',
                              'version.json'))

    def test_execution_patch(self, pyi):
        archive_name = u'myapp-{}-0.1.1.tar.gz'.format(get_system())
        parser = get_parser()
        data_dir = pyi.config[u'DATA_DIR']
        pyu_data_dir = os.path.join(data_dir, u'pyu-data')
        pyi.setup()
        pyi.make_keys(3)
        with ChDir(data_dir):
            loader = Loader()
            loader.save_config(pyi.config.copy())
            with open(u'app.py', u'w') as f:
                f.write('print "Hello World"')
            args, pyi_args = parser.parse_known_args(cmd)
            b = Builder(args, pyi_args)
            b.build()
            pyi.process_packages()

            args, pyi_args = parser.parse_known_args(cmd2)
            b = Builder(args, pyi_args)
            b.build()
            pyi.process_packages()
            pyi.sign_update()
        files = os.listdir(os.path.join(pyu_data_dir, u'deploy'))
        assert len(files) == 5
        assert os.path.exists(os.path.join(pyu_data_dir, u'deploy',
                              archive_name))
        assert os.path.exists(os.path.join(pyu_data_dir, u'files',
                              archive_name))

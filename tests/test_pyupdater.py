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

from pyupdater import PyUpdater
from pyupdater.utils.config import Loader, PyUpdaterConfig
from pyupdater.wrapper.builder import Builder
from pyupdater.wrapper.options import get_parser
from tconfig import TConfig


def create_build_cmd(version):
    cmd = ['build', '--app-name', 'myapp', '--app-version',
           '0.1.{}'.format(version), 'app.py', '-F']
    return cmd

if get_system() == 'win':
    ext = '.zip'
else:
    ext = '.tar.gz'


@pytest.mark.usefixtures('cleandir', 'db', 'pyu')
class TestPyUpdater(object):

    def test_dev_dir_none(self):
        updater = PyUpdaterConfig()
        myconfig = TConfig()
        myconfig.APP_NAME = None
        updater.update_config(myconfig)
        assert updater['APP_NAME'] == 'PyUpdater App'

    def test_setup(self):
        data_dir = os.getcwd()
        pyu_data_dir = os.path.join(data_dir, 'pyu-data')
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        pyu = PyUpdater(t_config)
        pyu.setup()
        assert os.path.exists(pyu_data_dir)
        assert os.path.exists(os.path.join(pyu_data_dir, 'deploy'))
        assert os.path.exists(os.path.join(pyu_data_dir, 'files'))
        assert os.path.exists(os.path.join(pyu_data_dir, 'new'))

    def test_execution(self, pyu, db):
        archive_name = 'myapp-{}-0.1.0{}'.format(get_system(), ext)
        parser = get_parser()
        data_dir = pyu.config['DATA_DIR']
        pyu_data_dir = os.path.join(data_dir, 'pyu-data')
        pyu.setup()
        pyu.make_keys(3)
        with ChDir(data_dir):
            loader = Loader(db)
            loader.save_config(pyu.config.copy())
            with open('app.py', 'w') as f:
                f.write('print "Hello World"')
            args, pyu_args = parser.parse_known_args(create_build_cmd(0))
            b = Builder(args, pyu_args)
            b.build()

        assert os.path.exists(os.path.join(pyu_data_dir, 'new',
                              archive_name))
        pyu.process_packages()
        assert os.path.exists(os.path.join(pyu_data_dir, 'deploy',
                              archive_name))
        assert os.path.exists(os.path.join(pyu_data_dir, 'files',
                              archive_name))
        pyu.sign_update()
        assert os.path.exists(os.path.join(pyu_data_dir, 'deploy',
                              'versions.gz'))

    def test_execution_patch(self, pyu, db):
        archive_name = 'myapp-{}-0.1.1{}'.format(get_system(), ext)
        parser = get_parser()
        data_dir = pyu.config['DATA_DIR']
        pyu_data_dir = os.path.join(data_dir, 'pyu-data')
        pyu.setup()
        pyu.make_keys(3)
        with ChDir(data_dir):
            loader = Loader(db)
            loader.save_config(pyu.config.copy())
            with open('app.py', 'w') as f:
                f.write('print "Hello World"')
            args, pyu_args = parser.parse_known_args(create_build_cmd(1))
            b = Builder(args, pyu_args)
            b.build()
            pyu.process_packages()
            pyu.sign_update()

            args, pyu_args = parser.parse_known_args(create_build_cmd(2))
            b = Builder(args, pyu_args)
            b.build()
            pyu.process_packages()
            pyu.sign_update()

            args, pyu_args = parser.parse_known_args(create_build_cmd(3))
            b = Builder(args, pyu_args)
            b.build()
            pyu.process_packages()
            pyu.sign_update()
        files = os.listdir(os.path.join(pyu_data_dir, 'deploy'))
        assert len(files) == 6
        assert os.path.exists(os.path.join(pyu_data_dir, 'deploy',
                              archive_name))
        assert os.path.exists(os.path.join(pyu_data_dir, 'files',
                              archive_name))

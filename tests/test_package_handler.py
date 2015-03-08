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

from pyupdater import settings
from pyupdater.config import PyiUpdaterConfig
from pyupdater.exceptions import PackageHandlerError
from pyupdater.package_handler import PackageHandler
from tconfig import TConfig

s_dir = settings.USER_DATA_FOLDER


@pytest.mark.usefixtures(u'cleandir')
class TestPackageHanlder(object):

    def test_init(self):
        data_dir = os.getcwd()
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        config = PyiUpdaterConfig(t_config)
        p = PackageHandler(config)
        assert p.files_dir == os.path.join(data_dir, s_dir, u'files')
        assert p.deploy_dir == os.path.join(data_dir, s_dir, u'deploy')

    def test_no_patch_support(self):
        data_dir = os.getcwd()
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        t_config.UPDATE_PATCHES = False
        config = PyiUpdaterConfig(t_config)
        p = PackageHandler(config)
        p.process_packages()

    def test_process_packages(self):
        data_dir = os.getcwd()
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        t_config.UPDATE_PATCHES = False
        config = PyiUpdaterConfig(t_config)
        p = PackageHandler(config)
        p.process_packages()

    def test_process_packages_fail(self):
        with pytest.raises(PackageHandlerError):
            p = PackageHandler()
            p.process_packages()

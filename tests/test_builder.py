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

from jms_utils.paths import ChDir
from jms_utils.system import get_system
import pytest

from pyupdater import PyUpdater
from pyupdater.wrapper.builder import Builder
from pyupdater.wrapper.options import get_parser
from tconfig import TConfig


@pytest.mark.usefixtures('cleandir')
class TestBuilder(object):

    def test_no_repo(self):
        with pytest.raises(SystemExit):
            b = Builder(list(), dict())
            b.build()

    def test_make_spec(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        pyu = PyUpdater(t_config)
        pyu.setup()
        new_folder = os.path.join(u'pyu-data', u'new')
        spec_cmd = [u'make-spec', u'app.py', u'-F']
        spec_file_name = get_system() + u'.spec'
        build_cmd = [u'build', u'--app-name', u'MyApp',
                     u'--app-version', u'0.1.0', spec_file_name]

        parser = get_parser()
        with open(u'app.py', u'w') as f:
            f.write('print "Hello, World!"')
        args, pyu_args = parser.parse_known_args(spec_cmd)
        b = Builder(args, pyu_args)
        b.make_spec()
        assert os.path.exists(spec_file_name)
        args, pyu_args = parser.parse_known_args(build_cmd)
        b = Builder(args, pyu_args)
        b.build()
        with ChDir(new_folder):
            assert len(os.listdir(os.getcwd())) == 1

    def test_build_fail(self):
        with pytest.raises(SystemExit):
            t_config = TConfig()
            t_config.DATA_DIR = os.getcwd()
            pyu = PyUpdater(t_config)
            pyu.setup()
            spec_cmd = [u'make-spec', u'app.py', u'-F']
            spec_file_name = get_system() + u'.spec'
            build_cmd = [u'build', u'--app-name', u'MyApp', u'--clean'
                         u'--app-version', u'0.1.0', spec_file_name]

            parser = get_parser()
            with open(u'app.py', u'w') as f:
                # Missing closing quote
                f.write('print "Hello, World!')
            args, pyu_args = parser.parse_known_args(spec_cmd)
            b = Builder(args, pyu_args)
            b.make_spec()
            assert os.path.exists(spec_file_name)
            args, pyu_args = parser.parse_known_args(build_cmd)
            b = Builder(args, pyu_args)
            b.build()

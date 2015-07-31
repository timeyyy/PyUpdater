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

new_folder = os.path.join('pyu-data', 'new')

@pytest.mark.usefixtures('cleandir')
class TestNoRepo(object):

    def test_no_repo(self):
        with pytest.raises(SystemExit):
            b = Builder(list(), dict())
            b.build()


@pytest.mark.usefixtures('cleandir')
class TestMakeSpec(object):

    def test_make_spec(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        pyu = PyUpdater(t_config)
        pyu.setup()

        spec_cmd = ['make-spec', 'app.py', '-F', '--app-name', 'MyApp',
                    '--app-version', '0.1.0']
        spec_file_name = get_system() + '.spec'
        build_cmd = ['build', '--app-name', 'MyApp',
                     '--app-version', '0.1.0', spec_file_name]

        build_cmd = [str(b) for b in build_cmd]
        parser = get_parser()
        with open('app.py', 'w') as f:
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


@pytest.mark.usefixtures('cleandir')
class TestBuild(object):

    def test_build(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        pyu = PyUpdater(t_config)
        pyu.setup()

        build_cmd = ['build', '--app-name', 'MyApp',
                     '--app-version', '0.1.0', 'app.py']
        build_cmd = [str(b) for b in build_cmd]
        parser = get_parser()
        with open('app.py', 'w') as f:
            f.write('print "Hello, World!"')
        args, pyu_args = parser.parse_known_args(build_cmd)
        b = Builder(args, pyu_args)
        b.build()
        with ChDir(new_folder):
            assert len(os.listdir(os.getcwd())) == 1

    def test_build_mac_dot_app(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        pyu = PyUpdater(t_config)
        pyu.setup()

        build_cmd = ['build', '-F', '-w', '--app-name', 'MyApp',
                     '--app-version', '0.1.0', 'app.py']
        build_cmd = [str(b) for b in build_cmd]
        parser = get_parser()
        with open('app.py', 'w') as f:
            f.write('print "Hello, World!"')
        args, pyu_args = parser.parse_known_args(build_cmd)
        b = Builder(args, pyu_args)
        b.build()
        with ChDir(new_folder):
            assert len(os.listdir(os.getcwd())) == 1

    def test_make_spec_then_build(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        pyu = PyUpdater(t_config)
        pyu.setup()

        spec_cmd = ['make-spec', 'app.py', '-F',
                    '--app-name', 'MyApp',
                    '--app-version', '0.1.0']
        spec_file_name = get_system() + '.spec'
        build_cmd = ['build', '--clean', '--app-name', 'MyApp',
                     '--app-version', '0.1.0', spec_file_name]

        parser = get_parser()
        with open('app.py', 'w') as f:
            # Missing closing quote
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

    def test_build_fail_script_syntax_error(self):
        with pytest.raises(SystemExit):
            t_config = TConfig()
            t_config.DATA_DIR = os.getcwd()
            pyu = PyUpdater(t_config)
            pyu.setup()
            spec_cmd = ['make-spec', 'app.py', '-F']
            spec_file_name = get_system() + '.spec'
            build_cmd = ['build', '--app-name', 'MyApp', '--clean'
                         '--app-version', '0.1.0', spec_file_name]

            parser = get_parser()
            with open('app.py', 'w') as f:
                # Missing closing quote
                f.write('print "Hello, World!')
            args, pyu_args = parser.parse_known_args(spec_cmd)
            b = Builder(args, pyu_args)
            b.make_spec()
            assert os.path.exists(spec_file_name)
            args, pyu_args = parser.parse_known_args(build_cmd)
            b = Builder(args, pyu_args)


    def test_build_fail_no_spec_or_src(self):
        with pytest.raises(SystemExit):
            t_config = TConfig()
            t_config.DATA_DIR = os.getcwd()
            pyu = PyUpdater(t_config)
            pyu.setup()
            build_cmd = ['build', '--app-name', 'MyApp', '--clean'
                         '--app-version', '0.1.0', '-F']

            parser = get_parser()
            args, pyu_args = parser.parse_known_args(build_cmd)
            b = Builder(args, pyu_args)
            b.build()

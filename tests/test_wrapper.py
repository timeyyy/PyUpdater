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

import pytest

from pyupdater.wrapper.options import (add_build_parser,
                                       add_clean_parser,
                                       add_init_parser,
                                       add_keys_parser,
                                       add_make_spec_parser,
                                       add_package_parser,
                                       add_upload_parser,
                                       add_version_parser,
                                       make_subparser)


@pytest.mark.usefixtures('cleandir', 'parser')
class TestBuilder(object):

    def test_build_no_options(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            parser.parse_known_args(['build'])

    def test_build_no_appanme(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            parser.parse_known_args(['build', '--app-version=0.2.10'])

    def test_build_no_appversion(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            parser.parse_known_args(['build', '--app-name=Test'])

    def test_build_no_arguments(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            with open('app.py', 'w') as f:
                f.write('print "Hello World"')
            parser.parse_known_args(['build', 'app.py'])

    def test_build(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with open('app.py', 'w') as f:
            f.write('print "Hello World"')
        parser.parse_known_args(['build', '--app-name=Test',
                                '--app-version=0.1.0', 'app.py'])


@pytest.mark.usefixtures('cleandir', 'parser')
class TestClean(object):
    def test_clean(self, parser):
        subparser = make_subparser(parser)
        add_clean_parser(subparser)
        assert parser.parse_known_args(['clean'])


@pytest.mark.usefixtures('cleandir', 'parser')
class TestInit(object):

    def test_init(self, parser):
        subparser = make_subparser(parser)
        add_init_parser(subparser)
        assert parser.parse_known_args(['init'])


@pytest.mark.usefixtures('cleandir', 'parser')
class TestKeys(object):

    def test_keys(self, parser):
        subparser = make_subparser(parser)
        add_keys_parser(subparser)
        assert parser.parse_known_args(['keys'])


@pytest.mark.usefixtures('cleandir', 'parser')
class TestMakeSpec(object):

    def test_make_spec(self, parser):
        subparser = make_subparser(parser)
        add_make_spec_parser(subparser)
        with pytest.raises(SystemExit):
            assert parser.parse_known_args(['make-spec'])


@pytest.mark.usefixtures('cleandir', 'parser')
class TestPkg(object):

    def test_package(self, parser):
        subparser = make_subparser(parser)
        add_package_parser(subparser)
        assert parser.parse_known_args(['pkg'])


@pytest.mark.usefixtures('cleandir', 'parser')
class TestSettings(object):

    def test_settings(self):
        pass


@pytest.mark.usefixtures('cleandir', 'parser')
class TestUploader(object):

    def test_upload(self, parser):
        subparser = make_subparser(parser)
        add_upload_parser(subparser)
        assert parser.parse_known_args(['upload'])


@pytest.mark.usefixtures('cleandir', 'parser')
class TestVersion(object):

    def test_version(self, parser):
        subparser = make_subparser(parser)
        add_version_parser(subparser)
        assert parser.parse_known_args(['version'])

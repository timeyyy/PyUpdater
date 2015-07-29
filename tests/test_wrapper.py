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

from pyupdater.wrapper.options import (make_subparser,
                                       add_build_parser,
                                       add_clean_parser,
                                       add_debug_parser,
                                       add_init_parser,
                                       add_keys_parser,
                                       add_make_spec_parser,
                                       add_package_parser,
                                       add_upload_parser,
                                       add_version_parser)


@pytest.mark.usefixtures('cleandir', 'parser')
class TestWrapper(object):

    def test_build_no_options(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            parser.parse_args(['build'])

    def test_build_no_appanme(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            parser.parse_args(['build', '--app-version=0.2.10'])

    def test_build_no_appversion(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            parser.parse_args(['build', '--app-name=Test'])

    def test_clean(self, parser):
        subparser = make_subparser(parser)
        add_clean_parser(subparser)
        assert parser.parse_args(['clean'])

    def test_init(self, parser):
        subparser = make_subparser(parser)
        add_init_parser(subparser)
        assert parser.parse_args(['init'])

    def test_keys(self, parser):
        subparser = make_subparser(parser)
        add_keys_parser(subparser)
        assert parser.parse_args(['keys'])

    def test_log(self, parser):
        subparser = make_subparser(parser)
        add_debug_parser(subparser)
        assert parser.parse_args(['collect-debug-info'])

    def test_make_spec(self, parser):
        subparser = make_subparser(parser)
        add_make_spec_parser(subparser)
        assert parser.parse_args(['make-spec'])

    def test_package(self, parser):
        subparser = make_subparser(parser)
        add_package_parser(subparser)
        assert parser.parse_args(['pkg'])

    def test_upload(self, parser):
        subparser = make_subparser(parser)
        add_upload_parser(subparser)
        assert parser.parse_args(['upload'])

    def test_version(self, parser):
        subparser = make_subparser(parser)
        add_version_parser(subparser)
        assert parser.parse_args(['version'])

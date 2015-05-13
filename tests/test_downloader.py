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
import pytest

from pyupdater.client.downloader import FileDownloader


FILENAME = u'dont+delete+pyu+test.txt'
FILENAME_WITH_SPACES = 'dont delete pyu test.txt'
FILE_HASH = u'9da856b0b8b77c838d6945e0bfbc62fff978a9dd5256eed231fc499b5d4b183c'
URL = u'https://s3-us-west-1.amazonaws.com/pyupdater-test/'


@pytest.mark.usefixtue("cleandir")
class TestDownload(object):
    def test_download_return(self):
        fd = FileDownloader(FILENAME, URL, FILE_HASH)
        binary_data = fd.download_verify_return()
        assert binary_data is not None

    def test_download_return_fail(self):
        fd = FileDownloader(FILENAME, URL, u'JKFEIFJILEFJ983NKFNKL')
        binary_data = fd.download_verify_return()
        assert binary_data is None

    def test_url_with_spaces(self):
        fd = FileDownloader(FILENAME_WITH_SPACES, URL, FILE_HASH)
        binary_data = fd.download_verify_return()
        assert binary_data is not None

    def test_bad_url(self):
        fd = FileDownloader(FILENAME, u'bad url', u'bad hash')
        binary_data = fd.download_verify_return()
        assert binary_data is None

    def test_bad_content_length(self):
        class FakeHeaders(object):
            headers = {}
        fd = FileDownloader(FILENAME, URL, FILE_HASH)
        data = FakeHeaders()
        assert fd._get_content_length(data) == 100000

    def test_good_conent_length(self):
        fd = FileDownloader(FILENAME, URL, FILE_HASH)
        fd.download_verify_return()
        assert fd.content_length == 60000

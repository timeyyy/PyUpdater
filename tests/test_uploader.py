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
import requests

from pyupdater.uploader import BaseUploader, Uploader
from pyupdater.utils.exceptions import UploaderError, UploaderPluginError

from tconfig import TConfig

my_config = TConfig()


@pytest.mark.usefixtures('cleandir')
class TestUploader(object):

    def test_plugin_baseclass_not_implemented(self):

        with pytest.raises(NotImplementedError):
            b = BaseUploader()
            b.init()

        with pytest.raises(NotImplementedError):
            b = BaseUploader()
            b.connect()

        with pytest.raises(NotImplementedError):
            b = BaseUploader()
            b.upload_file(u'test')

    def test_plugin_baseclass(self, httpbin):
        class MyUploader(BaseUploader):

            def init(self, **kwargs):
                self.file_list = ['test']

            def upload_file(self, filename):
                with open(u'testfile.txt', u'wb') as f:
                    f.write('this is some text')
                with open(u'testfile.txt', u'rb') as f:
                    data = f.read()
                files = {u'file': data}
                r = requests.post(httpbin.url + u'/post', files=files)
                assert r.json()[u'files'][u'file'] == data

        mu = MyUploader()
        mu.init()
        mu.upload()

    def test_fail_no_uploader_set_fail(self, httpbin):
        with pytest.raises(UploaderError):
            u = Uploader()
            u.init({})
            u.upload()

    def test_upload(self, httpbin):
        class MyUploader(BaseUploader):

            def init(self, **kwargs):
                self.file_list = ['test']

            def upload_file(self, filename):
                with open(u'testfile.txt', u'wb') as f:
                    f.write('this is some text')
                with open(u'testfile.txt', u'rb') as f:
                    data = f.read()
                files = {u'file': data}
                r = requests.post(httpbin.url + u'/post', files=files)
                assert r.json()[u'files'][u'file'] == data
        u = Uploader()
        u.init({u'test': u'test'})
        u.uploader = MyUploader()
        u.uploader.init(test=u'test')
        u.upload()

    def test_set_uploader_fail(self):
        u = Uploader()
        u.init({u'test': u'test'})
        with pytest.raises(UploaderError):
            u.set_uploader([])

        with pytest.raises(UploaderPluginError):
            u.set_uploader('bad plugin name')

    def test_set_uploader(self):
        u = Uploader()
        u.init({u'OBJECT_BUCKET': u'vdpro'})
        u.set_uploader('s3')
        assert u.uploader is not None

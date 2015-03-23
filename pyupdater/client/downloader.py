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
from io import BytesIO
import logging
import time

from pyupdater.utils import get_hash, lazy_import

log = logging.getLogger(__name__)


@lazy_import
def certifi():
    import certifi
    return certifi


@lazy_import
def urllib3():
    import urllib3
    return urllib3


class FileDownloader(object):
    """The FileDownloader object downloads files to memory and
    verifies their hash.  If hash is verified data is either
    written to disk to returned to calling object

    Args:

        filename (str): The name of file to download

        urls (list): List of urls to use for file download

    Kwargs:

        hexdigest (str): The hash of the file to download

        verify (bool) Meaning:

            True: Verify https connection

            False: Don't verify https connection
    """
    def __init__(self, filename, urls, hexdigest=None, verify=True,
                 progress_hooks=[]):
        self.filename = filename
        if isinstance(urls, list) is False:
            self.urls = [urls]
        else:
            self.urls = urls
        self.hexdigest = hexdigest
        self.verify = verify
        self.b_size = 4096 * 4
        self.file_binary_data = None
        self.my_file = BytesIO()
        self.content_length = None
        self.progress_hooks = progress_hooks
        if self.verify is True:
            self.http_pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                                 ca_certs=certifi.where())
        else:
            self.http_pool = urllib3.PoolManager()

    def download_verify_write(self):
        """Downloads file then verifies against provided hash
        If hash verfies then writes data to disk

        Returns:

            (bool) Meanings:

                True - Hash verified

                False - Hash not verified
        """
        # Downloading data internally
        self._download_to_memory()
        check = self._check_hash()
        # Nothing to verify against so return true
        if check is None:
            return True
        if check is True:
            self._write_to_file()
            return True
        else:
            del self.file_binary_data
            del self.my_file
            return False

    def download_verify_return(self):
        """
        Downloads file to memory, checks against provided hash
        If matched returns binary data

        Returns:

            (data) Meanings:

                Data - If everything verified

                None - If any verification didn't pass
        """
        self._download_to_memory()
        check = self._check_hash()
        if check is None:
            return self.file_binary_data
        if check is True:
            return self.file_binary_data
        else:
            return None

    @staticmethod
    def _best_block_size(elapsed_time, bytes):
        # Returns best block size for current Internet connection speed
        new_min = max(bytes / 2.0, 1.0)
        new_max = min(max(bytes * 2.0, 1.0), 4194304)  # Do not surpass 4 MB
        if elapsed_time < 0.001:
            return int(new_max)
        rate = bytes / elapsed_time
        if rate > new_max:
            return int(new_max)
        if rate < new_min:
            return int(new_min)
        return int(rate)

    def _download_to_memory(self):
        data = self._create_response()
        if data is None or data == '':
            return None

        self.content_length = self._get_content_length(data)
        recieved_data = 0

        while 1:
            # Grabbing start time for use with best block size
            start_block = time.time()
            block = data.read(self.b_size)
            # Grabbing end time for use with best block size
            end_block = time.time()
            if len(block) == 0:
                # No more data, get out of this never ending loop!
                break
            self.b_size = self._best_block_size(end_block - start_block,
                                                len(block))
            log.debug(u'Block size: %s' % self.b_size)
            self.my_file.write(block)
            recieved_data += len(block)
            percent = self._calc_progress_percent(recieved_data,
                                                  self.content_length)
            status = {u'total': self.content_length,
                      u'downloaed': recieved_data,
                      u'status': u'downloading',
                      u'percent_complete': percent}
            self._call_progress_hooks(status)

        self.my_file.flush()
        self.my_file.seek(0)
        self.file_binary_data = self.my_file.read()
        status = {u'total': self.content_length,
                  u'downloaed': recieved_data,
                  u'status': u'finished'}
        self._call_progress_hooks(status)
        log.debug(u'Download Complete')

    def _call_progress_hooks(self, data):
        log.debug(data)
        for ph in self.progress_hooks:
            ph(data)

    def _create_response(self):
        # Downloads file to memory.  Keeps internal reference
        data = None
        for url in self.urls:
            file_url = url + self.filename
            log.debug('Url for request: {}'.format(file_url))
            try:
                data = self.http_pool.urlopen('GET', file_url,
                                              preload_content=False)
                # Have to catch url with spaces
                if data.status == 505:
                    raise urllib3.exceptions.HTTPError
            except urllib3.exceptions.HTTPError:
                log.debug(u'Might have had spaces in an S3 url...')
                file_url = file_url.replace(' ', '+')
                log.debug(u'S3 updated url {}'.format(file_url))
                data = None
            except urllib3.exceptions.SSLError:
                log.error(u'SSL cert not verified')
                data = ''
            except Exception as e:
                # Catch whatever else comes up and log it
                # to help fix other http related issues
                log.error(str(e), exc_info=True)
                data = ''
            else:
                break

            # Try request again with spaces in url replaced with +
            if data is None:
                # Let's try one more time with the fixed url
                try:
                    data = self.http_pool.urlopen('GET', file_url,
                                                  preload_content=False)
                except urllib3.exceptions.SSLError:
                    log.error(u'SSL cert not verified')
                except Exception as e:
                    log.error(str(e), exc_info=True)
                    self.file_binary_data = None
                else:
                    break

        log.debug(u'Downloading {} from:\n{}'.format(self.filename, file_url))
        return data

    def _write_to_file(self):
        # Writes download data in memory to disk
        with open(self.filename, u'wb') as f:
            f.write(self.file_binary_data)

    def _check_hash(self):
        # Checks hash of downloaded file
        if self.hexdigest is None:
            # No hash provided to check.
            # So just return any data recieved
            log.debug(u'No hash to verify')
            return None
        if self.file_binary_data is None:
            # Exit quickly if we got nohting to compare
            # Also I'm sure we'll get an exception trying to
            # pass None to get hash :)
            log.debug(u'Cannot verify file hash - No Data')
            return False
        log.debug(u'Checking file hash')
        log.debug(u'Update hash: {}'.format(self.hexdigest))

        file_hash = get_hash(self.file_binary_data)
        if file_hash == self.hexdigest:
            log.debug(u'File hash verified')
            return True
        log.debug(u'Cannot verify file hash')
        return False

    def _get_content_length(self, data):
        content_length = int(data.headers.get(u"Content-Length", 100000))
        log.debug(u'Got content length of: %s', content_length)
        return content_length

    @staticmethod
    def _calc_eta(start, now, total, current):
        # Not currently implemented
        # Calculates remaining time of download
        if total is None:
            return u'--:--'
        dif = now - start
        if current == 0 or dif < 0.001:  # One millisecond
            return u'--:--'
        rate = float(current) / dif
        eta = int((float(total) - float(current)) / rate)
        (eta_mins, eta_secs) = divmod(eta, 60)
        if eta_mins > 99:
            return u'--:--'
        return u'%02d:%02d' % (eta_mins, eta_secs)

    def _calc_progress_percent(self, x, y):
        percent = float(x) / y * 100
        percent = u'%.1f' % percent
        return percent

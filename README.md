[![CircleCI](https://img.shields.io/circleci/project/BrightFlair/PHP.Gt.svg)](https://github.com/JohnyMoSwag/PyUpdater)
[![Coverage Status](https://coveralls.io/repos/JohnyMoSwag/PyUpdater/badge.svg?branch=master)](https://coveralls.io/r/JohnyMoSwag/PyUpdater?branch=master)
[![Development Status](https://pypip.in/status/PyUpdater/badge.svg?style=flat)](https://pypi.python.org/pypi/PyUpdater/)
[![Requirements Status](https://requires.io/github/JohnyMoSwag/PyUpdater/requirements.svg?branch=master)](https://requires.io/github/JohnyMoSwag/PyUpdater/requirements/?branch=master)
[![Downloads](https://pypip.in/download/PyUpdater/badge.svg?style=flat)](https://pypi.python.org/pypi/PyUpdater/)

# PyUpdater
##### An update framework for managing, signing & uploading your app updates
[Documentation](http://docs.pyupdater.com)

[Dev Documentation](http://dev-docs.pyupdater.com)


[Full changelog](https://github.com/JohnyMoSwag/PyUpdater/blob/master/changelog.txt)

#### Made for [PyInstaller](http://www.pyinstaller.org) >= 2.1


## To Install

######Stable:

    $ pip install -U PyUpdater

######Dev:

    $ pip install -U https://github.com/JohnyMoSwag/PyUpdater/tarball/master

######Extras: S3 & SCP upload plugins are available with

    $ pip install -U PyUpdater[s3]

or

    $ pip install -U PyUpdater[scp]


## Usage:

###### To compile & package your script

    $ pyupdater build example_app.py --app-name="Example APP" --app-version=0.1.0


###### For creating update diff's, updating your version file & uploading your update

    $ pyupdater pkg --process

    $ pyupdater pkg --sign

###### Upload your updates to Amazon S3

    $ pyupdater upload --service s3


######For help & extra commands

    $ pyupdater -h
    $ pyupdater command -h


###### Using programmatically
######[Click Here](https://github.com/JohnyMoSwag/PyUpdater/tree/master/demos "Example Usage") To See Example Work Flow


## Write your own upload plugin
######Its up to Plugin authors to get credentials from users. Easiest would be to have env vars set.

    from pyi_updater.uploader import BaseUploader


    class MyUploader(BaseUploader):

        def __init__(self):
            super(MyUplaoder, self).__init__()

        def init(**kwargs):
            # files (list): List of files to upload
            #
            # The following items may be None
            #
            # object_bucket (str): AWS/Dream Objects/Google Storage Bucket
            #
            # ssh_remote_dir (str): Full path on remote machine to place updates
            #
            # ssh_username (str): user account of remote server uploads
            #
            # ssh_host (str): Remote host to connect to for server uploads


        def connect(self):
            # Grab credentials from env vars & connect to service here

        def upload_file(self, filename):
            # Upload file here


######In your setup.py

Example from s3 upload plugin

    entry_points={
        'pyupdater.plugins.uploaders': [
            's3 = s3_plugin:S3Uploader',
        ]


#### Examples available
###### [S3 Plugin](https://github.com/JohnyMoSwag/PyUpdater-S3-Plugin "S3 Plugin")
###### [SCP Plugin](https://github.com/JohnyMoSwag/PyUpdater-SCP-Plugin "SCP Plugin")

## Support Archive Formats
###### Zip for Windows and GZip for Mac & Linux.  Constraints being on patch size.

#### Archive Patch Tests:
Format  -  Src  -  Dst  -  Patch

7z - 6.5mb - 6.8mb -  6.8mb

bz2 - 6.6mb - 6.8mb - 6.9mb

zip - 6.5mb - 6.8mb - 3.2mb

gz - 6.5mb - 6.8mb - 3.2mb

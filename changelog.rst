Changelog
=========
v0.19.3 - 2015/02/22
~~~~~~~~~~~~~~~~~~~~

* Fixed

  - Client

    - Removing old updates. Really fixed it this time :)

v0.19.2 - 2015/02/22
~~~~~~~~~~~~~~~~~~~~

* Fixed

  - Client

    - Removing old updates

v0.19.1 - 2015/02/22
~~~~~~~~~~~~~~~~~~~~

* Fixed

  - PyiUpdater

    - Creating new config db when running any command

v0.19 - 2015/02/22
~~~~~~~~~~~~~~~~~~~~

* Added

  - CLI

    - Update command. Used after updating PyiUpdater to update repository

  - Logging

    - Now logs framework version

* Updated

  - CLI

    - Clearer output messages
    - Correct some spelling

  - Client

    - Exception handling
    - Moved patcher and downloader to client package
    - Using requests instead of urllib3.
    - More reliable https verification

  - PyiUpdater

    - Potential incorrect comparison of pyinstaller versions
    - Archive version parsing
    - Crashing if directory doesn't exists
    - Pinning version of plugins
    - Initial support for pre release versions
    - Moved some uploader config to plugins. Check plugin docs for more info.
    - Updated config attributes. * Make sure to run pyiupdater update
    - Install commands

      $ pip install[patch] # To enable patch support
      $ pip install[all] # To add patch support, aws s3 & scp upload plugins

  - Plugins

    - from pyi_updater.uploader import BaseUploader
    - from pyi_updater.uploader.commom import BaseUploader will
      be remove in v0.22+

* Fixed

  - Key Handler

    - Writing of deprecated version meta after migration
    - Not loading keys from db

  - Package Handler

    - Migration of repo meta config

  - PyiUpdater

    - Potential error when adding key add key.db isn't loaded

* Removed

  - PyiUpdater

    - Some unused attributes on config object
    - Unsed functions


v0.18.0 - 2015/2/7
~~~~~~~~~~~~~~~~~~
* Updated

  - Docs

    - New dev install method

  - Logging

    - Increased log rotation size to 10mb
    - Using bzip2 to compress logs for export

  - PyiUpdater

    - More lazy import to decrease start up times
    - Code refactoring

* Fixed

  - Client

    - Failing to download version file because of failed TLS/SSL cert
      verification

  - Logging

    - Not logging because of incorrect format string

v0.17.3 - 2015/2/7
~~~~~~~~~~~~~~~~~~
* Fixed

  - PyiUpdater

    - Mac .app's binary now has correct app name

v0.17.2 - 2015/2/7
~~~~~~~~~~~~~~~~~~

* Updated

  - Logging

    - Increased log rotation file size to 1.4mb. Was .5mb

  - Utils

    - Lazy loading implementation
    - Simplified code for various methods using updated lazing loading

* Fixed

  - CLI

    - Initial setup input error

v0.17.1 - 2015/2/1
~~~~~~~~~~~~~~~~~~
* Added

  - PyiUpdater

    - Spec file support. Examples below
    ::

      $ pyiupdater make-spec [opts] script.py

      # Then build your app

      $ pyiupdater script.spec --app-name=script --app-version=0.1.0

    - Debugging will be turned on by default on dev builds

* Updated

  - PyiUpdater

    - Added more checks to repo verification


* Fixed

  - Client

    - Deletion of app on initial update download


v0.16 - 2015/25/1
~~~~~~~~~~~~~~~~~
* Added
  - CLI

    - Can now update repo settings

  - Client

    - Progress hooks - used for download progress

  - Docs

    - Todo list
    - Updated demos to match api & code comments more descriptive

  - PyiUpdater

    - Hooks for certifi
    - Settings module to make updating easier.
    - PyiUpdater settings db
    - Unified utils modules
    - Added version object


* Updated

  - CLI

    - Handles exceptions better
    - More descriptive error messages
    - Updated command args
    - Log export for debugging
    - Builder is now a class
    - Utils class
    - Added --clean to compile a fresh build
    - Handling of args for pyiupdater

  - Client

    - Only log version data file once
    - logging difference between patch & full update
    - Version objects for better version comparison & conversion

  - PyiUpdater

    - Lowered pyinstaller requirement to 2.1
    - Added hooks included in newer versions of pyinstaller
    - Added rotating logs
    - Handling cases where root directory name is changed

* Fixed

  - CLI

    - Build: Packaging mac .app

  - Client

    - Restarting app after auto-update
    - Deleting version data on bad sig check
    - Windows restart batch file not closing
    - Removal of old update archives

* Removed

  - CLI

    - Build: Spec file support - will be coming back bigger & better.

  - PyiUpdater

    - Storing pickled config in plain file
    - Unused requirements
    - Blinker dependency


v0.15.0 - 2015/4/1
~~~~~~~~~~~~~~~~~~

Backwards incompatible release * Migration Available *


If you update to this release, do not revoke any keys until you are sure all clients are updated to this version of the framework. If you revoke a key it will break the built in migration.

* New

  - CLI

    - Can now revoke signing keys. The number of keys to revoke from oldest.
      ::

      $ pyiupdater keys --revoke 1

    - clean command: can remove PyiUpdater data & support file from root dir


  - PackageHandlder

    - Added migration command to new key system

* Updated

  - CLI

    - build command: Fixed naming of exe on windows

    - init command: can pass --count with the number of keys to create.

    - refactored cli code

  - Client

    - Support for multiple public keys verifying

    - Downloads & decompresses zipped meta data

  - KeyHandler

    - Creates gzipped meta data

  - License

    - Digital Sapphire Development Team


v0.13.0 - 2014/12/27
~~~~~~~~~~~~~~~~~~~~

Backwards incompatible release

Demos have been update with the changes. Also its very important to make a decrypted copy of your config file before updating.

* Updated

  - CLI

    - Updated with subcommands
    - pyiupdater -h
    - pyiupdater sub_command -h

  - Client

    - Fixed error when version numbers are correct in version file

  - KeyHandler

    - Moved key storage to .pyiupdater folder

  - PyiUpdater

    - Simplified config

* Fixed

  - PyiUpdater

    - Logging when pyi.log is next to Mac .app bundles

* Removed

  - Client

    - Redundant code

  - FileCrypt

    - Passwords for remote locations will need to be set as env vars

  - PyiUpdater

    - Redundant system calls

  - TUI

    - Removed in favor of cli


v0.12.3 - 2014/12/7
~~~~~~~~~~~~~~~~~~~

* Updated

  - Client

    - Handling version numbers passed to update_check

* Fixed

  - Client

    - Missing var

  - PackageHandler

    - Incrementing patch number
    - Trying to move a file that doesn't exist
    - Doing migrate on every run
    - Getting hash of file that doesn't exists

v0.12.2 - 2014/12/7
~~~~~~~~~~~~~~~~~~~

* Updated

  - PackageHandler

    - Error reporting when calling methods

* Fixed

  - CLI scripts

* Removed

  - Some unused code

v0.12.1 - 2014/12/4
~~~~~~~~~~~~~~~~~~~

* Fixed

  - Migrating to new patch numbering system


v0.12.0 - 2014/11/29
~~~~~~~~~~~~~~~~~~~~

* Added

  - .pyiupdater data directory. Used to keep track of packages & patch numbers.

* Updated

  - PackageHandler

    - Will migrate packages in files directory to safe-to-remove folder.
      Now only the most recent package will be kept in files directory for patch creation

* Fixed

  - Install from setup.py
  - Failed password retry

* Removed

v0.11.0 - 2014/11/22
~~~~~~~~~~~~~~~~~~~~

* Added

  - PyiWrapper

    - Spec file support. Spec file will be rejected if onedir mode is specified.

* Updated

  - Client

    - Now each call to update_check returns 1 of 2 update objects. AppUpdate or LibUpdate. The updated objects are nearly identical. The AppUpdate object has a few more methods like restart & extract_restart. Now instead of calling client.download() you will use app_update.download(). Check the demos for more info.

  - PyiWrapper

    - Increased stability of wrapper to better parse args

  - CLI

    - start cli with pyiupdater-cli instead of pyi-cli


* Removed

  - CLI

    - Archiver Utility

v0.10.0 - 2014/11/16
~~~~~~~~~~~~~~~~~~~~

* Added

  - Secure downloading of manifest
  - Offline update

    - Upon successful online version manifest signature verification, the version file manifest will be written to the app data folder.

    - Calls to client.download() will check if update has already been downloaded & return True if the checksum verifies before attempting to download update.

  - Pyinstaller wrapper

    - Using the following command compiles your script and archives it ready for file diff and upload::

      $ pyiupdater app.py --app-name=APP --app-version=0.1.0

  - Deprecated Warnings

    - use client.extract() instead of client.install()
    - use client.extract_restart() instead of client.install_restart()

* Updated

  - URL sanitizing

    - Better handling of types passed to config class attributes

* Fixed

  - Archiving currently running app

    - Will now archive Mac.app apps

* Removed

  - Common util functions

    - They were added to jms-utils


v0.9.2 - 2014/10/19
~~~~~~~~~~~~~~~~~~~

* Fixed

  - Require PyInstaller 2.1.1 for PyiUpdater usage


v0.9.1 - 2014/10/19
~~~~~~~~~~~~~~~~~~~

* Added

  - Require PyInstaller 2.1.1 for PyiUpdater usage


v0.9.0 - 2014/10/18
~~~~~~~~~~~~~~~~~~~

* Added

  - Support for multiple update urls
  - Auto generated client config
  - ed25529 Update verification

    - Using instead of RSA

* Updated

  - Client updater

    - Support Mac GUI app bundles
    - Better error handling
    - Less failed application execution when updater
      has errors

    - Patcher

      - Now verifies patched update integrity
        against version file

  - Downloader

    - Https verification

      - on by default
      - Can disable in config file
      - VERIFY_SERVER_CERT

    - Dynamic block resizing

  - Archive Extraction

    - More reliable

  - Archive creator

    - Works with mac GUI apps

  - Private methods

    - Refactored to make testing easier


v0.8.1 - 2014/9/3
~~~~~~~~~~~~~~~~~

* Added

  - jms-utils

* Fixed

  - Packaging setup.py installation

* Removed

  - Unused tests


v0.8.0 - 2014/8/31
~~~~~~~~~~~~~~~~~~

* Added

  - Archive Maker utility

    - Makes zip & gzip archives with name, version
      and platform in correct format for package handler

  - Signals

    - If you want to run updater in background
      thread you can subscribe to signals for
      download progress and completion

  - CLI

    - Option to change encryption password

  - Initial py3 compat

  - More code comments if you want to get your
    hands dirty

  - Option to enable https verification

* Updated

  - Package Handler

    - Package metadata parsing is faster. Thanks
      to a new & shiny package object.

  - File Crypt

    - Uses simple encryption interface of
      simple-crypt. Pycrypto in background.

* Fixed

  - CLI

    - Initial setup didn't save settings
      to correct class attributes


  - Client

    - Parsing of version file


  - Patch creation

    - Example:

      1.9 > 1.10 was True

      1.9 > 1.10 is now False

* Removed

  - Cryptography dependency
  - License text from individual files
  - Unused imports


v0.7.2 - 2014/8/10
~~~~~~~~~~~~~~~~~~

* Fixed

  - Error on load cli

v0.7.1 - 2014/8/10
~~~~~~~~~~~~~~~~~~

* Added

  - Utils

    - Utils specific errors

  - KeyHandler

    - Error if DevDataDir not setup

* Updated

  - Client

    - Better parsing of old updates to remove

    - More error checking

    - More error reporting

    - Dynamic creation of archive format

  - Utils

    - Better parsing of dot files for removal

* Removed

  - Client

    - Some old transition code


v0.7 - 2014/8/3
~~~~~~~~~~~~~~~

* Added

  - Uploader plugin support
  - Default S3 & SCP plugins
  - Support for gzipped archives

* Updated

  - Menu option handling

* Remove

  - Upload code for s3 and scp
  - Unused config options
  - Redundant upload checks


v0.6.0 - 2014/7/27
~~~~~~~~~~~~~~~~~~

*** Renamed to PyiUpdater ***

* Removed

  - Old transition code
  - Binary support

    - only pip & src install

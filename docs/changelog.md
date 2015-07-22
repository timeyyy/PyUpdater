# Changelog

## v0.23.4 - Master
##### This version is not yet released and is under active development.


## v0.23.3 - 2015/07/21

Fixed

  - File already exists error

## v0.23.2 - 2015/07/21

Fixed

  - Compilation

Updated

  - PyInstaller to 39b02fe5e7563431115f9812f757a21bbcc78837


## v0.23.1 - 2015/07/19

Fixed

  - Missing bootloaders


## v0.23.0 - 2015/07/19

Added

  - Vendored PyInstaller

    - f920d3eea510ed088eda5359c04990338600c2b8
    - Ability to provide fixes quicker

Fixed

  - Error when patch info is None


## v0.22.3 - 2015/07/18

Fixed

  - Parsing platform names


## v0.22.2 - 2015/07/18

Fixed

  - Versioneer settings


## v0.22.1 - 2015/07/18

Updated

  - Versioneer settings



## v0.22 - 2015/07/18

Updated

  - Code refactoring & optimizations

  - Download url

  - Converted docs to markdown

  - Error handling for callbacks

  - Libs

    - ed15519 1.4
    - stevedore 1.6.0
    - PyUpdater-S3-Plugin 2.3

Removed

  - Duplicate code
  - Deprecated log command

## v0.21.1 - 2015/05/25

Added

  * More hooks from pyinstaller develop

Updated

  * Test runs in parallel
  * Documentation
  * Libs
    - requests 2.7.0
    - urllib3 1.10.4

Fixed

  - Parsing App Name from update archive filename when version number is in x.x format
  - Potential import error if pyinstaller version lower then 2.1

Removed

  - Unused code


## v0.21.0 - 2015/04/30

Updated

  - PyUpdater

    - Debug logs are uploaded to a gist on github
    - requests lib 2.6.2
    - urllib3 lib 1.10.3
    - stevedore lib 1.4.0
    - S3 plugin 2.2
    - SCP plugin 2.2
    - Code refactoring

Fixed

  - PyUpdater

    - Potential leak of sensitive information to log files


## v0.20.0 - 2015/03/08
##### Renamed to PyUpdater

Added

Updated

  - Client

    - Better error handling

  - PyUpdater

    - Using json to store config data
    - Less IO during execution
    - Header performance improvements - upstream
    - Central db object

Fixed

  - Client

    - Handling of download with corresponding hash

  - PyUpdater

    - session fixation attacks and potentially cookie stealing - upstream
    - Not writing config file when cleaning repo

Removed

  - PyUpdater

    - RC4 from default cipher list - upstream
    - Old migration code
    - Removed old json version file
    - Download progress to stdout
    - Unused imports


## v0.19.3 - 2015/02/22

Fixed

  - Client

    - Removing old updates. Really fixed it this time :)


## v0.19.2 - 2015/02/22

Fixed

  - Client

    - Removing old updates


## v0.19.1 - 2015/02/22

Fixed

  - PyUpdater

    - Creating new config db when running any command


## v0.19 - 2015/02/22

Added

  - CLI

    - Update command. Used after updating PyUpdater to update repository

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

  - PyUpdater

    - Potential incorrect comparison of pyinstaller versions
    - Archive version parsing
    - Crashing if directory doesn't exists
    - Pinning version of plugins
    - Initial support for pre release versions
    - Moved some uploader config to plugins. Check plugin docs for more info.
    - Updated config attributes. * Make sure to run pyupdater update
    - Install commands

      $ pip install[patch] # To enable patch support
      $ pip install[all] # To add patch support, aws s3 & scp upload plugins

  - Plugins

    - from pyi_updater.uploader import BaseUploader
    - from pyi_updater.uploader.commom import BaseUploader will
      be remove in v0.22+

Fixed

  - Key Handler

    - Writing of deprecated version meta after migration
    - Not loading keys from db

  - Package Handler

    - Migration of repo meta config

  - PyUpdater

    - Potential error when adding key add key.db isn't loaded

Removed

  - PyUpdater

    - Some unused attributes on config object
    - Unsed functions
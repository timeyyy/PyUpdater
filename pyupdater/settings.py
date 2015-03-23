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
APP_NAME = u'PyUpdater App'
APP_AUTHOR = u'Digital Sapphire'

# Used to hold PyUpdater config info for repo
CONFIG_DATA_FOLDER = u'.pyupdater'

DEBUG_ARCHIVE = u'pyupdater-debug.tar.bz2'

# User config file
CONFIG_FILE_USER = u'pyuconfig.db'

CONFIG_DB_KEY_APP_CONFIG = u'app_config'
CONFIG_DB_KEY_KEYS = u'signing_keys'
CONFIG_DB_KEY_VERSION_META = u'version_meta'
CONFIG_DB_KEY_PY_REPO_CONFIG = u'py_repo_config'

GENERIC_APP_NAME = u'PyUpdater App'
GENERIC_COMPANY_NAME = u'PyUpdater'

# Log filename
LOG_FILENAME = u'pyu.log'
LOG_FILENAME_DEBUG = u'pyu-debug.log'

# Used for plugins
UPLOAD_PLUGIN_NAMESPACE = 'pyupdater.plugins.uploaders'

# Name of client config file
USER_CLIENT_CONFIG_FILENAME = u'client_config.py'

# Main user visible data folder
USER_DATA_FOLDER = u'pyu-data'

# Name of env var to get users passwrod from
USER_PASS_ENV = u'PYUPDATER_PASS'

# Key in version file where value are update meta data
UPDATES_KEY = u'updates'

# Folder on client system where updates are stored
UPDATE_FOLDER = u'update'

# Name of version file place in online repo
VERSION_FILE = u'versions.gz'
VERSION_FILE_OLD = u'version.json'

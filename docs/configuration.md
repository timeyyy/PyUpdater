# Configuration

Class Attribute | Description
--- | ---
APP_NAME | (str) Name of your app. Used with COMPANY_NAME to create an update cache dir on end user system.
COMPANY_NAME | (str) Company or your name. Used with APP_NAME to create an update cache dir on end user system.
PUBLIC_KEYS | (list) Public keys used to verify version manifest file.
UPDATE_URLS | (list) A list of url where a client will look for needed update objects.
UPDATE_PATCHES | (bool) Enable/disable creation of patch updates
OBJECT_BUCKET | (str) AWS/Dream Objects/Google Storage Bucket
SSH_USERNAME | (str) user account of remote server uploads
SSH_HOST | (str) Remote host to connect to for server uploads
SSH_REMOTE_DIR | (str) Full path on remote machine to place updates
VERIFY_SERVER_CERT | (str) Verify TLS/SSL certs
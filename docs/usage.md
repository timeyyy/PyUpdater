# Usage

All commands must be ran from root or repository.

Initialize a new repository.

    $ pyupdater init


To create your first update.

    $ pyupdater --app-name"Your app name" --app-version1.0.0 app.py


Get update meta data and save to file.

    $ pyupdater pkg -P


Sign update file with signing keys & gzip compress.

    $ pyupdater pkg -S


Upload to remote location.

    $ pyupdater upload --service s3


To update repo settings pass each flag you'd like to update.

    $ pyupdater settings --app-name --company


Here using Amazon S3. Must have PYUPDATER_PASS env set. Install with pyupdater[s3].

    $ pip install pyupdater[s3]


For help & extra commands::

    $ pyupdater -h
    $ pyupdater command -h


# Demos

Example of using the client within your app

    demos/client.py

# Limitations

* No onedir support
* No python3 support
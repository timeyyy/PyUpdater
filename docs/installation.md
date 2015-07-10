## Installation

PyUpdater depends on a few external libraries:

[appdirs](https://pypi.python.org/pypi/appdirs/), [blinker](https://pypi.python.org/pypi/blinker), [boto](http://aws.amazon.com/sdkforpython/), [bsdiff4](https://github.com/ilanschnell/bsdiff4), [certifi](https://pypi.python.org/pypi/certifi), [ed25519](https://pypi.python.org/pypi/ed25519), [jms_utils](https://pypi.python.org/pypi/JMS-Utils), [pyinstaller](https://github.com/pyinstaller/pyinstaller), [six](https://pypi.python.org/pypi/six), [stevedore](https://pypi.python.org/pypi/stevedore) & [urllib3](https://pypi.python.org/pypi/urllib3).

* Bsdiff4 is only required to make patches, not to apply them.  These libraries are not documented here.


So how do you get all that on your computer quickly?


#### Install Stable version

    $ pip install PyUpdater`

For patch support

    $ pip install PyUpdater[patch]


For complete install with aws s3 & scp upload plugins

    $ pip install PyUpdater[all]


Version 0.19+ Requires repository update after framework update

    $ pyupdater update

S3 & SCP upload plugins are available with

    $ pip install PyUpdater[s3]

    $ pip install PyUpdater[scp]


Be sure to check the plugins docs for setup & configuration options.

[PyUpdater-S3-Plugin](https://github.com/JohnyMoSwag/pyupdater-s3-plugin)

[PyUpdater-SCP-Plugin](https://github.com/JohnyMoSwag/pyupdater-scp-plugin)


#### Install Beta version

    $ pip install -U https://github.com/JohnyMoSwag/PyUpdater/tarball/master
from __future__ import unicode_literals

import shutil
import os

HOME = os.path.join('pyupdater', 'vendor')

junitxml = os.path.join(HOME, 'PyInstaller', 'lib', 'junitxml', 'tests')
unittest2 = os.path.join(HOME, 'PyInstaller', 'lib', 'unittest2')
items_to_remove = [junitxml, unittest2]


def remove(x):
    if os.path.isfile(x):
        os.remove(x)
    if os.path.isdir(x):
        shutil.rmtree(x, ignore_errors=True)


def main():
    for i in items_to_remove:
        remove(i)


if __name__ == '__main__':
    main()

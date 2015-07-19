import shutil
import os

HOME = os.path.join(u'pyupdater', u'vendor', 'PyInstaller', 'lib')

junitxml = os.path.join(HOME, u'junitxml', 'tests')
unittest2 = os.path.join(HOME, u'unittest2')

items = [junitxml, unittest2]


def remove(x):
    if os.path.isfile(x):
        os.remove(x)
    if os.path.isdir(x):
        shutil.rmtree(x, ignore_errors=True)


def main():
    for i in items:
        remove(i)


if __name__ == '__main__':
    main()

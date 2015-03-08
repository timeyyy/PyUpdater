#!/usr/bin/env python

from setuptools import Command, find_packages, setup
import subprocess
import sys

import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = 'pyi_updater/_version.py'
versioneer.versionfile_build = 'pyi_updater/_version.py'
versioneer.tag_prefix = ''  # tags are like 1.2.0
versioneer.parentdir_prefix = 'PyiUpdater-'  # dirname like 'myproject-1.2.0'


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, u'runtests.py', u'-v', u'-x',
                                u'--cov', u'pyi_updater', u'-n', u'4'])
        raise SystemExit(errno)


class PyTestCover(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, u'runtests.py', u'tests',
                                 u'--cov', u'pyi_updater', u'-n', u'1'])
        raise SystemExit(errno)


class PyTestMyCover(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, u'runtests.py', u'tests',
                                 u'--cov-report', u'html', u'--cov',
                                 u'pyi_updater', u'-n', u'4'])
        raise SystemExit(errno)

cmd_class = versioneer.get_cmdclass()
cmd_class.update({u'test': PyTest,
                  u'ctest': PyTestCover,
                  u'mytest': PyTestMyCover})

extra_s3 = 'PyiUpdater-s3-Plugin == 1.3'
extra_scp = 'PyiUpdater-scp-Plugin == 1.3'
extra_patch = 'bsdiff4'

setup(
    name='PyiUpdater',
    version=versioneer.get_version(),
    description='Simple App update framwork',
    author='Johny Mo Swag',
    author_email='johnymoswag@gmail.com',
    url='docs.pyiupdater.org',
    download_url=('https://github.com/JohnyMoSwag/Pyi'
                  'Updater/archive/master.zip'),
    license='Apache License 2.0',
    extras_require={
        's3': extra_s3,
        'scp': extra_scp,
        'patch': extra_patch,
        'all': [extra_s3, extra_scp, extra_patch]
        },
    tests_require=['pytest', ],
    cmdclass=cmd_class,
    install_requires=[
        'appdirs',
        'ed25519',
        'jms-utils >= 0.6.2',
        'pyinstaller >= 2.1',
        'requests',
        'six',
        'stevedore',
        ],
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    pyiupdater=pyi_updater.wrapper:main
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7'],
    )

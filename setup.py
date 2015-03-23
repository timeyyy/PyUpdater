#!/usr/bin/env python

from setuptools import Command, find_packages, setup
import subprocess
import sys

import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = 'pyupdater/_version.py'
versioneer.versionfile_build = 'pyupdater/_version.py'
versioneer.tag_prefix = ''  # tags are like 1.2.0
versioneer.parentdir_prefix = 'PyUpdater-'  # dirname like 'myproject-1.2.0'


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, u'runtests.py', u'-v', u'-x',
                                u'--cov', u'pyupdater', u'-n', u'4'])
        raise SystemExit(errno)


class PyTestCover(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, u'runtests.py', u'tests',
                                 u'--cov', u'pyupdater', u'-n', u'1'])
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
                                 u'pyupdater', u'-n', u'4'])
        raise SystemExit(errno)

with open(u'requirements.txt', u'r') as f:
    required = f.read().splitlines()

cmd_class = versioneer.get_cmdclass()
cmd_class.update({u'test': PyTest,
                  u'ctest': PyTestCover,
                  u'mytest': PyTestMyCover})

extra_s3 = 'PyUpdater-s3-Plugin == 2.1'
extra_scp = 'PyUpdater-scp-Plugin == 2.1'
extra_patch = 'bsdiff4 == 1.1.4'

setup(
    name='PyUpdater',
    version=versioneer.get_version(),
    description='Simple App update framwork',
    author='Johny Mo Swag',
    author_email='johnymoswag@gmail.com',
    url='docs.pyupdater.org',
    download_url=('https://github.com/JohnyMoSwag/Py'
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
    install_requires=required,
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    pyupdater=pyupdater.wrapper:main
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7'],
    )

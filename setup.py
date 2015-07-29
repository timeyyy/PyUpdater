#!/usr/bin/env python

from setuptools import Command, find_packages, setup
import subprocess
import sys

import versioneer


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, u'runtests.py', u'-x',
                                 u'-n', u'2'])
        raise SystemExit(errno)


class PyTestMyCover(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, u'runtests.py', u'tests',
                                 u'--cov-report', u'html', u'-n', u'4'])
        raise SystemExit(errno)

with open(u'requirements.txt', u'r') as f:
    required = f.read().splitlines()

cmd_class = versioneer.get_cmdclass()
cmd_class.update({u'test': PyTest,
                  u'mytest': PyTestMyCover})

extra_s3 = 'PyUpdater-s3-Plugin == 2.4'
extra_scp = 'PyUpdater-scp-Plugin == 2.2'
extra_patch = 'bsdiff4 == 1.1.4'

setup(
    name='PyUpdater',
    version=versioneer.get_version(),
    description='Simple App update framwork',
    author='Johny Mo Swag',
    author_email='johnymoswag@gmail.com',
    url='docs.pyupdater.org',
    download_url=('https://github.com/JMSwag/Py'
                  'Updater/archive/master.zip'),
    license='Apache License 2.0',
    extras_require={
        's3': extra_s3,
        'scp': extra_scp,
        'patch': extra_patch,
        'all': [extra_s3, extra_scp, extra_patch]
        },
    zip_safe=False,
    package_data={
        # This includes precompiled bootloaders.
        'pyupdater.vendor.PyInstaller': ['bootloader/*/*'],
        # This file is necessary for rthooks (runtime hooks).
        'pyupdater.vendor.PyInstaller.loader': ['rthooks.dat'],
        },
    include_package_data=True,
    tests_require=['pytest', extra_patch],
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

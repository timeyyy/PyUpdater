import os
import shutil
import tempfile

from pyupdater.utils.storage import Storage

import pytest


collect_ignore = [u"pyupdater/_version.py",
                  u"pyupdater/hooks/hook-cryptography",
                  u"pyupdater/hooks/hook-markdown"]


@pytest.fixture
def cleandir(request):
    newpath = tempfile.mkdtemp()

    def fin():
        os.chdir(os.path.dirname(os.getcwd()))
        shutil.rmtree(newpath, ignore_errors=True)
    request.addfinalizer(fin)
    os.chdir(newpath)


@pytest.fixture
def db():
    db = Storage()
    return db

import os
import shutil
import tempfile

from pyupdater.storage import Storage

import pytest


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

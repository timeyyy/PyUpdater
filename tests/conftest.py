import os
import shutil
import tempfile

from pyupdater import PyUpdater
from pyupdater.client import Client
from pyupdater.utils.storage import Storage
from pyupdater.wrapper.options import make_parser
from tconfig import TConfig

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
def client():
    t_config = TConfig()
    t_config.DATA_DIR = os.getcwd()
    client = Client(t_config, refresh=True, test=True)
    client.FROZEN = True
    return client


@pytest.fixture
def db():
    db = Storage()
    return db


@pytest.fixture
def parser():
    parser = make_parser()
    return parser


@pytest.fixture
def pyu():
    t_config = TConfig()
    t_config.DATA_DIR = os.getcwd()
    pyu = PyUpdater(t_config)
    return pyu

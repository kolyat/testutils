import pytest

from utils import client
import config


@pytest.fixture(scope='session')
def arclient():
    _client = client.ArClient()
    _client.login()
    yield _client
    _client.logout()


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(config.IMPLICIT_WAIT)
    # selenium.maximize_window()
    return selenium

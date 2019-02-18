import pytest
import settings


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(settings.IMPLICIT_WAIT)
    # selenium.maximize_window()
    return selenium

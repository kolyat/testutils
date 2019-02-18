import pytest
from . import models


@pytest.mark.parametrize('login,password', [('yauser', 'password')])
def test_login_ok(selenium, login, password):
    login_page = models.LoginPageModel(selenium)
    login_page.enter_login(login)
    login_page.enter_password(password)
    login_display = login_page.submit()
    assert login_display == login


@pytest.mark.parametrize('login,password', [('yauser', 'wrong_password')])
def test_wrong_password(selenium, login, password):
    login_page = models.LoginPageModel(selenium)
    login_page.enter_login(login)
    login_page.enter_password(password)
    login_page.submit()
    assert login_page.get_wrong_password_msg() == 'Неверный пароль'

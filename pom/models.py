from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait

import settings
from . import locators


class BaseModel:
    URL = None

    def __init__(self, driver):
        self.driver = driver

    def get_element(self, selector, path):
        try:
            element = WebDriverWait(
                driver=self.driver, timeout=settings.TIMEOUT,
                poll_frequency=settings.POLL_FREQUENCY
            ).until(lambda driver: driver.find_element(selector, path))
            return element
        except exceptions.TimeoutException:
            return None


class LoginPageModel(BaseModel,
                     locators.LoginPageLocators, locators.ProfilePageLocators):
    URL = 'https://passport.yandex.ru'

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(self.URL)
        self._login_field = self.get_element(*self.LOGIN_FIELD)
        self._password_field = None

    def enter_login(self, login):
        self._login_field.send_keys(login)
        self.submit()
        self._password_field = self.get_element(*self.PASSWORD_FIELD)

    def enter_password(self, password):
        self._password_field.send_keys(password)

    def submit(self):
        self.get_element(*self.SUBMIT_BUTTON).click()
        _login_label = self.get_element(*self.LOGIN_LABEL)
        if _login_label:
            return _login_label.text
        else:
            return None

    def get_wrong_password_msg(self):
        return self.get_element(*self.WRONG_PASSWORD_MSG).text

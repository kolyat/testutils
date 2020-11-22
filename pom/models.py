from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait

import config
from . import locators


class BaseModel:
    URL = None

    def __init__(self, driver):
        self.driver = driver

    def get_element(self, selector, path, timeout=config.TIMEOUT,
                    poll_frequency=config.POLL_FREQUENCY):
        try:
            element = WebDriverWait(driver=self.driver, timeout=timeout,
                                    poll_frequency=poll_frequency).until(
                lambda driver: driver.find_element(selector, path))
            return element
        except exceptions.TimeoutException:
            return None


class LoginPageModel(BaseModel,
                     locators.LoginPageLocators, locators.ProfilePageLocators):
    URL = 'https://passport.yandex.ru'

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(self.URL)

    def enter_login(self, login):
        self.get_element(*self.LOGIN_FIELD).send_keys(login)
        self.submit()

    def enter_password(self, password):
        self.get_element(*self.PASSWORD_FIELD).send_keys(password)

    def submit(self):
        self.get_element(*self.SUBMIT_BUTTON).click()
        _login_label = self.get_element(*self.LOGIN_LABEL)
        if _login_label:
            return _login_label.text
        else:
            return None

    def get_wrong_password_msg(self):
        return self.get_element(*self.WRONG_PASSWORD_MSG).text

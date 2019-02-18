from selenium.webdriver.common.by import By


class LoginPageLocators:
    LOGIN_FIELD = (By.ID, 'passp-field-login')
    PASSWORD_FIELD = (By.ID, 'passp-field-passwd')
    SUBMIT_BUTTON = (By.CSS_SELECTOR, 'div[class*="passp-sign-in-button"]>'
                                      'button[type="submit"]')
    WRONG_PASSWORD_MSG = (By.CSS_SELECTOR,
                          'div[class="passp-form-field__error"]')


class ProfilePageLocators:
    LOGIN_LABEL = (By.XPATH, '//div[@class="personal"]/div[1]/div[2]')

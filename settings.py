import logging

#
# Logging
#
LOG_OPTIONS = {
    'filemode': 'w',
    'format': '%(asctime)s [%(module)15s] %(levelname)7s - %(funcName)s - %(message)s',
    'level': logging.INFO
}

#
# Endpoints
#
# Relative paths (_PATH) are used in locust scenarios
# Absolute paths (_URL) are used in API tests
#
PROTOCOL = 'http://'
HOST = 'testhost'
BASE_URL = '{}{}'.format(PROTOCOL, HOST)

LOGIN_PATH = '/login'
LOGIN_URL = '{}{}'.format(BASE_URL, LOGIN_PATH)

LOGOUT_PATH = '/logout'
LOGOUT_URL = '{}{}'.format(BASE_URL, LOGOUT_PATH)

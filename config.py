from utils import service


#
# Defaults
#

DEFAULT_TARGET_CONFIG = {
    'default': {
        'protocol': 'http',
        'server': 'test.server',
        'api_version': 'v5',
        'users': {
            'default': {
                'username': 'bot',
                'userpass': 'password',
                'mail_server': 'outlook.office365.com'
            }
        },
        'platforms': {
            'default': {
                'name': 'bot_platform'
            }
        }
    }
}

DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s | [%(levelname)8s] | '
                      '%(module)s.%(funcName)s(%(lineno)d) - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO',
            'stream': 'ext://sys.stdout'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}


#
# Selenium
#

IMPLICIT_WAIT = 0
TIMEOUT = 5
POLL_FREQUENCY = 1


#
# Init
#

current_config = service.Config()
current_config.update_config('config.json')

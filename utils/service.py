from typing import Union
import os
import json
import logging
import http.client

import config


class Reader:
    """File parsing utility.
    Now supports only JSON files.
    """

    @staticmethod
    def read_json(file_name: str) -> Union[dict, None]:
        """Read JSON file.

        :param file_name: name of a JSON file
        :type file_name: str

        :return: deserialized JSON document
        :rtype: dict
        """
        _json = None
        try:
            fp = open(file_name)
            _json = json.load(fp)
            fp.close()
        except Exception as e:
            print(f'Error in processing {file_name}')
            print(e)
        return _json


class Config(dict):
    """Class for storing configuration options.

    * **target** - testing object/server data
    * **logging** - various logging options
    """

    def __init__(self):
        super().__init__()
        self['target'] = config.DEFAULT_TARGET_CONFIG.copy()
        self['logging'] = config.DEFAULT_LOGGING_CONFIG.copy()

    def update_config(self, config_file: str) -> None:
        """Load and update configuration options from a file.

        :param config_file: config file name
        :type config_file: str
        """
        _config = None
        _, ext = os.path.splitext(config_file)
        if ext == '.json':
            _config = Reader.read_json(config_file)
        else:
            print(f'Configuration file {config_file} is not supported')
        self.target.update(_config.get('target', {}))
        self.logging.update(_config.get('logging', {}))

    @property
    def target(self) -> dict:
        """
        :return: testing object/server data
        :rtype: dict
        """
        return self['target']

    @property
    def logging(self) -> dict:
        """
        :return: logging options
        :rtype: dict
        """
        return self['logging']

    def api_uri(self, target: str = 'default') -> str:
        """Get API URI

        :param target: testing target (set to "default")
        :type target: str

        :return: API URI (e. g., "https://api.test.server/v5")
        :rtype: str
        """
        _target = self.target[target]
        _api_uri = ''.join((_target['protocol'], '://api.', _target['server'],
                            '/', _target['api_version']))
        return _api_uri

    def admin_uri(self, target: str = 'default') -> str:
        """Get URI of administration panel

        :param target: testing target (set to "default")
        :type target: str

        :return: admin URI (e. g., "https://root.test.server")
        :rtype: str
        """
        _target = self.target[target]
        _admin_uri = ''.join((_target['protocol'], '://root.',
                              _target['server']))
        return _admin_uri

    def ucp_uri(self, target: str = 'default') -> str:
        """Get URI of User Control Panel

        :param target: testing target (set to "default")
        :type target: str

        :return: UCP URI (e. g., "https://id.test.server")
        :rtype: str
        """
        _target = self.target[target]
        _ucp_uri = ''.join((_target['protocol'], '://id.', _target['server']))
        return _ucp_uri

    def platform_uri(self, target: str = 'default',
                     platform: str = 'default') -> str:
        """Get URI of a platform

        :param target: testing target (set to "default")
        :type target: str

        :param platform: selected platform (set to "default")
        :type platform: str

        :return: platform URI (e. g., "https://myspace.test.server")
        :rtype: str
        """
        _target = self.target[target]
        _platform = _target['platforms'][platform]['name']
        _platform_uri = ''.join((_target['protocol'], f'://{_platform}.',
                                 _target['server']))
        return _platform_uri

    def get_user(self, target: str = 'default', user: str = 'default') -> dict:
        """Get user's registration data

        :param target: testing target (set to "default")
        :type target: str

        :param user: selected user (set to "default")
        :type user: str

        :return: user's registration data
        :rtype: dict
        """
        _target = self.target[target]
        _user = _target['users'][user]
        return _user


httpclient_logger = logging.getLogger('http.client')


def httpclient_logging_patch(level: int = logging.DEBUG) -> None:
    """Enable HTTPConnection debug logging to the logging framework

    :param level: logging level (logging.DEBUG = 10 by default)
    :type level: int
    """

    def httpclient_log(*args: Any) -> None:
        httpclient_logger.log(level, ' '.join(args))

    http.client.print = httpclient_log
    http.client.HTTPConnection.debuglevel = 1

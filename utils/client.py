from typing import Tuple, Union, Any
import re
import json
import logging.config
import logging
from http.client import responses
import imapclient
import email
import keyring
import requests
import locust

import config
from . import urls


logging.config.dictConfig(config.current_config.logging)
logger = logging.getLogger(__name__)


class EmailClient:
    """Client for e-mail processing.
    Now supports only IMAP4 protocol (over SSL).

    :ivar client: e-mail client instance
    :ivar current_folder: current selected folder in mailbox
    """

    def __init__(self, host: str, port: int = 993):
        """
        :param host: IMAP server
        :type host: str

        :param port: IMAP port (993 by default)
        :type port: int
        """
        self.client = imapclient.IMAPClient(host, port, ssl=True)
        self.current_folder = None

    def login(self, username: str):
        """Perform log-in to IMAP server.
        Password is retrieved automatically from local keyring storage.

        :param username: user's name / e-mail address
        :type username: str
        """
        self.client.login(username, keyring.get_password('system', username))

    def logout(self):
        """Perform log-out from IMAP server.
        """
        self.client.logout()

    def find_recovery_mail(self) -> Union[int, None]:
        """Search for latest password recovery mail.

        :return: mail's UID
        :rtype: int
        """
        inbox = 'INBOX'
        if self.current_folder != inbox:
            self.client.select_folder(inbox)
            self.current_folder = inbox
            logger.info(f'Go to {inbox}')
        try:
            uid = max(self.client.search(['UNSEEN', 'TEXT', 'sendgrid']))
            logger.info(f'Found latest recovery mail: UID #{uid}')
        except ValueError:
            uid = None
        return uid

    def get_recovery_link(self, uid: int) -> Union[str, None]:
        """Extract URL for password recovery from e-mail message.

        :param uid: mail's UID
        :type uid: int

        :return: password recovery URL
        :rtype: str
        """
        data = self.client.fetch(uid, 'RFC822')
        raw_msg = data[uid]
        decoded_msg = email.message_from_bytes(raw_msg[b'RFC822'])
        body = str(decoded_msg.get_payload(decode=True))
        try:
            r = re.search(r'href="(\S+sendgrid\S+)" target', body).group(1)
            logger.info(f'Found password recovery link: {r}')
        except AttributeError:
            logger.warning(f'Password recovery link was not found in #{uid}')
            r = None
        return r


class HTTPClient:
    """Base HTTP client.

    :ivar session: :class:`requests.Session` instance
    :ivar latest_response: latest received :class:`requests.Response` object
    """

    def __init__(self):
        self.session = requests.Session()
        self.latest_response = None

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper for :class:`requests.Session.get()` method with extended
        logging.

        :param url: target URL
        :type url: str

        :param kwargs: optional arguments that
                       :class:`requests.Session.request()` takes.

        :return: response object
        :rtype: requests.Response
        """
        logger.debug(f'GET {url}')
        response = self.session.get(url, **kwargs)
        logger.debug(f'{response.status_code}: '
                     f'{responses.get(response.status_code, "<unknown>")}')
        if response.text != '':
            logger.debug(f'Body: {response.text}')
        else:
            logger.debug('No body')
        self.latest_response = response
        return response

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper for :class:`requests.Session.post()` method with extended
        logging.

        :param url: target URL
        :type url: str

        :param kwargs:
        * **data** (optional) - dictionary, list of tuples, bytes, or file-like
          object to send in the body of the request
        * **json** (optional) - json to send in the body of the request
        * other optional arguments that :class:`requests.Session.request()`
          takes.

        :return: response object
        :rtype: requests.Response
        """
        logger.debug(f'POST {url}')
        if kwargs.get('json', None):
            logger.debug(f'Body (JSON): {json.dumps(kwargs["json"])}')
        elif kwargs.get('data', None):
            logger.debug(f'Body (data): {str(kwargs["data"])}')
        else:
            logger.debug('No body')
        response = self.session.post(url, **kwargs)
        logger.debug(f'{response.status_code}: '
                     f'{responses.get(response.status_code, "<unknown>")}')
        if response.text != '':
            logger.debug(f'Body: {response.text}')
        else:
            logger.debug('No body')
        self.latest_response = response
        return response

    def put(self, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper for :class:`requests.Session.put()` method with extended
        logging.

        :param url: target URL
        :type url: str

        :param kwargs:
        * **data** (optional) - dictionary, list of tuples, bytes, or file-like
          object to send in the body of the request
        * **json** (optional) - json to send in the body of the request
        * other optional arguments that :class:`requests.Session.request()`
          takes.

        :return: response object
        :rtype: requests.Response
        """
        logger.debug(f'PUT {url}')
        if kwargs.get('json', None):
            logger.debug(f'Body (JSON): {json.dumps(kwargs["json"])}')
        elif kwargs.get('data', None):
            logger.debug(f'Body (data): {str(kwargs["data"])}')
        else:
            logger.debug('No body')
        response = self.session.put(url, **kwargs)
        logger.debug(f'{response.status_code}: '
                     f'{responses.get(response.status_code, "<unknown>")}')
        if response.text != '':
            logger.debug(f'Body: {response.text}')
        else:
            logger.debug('No body')
        self.latest_response = response
        return response


class ArClient(HTTPClient):
    """REST API client with both basic and multistep authentication support.

    :ivar session_ids: list for storing session ID's
    """

    def __init__(self):
        super().__init__()
        self.session_ids = []

    @property
    def access_token(self) -> str:
        """
        :return: access token
        :rtype: str
        """
        access_token = self.session.cookies.get('access_token')
        logger.debug(f'Access token: {access_token}')
        return access_token

    @property
    def refresh_token(self) -> str:
        """
        :return: refresh token
        :rtype: str
        """
        refresh_token = self.session.cookies.get('refresh_token')
        logger.debug(f'Refresh token: {refresh_token}')
        return refresh_token

    #
    # Basic authentication
    #

    def basic_login(self, **kwargs: Any) -> \
            Tuple[requests.Response, Union[str, None], Union[str, None]]:
        """Basic authentication: log in.

        :param kwargs:
        * **json** (optional) - json to send in the body of the request

        :return: response object, access and refresh tokens
        :rtype: Tuple[requests.Response, Union[str, None], Union[str, None]]
        """
        url = config.current_config.api_uri() + urls.AUTH_BASIC_LOGIN
        login = config.current_config.get_user()['username']
        password = config.current_config.get_user()['userpass']
        _json = kwargs.get('json', None)
        payload = _json if _json else {'email': login, 'password': password}
        logger.info(f'Basic auth: log in under {login}')
        response = self.post(url, json=payload)
        if response.status_code != 200:
            logger.warning('Basic auth failed')
        else:
            logger.info('Basic auth passed')
        return response, self.access_token, self.refresh_token

    #
    # Multistep authentication
    #

    def get_session_id(self) -> Tuple[requests.Response, Union[str, None]]:
        """1-st step of multistep authentication: get session ID.

        :return: tuple with response and session id
        :rtype: Tuple[requests.Response, Union[str, None]
        """
        url = config.current_config.api_uri() + urls.AUTH_STEP_START
        logger.info('Get auth session ID')
        response = self.post(url)
        session_id = None
        if response.text != '':
            try:
                session_id = response.json()['session_id']
                logger.info(f'Got session ID: {session_id}')
            except ValueError as e:
                logger.error('Invalid JSON in response')
                logger.error(e)
            except KeyError as e:
                logger.error('Session ID not found')
                logger.error(e)
        else:
            logger.error('Unable to get session ID: empty body in response')
        self.session_ids.append(session_id)
        return response, session_id

    def check_login(self, **kwargs: Any) -> requests.Response:
        """2-nd step of multistep authentication: check login.

        :param kwargs:
        * **json** (optional) - json to send in the body of the request

        :return: response object
        :rtype: requests.Response
        """
        url = config.current_config.api_uri() + urls.AUTH_STEP_CHECK_LOGIN
        login = config.current_config.get_user()['username']
        session_id = self.session_ids[-1]
        _json = kwargs.get('json', None)
        payload = _json if _json \
            else {'session_id': session_id, 'login': login}
        logger.info(f'Check login: {login}')
        response = self.post(url, json=payload)
        if response.status_code != 200:
            logger.warning('Check login failed')
        else:
            logger.info('Check login OK')
        return response

    def check_password(self, **kwargs: Any) -> requests.Response:
        """3-rd step of multistep authentication: check password.

        :param kwargs:
        * **json** (optional) - json to send in the body of the request

        :return: response object
        :rtype: requests.Response
        """
        url = config.current_config.api_uri() + urls.AUTH_STEP_CHECK_PASSWORD
        password = config.current_config.get_user()['userpass']
        session_id = self.session_ids[-1]
        _json = kwargs.get('json', None)
        payload = _json if _json \
            else {'session_id': session_id, 'password': password}
        logger.info(f'Check password: {password}')
        response = self.post(url, json=payload)
        if response.status_code != 200:
            logger.warning('Check password failed')
        else:
            logger.info('Check password OK')
        return response

    def finish_auth(self, **kwargs: Any) -> \
            Tuple[requests.Response, Union[str, None], Union[str, None]]:
        """4-th step of multistep authentication: finish authentication.

        :param kwargs:
        * **json** (optional) - json to send in the body of the request

        :return: response object, access and refresh tokens
        :rtype: Tuple[requests.Response, Union[str, None], Union[str, None]]
        """
        url = config.current_config.api_uri() + urls.AUTH_STEP_FINISH
        session_id = self.session_ids[-1]
        _json = kwargs.get('json', None)
        payload = _json if _json else {'session_id': session_id}
        logger.info(f'Finishing auth')
        response = self.post(url, json=payload)
        if response.status_code != 200:
            logger.warning('Authentication failed')
        else:
            logger.info('Authentication passed')
        return response, self.access_token, self.refresh_token

    #
    # Combined authentication methods
    #

    def login(self, auth: str = 'multistep') -> None:
        """Combined log-in method with both basic and multistep authentication
        support.

        :param auth: authentication type: "basic", "multistep"
        :type auth: str
        """
        if auth == 'basic':
            self.basic_login()
        elif auth == 'multistep':
            self.get_session_id()
            self.check_login()
            self.check_password()
            self.finish_auth()
        else:
            logger.error(f'Unknown type of auth: {auth}')
        return

    def logout(self) -> requests.Response:
        """Log out from system.

        :return: response object
        :rtype: requests.Response
        """
        url = config.current_config.api_uri() + urls.AUTH_LOGOUT
        logger.info('Log out...')
        response = self.post(url)
        if response.status_code != 200:
            logger.warning('Logout failed')
        else:
            logger.info('Logout completed')
        return response

    #
    # Response headers verification
    #

    def check_cache_control(self) -> bool:
        """Validate *Cache-Control* header.

        :return: result (False by default)
        :rtype: bool
        """
        params = ('private', 'no-cache', 'no-store', 'must-revalidate',
                  'max-age=0')
        logging.info(f'Check header Cache-Control: {", ".join(params)}')
        result = False
        _header = self.latest_response.headers.get('Cache-Control', False)
        if _header:
            c = [p in _header for p in params]
            if all(c):
                logger.info('Cache-Control OK')
                result = True
            else:
                logger.warning(f'Cache-Control expected: {", ".join(params)}')
                logger.warning(f'Cache-Control actual: {_header}')
        else:
            logger.warning('Response header Cache-Control is not found')
        return result

    def check_pragma(self) -> bool:
        """Validate *Pragma* header.

        :return: result (False by default)
        :rtype: bool
        """
        logging.info('Check header Pragma: no-cache')
        result = False
        _header = self.latest_response.headers.get('Pragma', False)
        if _header:
            if 'no-cache' in _header:
                logger.info('Pragma OK')
                result = True
            else:
                logger.warning('Pragma expected: no-cache')
                logger.warning(f'Pragma actual: {_header}')
        else:
            logger.warning('Response header Pragma is not found')
        return result


class ArClientPasswdRecovery(ArClient):
    """Derived class from :class:`ArClient` with password recovery methods.

    :ivar passwd_session_ids: list of session ID's for password recovery
    :ivar secret_keys: list of secret_keys for password recovery
    """

    def __init__(self):
        super().__init__()
        self.passwd_session_ids = []
        self.secret_keys = []

    def passwd_get_session_id(self) \
            -> Tuple[requests.Response, Union[str, None]]:
        """1-st step of password recovery: get session ID.

        :return: tuple with response and session id
        :rtype: Tuple[requests.Response, Union[str, None]
        """
        url = config.current_config.api_uri() + urls.PASSWD_START
        logger.info('Password recovery: get session ID')
        response = self.post(url)
        session_id = None
        if response.text != '':
            try:
                session_id = response.json()['session_id']
                logger.info(f'Password recovery: session ID: {session_id}')
            except ValueError as e:
                logger.error('Password recovery: invalid JSON in response')
                logger.error(e)
            except KeyError as e:
                logger.error('Password recovery: session ID not found')
                logger.error(e)
        else:
            logger.error('Password recovery: unable to get session ID - '
                         'empty body in response')
        self.passwd_session_ids.append(session_id)
        return response, session_id

    def passwd_check_login(self, **kwargs: Any) -> requests.Response:
        """2-nd step of password recovery: check login.

        :param kwargs:
        * **json** (optional) - json to send in the body of the request

        :return: response object
        :rtype: requests.Response
        """
        url = config.current_config.api_uri() + urls.PASSWD_CHECK_LOGIN
        login = config.current_config.get_user()['username']
        session_id = self.passwd_session_ids[-1]
        _json = kwargs.get('json', None)
        payload = _json if _json \
            else {'session_id': session_id, 'login': login}
        logger.info(f'Password recovery: check login {login}')
        response = self.post(url, json=payload)
        if response.status_code != 200:
            logger.warning('Password recovery: login checking failed')
        else:
            logger.info('Password recovery: login checking OK')
        return response

    def passwd_send_mail(self, **kwargs: Any) -> requests.Response:
        """3-rd step of password recovery: send e-mail.

        :param kwargs:
        * **json** (optional) - json to send in the body of the request

        :return: response object
        :rtype: requests.Response
        """
        url = config.current_config.api_uri() + urls.PASSWD_SEND_MAIL
        session_id = self.passwd_session_ids[-1]
        _json = kwargs.get('json', None)
        payload = _json if _json else {'session_id': session_id}
        logger.info('Password recovery: send e-mail')
        response = self.post(url, json=payload)
        if response.status_code != 200:
            logger.warning('Password recovery: sending failed')
        else:
            logger.info('Password recovery: sending passed')
        return response

    def passwd_check_key(self, **kwargs: Any) -> requests.Response:
        """4-th step of password recovery: check secret key.

        :param kwargs:
        * **key_link** (optional) - URL to retrieve secret key
        * **secret_key** (optional) - secret key
        * **json** (optional) - json to send in the body of the request

        :return: response object
        :rtype: requests.Response
        """
        url = config.current_config.api_uri() + urls.PASSWD_CHECK_KEY
        session_id = self.session_ids[-1]
        payload = {'session_id': session_id}
        if kwargs.get('key_link', None):
            response = self.get(kwargs['key_link'], allow_redirects=False)
            location = response.headers.get('Location', '')
            try:
                secret_key = re.search(r'secret_key=(\S+)$', location).group(1)
                logging.info(f'Password recovery: '
                             f'retrieved secret key: {secret_key}')
                payload.update({'secret_key': secret_key})
                self.secret_keys.append(secret_key)
            except AttributeError:
                logging.warning('Password recovery: failed to get secret key')
        elif kwargs.get('secret_key', None):
            payload.update({'secret_key': kwargs['secret_key']})
        elif kwargs.get('json', None):
            payload = kwargs['json']
        else:
            pass
        logger.info('Password recovery: check secret key')
        response = self.post(url, json=payload)
        if response.status_code != 200:
            logger.warning('Password recovery: secret key checking failed')
        else:
            logger.info('Password recovery: secret key checking passed')
        return response

    def passwd_finish(self, **kwargs: Any) -> requests.Response:
        """5-th step of password recovery: set up new password.

        :param kwargs:
        * **password** (optional) - new password
        * **json** (optional) - json to send in the body of the request

        :return: response object
        :rtype: requests.Response
        """
        url = config.current_config.api_uri() + urls.PASSWD_FINISH
        session_id = self.passwd_session_ids[-1]
        secret_key = self.secret_keys[-1]
        payload = {'session_id': session_id, 'secret_key': secret_key}
        if kwargs.get('password', None):
            payload.update({'password': kwargs['password']})
        elif kwargs.get('json', None):
            payload = kwargs['json']
        else:
            pass
        logger.info('Password recovery: set up new password')
        response = self.post(url, json=payload)
        if response.status_code != 200:
            logger.warning('Password recovery: failed to set up new password')
        else:
            logger.info('Password recovery procedure finished')
        return response


class LoadClient(locust.TaskSet, ArClient):
    """Base client class for load testing purposes
    """

    def on_start(self):
        """Log into system before start
        """
        # TODO: switch off logging
        # TODO: parametrize login
        self.login()

import logging.config
import logging
import re
import pytest

import config
from utils.codes import API_CODES
from utils import client, rnd


logging.config.dictConfig(config.current_config.logging)
logger = logging.getLogger(__name__)


def test_auth_start():
    """Test 1-st step of multistep authentication.
    """
    _client = client.ArClient()
    response, session_id = _client.get_session_id()
    assert response.status_code == 200
    assert _client.check_cache_control()
    assert _client.check_pragma()
    assert session_id is not None and session_id != ''
    assert re.match(r'[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}', session_id) \
           is not None


def test_auth_check_login():
    """Test 2-nd step of multistep authentication.
    """
    _client = client.ArClient()
    _client.get_session_id()
    response = _client.check_login()
    assert response.status_code == 200
    assert _client.check_cache_control()
    assert _client.check_pragma()


@pytest.mark.parametrize(
    'payload, response_code, api_code',
    [
        ({'session_id': rnd.random_session_id(), 'login': None}, 404, 1999),
        ({'session_id': 667,                     'login': None}, 400, 2011),
        ({'session_id': '',                      'login': None}, 404, 1999),
        ({                                       'login': None}, 404, 1999),
        ({'session_id': None, 'login': rnd.random_str()}, 404, 1130),
        ({'session_id': None, 'login': 667},              400, 2011),
        ({'session_id': None, 'login': ''},               404, 1130),
        ({'session_id': None},                            404, 1130),
    ]
)
def test_auth_check_login_negative(payload: dict,
                                   response_code: int, api_code: int):
    """Negative tests for 2-nd step of multistep authentication.

    :param payload: request's payload
    :type payload: dict

    :param response_code: server's response code
    :type response_code: int

    :param api_code: API's error code
    :type api_code: int
   """
    _client = client.ArClient()
    _, session_id = _client.get_session_id()
    if 'session_id' in payload and payload.get('session_id', False) is None:
        payload['session_id'] = session_id
    login = config.current_config.get_user()['username']
    if 'login' in payload and payload.get('login', False) is None:
        payload['login'] = login
    response = _client.check_login(json=payload)
    body = response.json()
    assert response.status_code == response_code
    assert body.get('code', None) == api_code
    assert body.get('key', None) == API_CODES[api_code]


def test_auth_check_login_previous_session_id():
    """Test 2-nd step with previous session ID.
    """
    _client = client.ArClient()
    _, previous_session_id = _client.get_session_id()
    _client.get_session_id()
    login = config.current_config.get_user()['username']
    response = _client.check_login(json={'session_id': previous_session_id,
                                         'login': login})
    body = response.json()
    assert response.status_code == 404
    assert body.get('code', None) == 1999
    assert body.get('key', None) == API_CODES[1999]


def test_auth_check_password():
    """Test 3-rd step of multistep authentication.
    """
    _client = client.ArClient()
    _client.get_session_id()
    _client.check_login()
    response = _client.check_password()
    assert response.status_code == 200
    assert _client.check_cache_control()
    assert _client.check_pragma()


@pytest.mark.parametrize(
    'payload, response_code, api_code',
    [
        ({'session_id': rnd.random_session_id(), 'password': None}, 404, 1999),
        ({'session_id': 667,                     'password': None}, 400, 2011),
        ({'session_id': '',                      'password': None}, 404, 1999),
        ({                                       'password': None}, 404, 1999),
        ({'session_id': None, 'password': rnd.random_str()}, 400, 2110),
        ({'session_id': None, 'password': 667},              400, 2011),
        ({'session_id': None, 'password': ''},               400, 2110),
        ({'session_id': None},                               400, 2110),
    ]
)
def test_auth_check_password_negative(payload: dict,
                                      response_code: int, api_code: int):
    """Negative tests for 3-rd step of multistep authentication.

    :param payload: request's payload
    :type payload: dict

    :param response_code: server's response code
    :type response_code: int

    :param api_code: API's error code
    :type api_code: int
   """
    _client = client.ArClient()
    _, session_id = _client.get_session_id()
    _client.check_login()
    if 'session_id' in payload and payload.get('session_id', False) is None:
        payload['session_id'] = session_id
    password = config.current_config.get_user()['userpass']
    if 'password' in payload and payload.get('login', False) is None:
        payload['password'] = password
    response = _client.check_password(json=payload)
    body = response.json()
    assert response.status_code == response_code
    assert body.get('code', None) == api_code
    assert body.get('key', None) == API_CODES[api_code]


def test_auth_check_password_previous_session_id():
    """Test 3-rd step with previous session ID.
    """
    _client = client.ArClient()
    _, previous_session_id = _client.get_session_id()
    _client.check_login()
    _client.get_session_id()
    password = config.current_config.get_user()['userpass']
    response = _client.check_password(json={'session_id': previous_session_id,
                                            'password': password})
    body = response.json()
    assert response.status_code == 404
    assert body.get('code', None) == 1999
    assert body.get('key', None) == API_CODES[1999]


def test_auth_check_incomplete_password():
    """Test 3-rd step with incomplete password.
    """
    _client = client.ArClient()
    _, session_id = _client.get_session_id()
    _client.check_login()
    password = config.current_config.get_user()['userpass'][1:-2]
    response = _client.check_password(json={'session_id': session_id,
                                            'password': password})
    body = response.json()
    assert response.status_code == 400
    assert body.get('code', None) == 2110
    assert body.get('key', None) == API_CODES[2110]


def test_auth_check_finish():
    """Test 4-th step of multistep authentication.
    """
    _client = client.ArClient()
    _client.get_session_id()
    _client.check_login()
    _client.check_password()
    response, access_token, refresh_token = _client.finish_auth()
    assert response.status_code == 200
    assert access_token
    assert refresh_token
    assert _client.check_cache_control()
    assert _client.check_pragma()


def test_auth_skip_password_check():
    """Test with skipping password check.
    """
    _client = client.ArClient()
    _client.get_session_id()
    _client.check_login()
    response, access_token, refresh_token = _client.finish_auth()
    body = response.json()
    assert response.status_code == 400
    assert body.get('code', None) == 6000
    assert body.get('key', None) == API_CODES[6000]
    assert not access_token
    assert not refresh_token

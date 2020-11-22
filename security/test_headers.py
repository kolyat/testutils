import pytest

import config


@pytest.mark.parametrize('url', [
        config.current_config.admin_uri(),
        config.current_config.ucp_uri(),
        config.current_config.platform_uri()
    ]
)
def test_xss(arclient, url):
    """Test Cross-Site Scripting protection.
    """
    response = arclient.get(url)
    assert response.status_code == 200
    _header = response.headers.get('X-XSS-Protection')
    assert '1' in _header
    assert 'mode=block' in _header
    _header = response.headers.get('X-Content-Type-Options')
    assert 'nosniff' in _header
    _header = response.headers.get('X-Frame-Option')
    assert 'DENY' in _header


@pytest.mark.parametrize('url', [
        config.current_config.admin_uri(),
        config.current_config.ucp_uri(),
        config.current_config.platform_uri()
    ]
)
def test_csp(arclient, url):
    """Test Content Security Policy.
    """
    response = arclient.get(url)
    assert response.status_code == 200
    _header = response.headers.get('Content-Security-Policy')
    assert "default-src * data: blob: about:" in _header
    assert "script-src 'unsafe-inline' 'unsafe-eval' 'self'" in _header
    assert "style-src 'unsafe-inline' 'self'" in _header
    assert "img-src 'self' data: blob:" in _header


@pytest.mark.parametrize('url', [
        config.current_config.admin_uri(),
        config.current_config.ucp_uri(),
        config.current_config.platform_uri()
    ]
)
def test_hsts(arclient, url):
    """Test HTTP Strict Transport Security (HSTS).
    """
    response = arclient.get(url)
    assert response.status_code == 200
    _header = response.headers.get('Strict-Transport-Security')
    assert 'max-age=31536000' in _header
    assert 'includeSubDomains' in _header

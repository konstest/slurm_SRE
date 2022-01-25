import pytest
import src.api


@pytest.fixture(scope='function', autouse=True)
def mock_auth_service_call(monkeypatch):
    monkeypatch.setattr(src.api, 'get_auth_header', get_auth_header)
    monkeypatch.setattr(src.api.movies, 'get_auth_header', get_auth_header)
    monkeypatch.setattr(src.api.bookings, 'get_auth_header', get_auth_header)
    pass


async def get_auth_header(*_, **__):
    return {'X-Auth-Operation-Id': 'TEST'}

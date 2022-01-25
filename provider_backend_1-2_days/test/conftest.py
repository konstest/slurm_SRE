import asyncio
import logging
from os import getenv
from aiohttp import web
from aioprometheus import Counter
import pytest
from src.main import read_schemas
import random


@pytest.yield_fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def loop(event_loop):
    return event_loop


@pytest.fixture
def create_mocked_app(primary_db_conn_pool, secondary_db_conn_pool, event_loop):
    def impl(router_impl):
        app = web.Application(loop=event_loop)
        router_impl(app)
        app['primary_db_conn_pool'] = primary_db_conn_pool
        app['secondary_db_conn_pool'] = secondary_db_conn_pool
        app['default_headers'] = pytest.default_headers
        app['schemas'] = pytest.schemas
        app['success_bookings_total'] = Counter("success_bookings_total_random_{}".format(random.randint(0, 100000000)), 'The total number of successfull bookings')
        app['logger'] = logging.getLogger()
        return app
    return impl


pytest_plugins = [
    "test.tests.fixtures.booking",
    "test.tests.fixtures.db",
    "test.tests.fixtures.mock_calls",
    "test.tests.fixtures.movie",
    "test.tests.fixtures.seance",
    "test.tests.fixtures.seats",
    "aiohttp.pytest_plugin"
]


def pytest_configure():
    pytest.postgresql_credentials = f"dbname=provider_development user=postgres password=Gj7BDvmL8SD host={getenv('TEST_POSTGRES_HOST', '127.0.0.1')} port=5432"

    pytest.default_headers = {'charset': 'utf-8'}

    pytest.schemas = dict(read_schemas())

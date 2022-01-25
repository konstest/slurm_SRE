import asyncio
import hamcrest as hc
import psycopg2
import psycopg2.extras
import pytest
import src.api
from src.api import movies


@pytest.fixture(scope='function')
async def create_movie(request: pytest.fixture, create_mocked_app, aiohttp_client, event_loop):
    app = create_mocked_app(lambda app: app.router.add_post('/movies',
                                                            movies.create_movie.__wrapped__.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)

    payload = {
        "name": "Test Movie",
        "description": "Test description",
        "image_url": "http://example.com/test_image.jpeg"
    }
    response = await client.post('/movies', json=payload)
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    hc.assert_that(response_data['data'], hc.has_key(hc.equal_to('id')))
    movie_id = response_data['data']['id']
    hc.assert_that(response_data, hc.has_entries({"data": hc.has_entries({
        "type": "movies",
        "attributes": hc.has_entries(payload),
    })}))
    cnx = psycopg2.connect(pytest.postgresql_credentials)
    cursor = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(R'''
        SELECT * FROM movies WHERE id = %(id)s  
    ''', {'id': movie_id})
    payload['id'] = movie_id
    data = cursor.fetchone()
    hc.assert_that(payload, hc.equal_to(data))
    cnx.commit()
    cursor.close()
    cnx.close()

    def fin(movie_id):
        async def afin(movie_id):
            await delete_movie(movie_id, aiohttp_client, create_mocked_app)
        event_loop.run_until_complete(afin(movie_id))

    request.addfinalizer(lambda: fin(movie_id))
    return movie_id


async def delete_movie(movie_id, aiohttp_client, create_mocked_app):
    app = create_mocked_app(lambda app: app.router.add_delete('/movies/{movie_id}',
                                                              movies.delete_movie.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)

    response = await client.delete(f'/movies/{movie_id}')
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({"data": hc.has_entries({
        "id": str(movie_id),
        "type": "movies",
    })}))
    cnx = psycopg2.connect(pytest.postgresql_credentials)
    cursor = cnx.cursor()
    cursor.execute(R'''
        SELECT * FROM movies WHERE id = %(id)s  
    ''', {'id': movie_id})
    data = cursor.fetchone()
    hc.assert_that(data, hc.none())
    cnx.commit()
    cursor.close()
    cnx.close()


create_another_movie = create_movie

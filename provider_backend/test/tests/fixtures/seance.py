import asyncio
import hamcrest as hc
import psycopg2
import psycopg2.extras
import pytest
from src.api import movies


@pytest.fixture(scope='function')
async def create_seance(request: pytest.fixture, create_mocked_app, aiohttp_client, create_seats, event_loop,
                        monkeypatch):
    async def impl(movie_id, datetime_val: str):
        app = create_mocked_app(lambda app: app.router.add_post('/movies/{movie_id}/seances',
                                                                movies.create_movie_seance.__wrapped__.__wrapped__.__wrapped__))
        client = await aiohttp_client(app)

        payload = {"datetime": datetime_val,
                   "price": 250}
        seats = [{'id': seat_id, 'vacant': True} for seat_id in create_seats]
        response = await client.post(f'/movies/{movie_id}/seances', json=payload)
        hc.assert_that(response.status, hc.equal_to(200))
        response_data = await response.json()
        hc.assert_that(response_data['data'], hc.has_key(hc.equal_to('id')))
        seance_id = response_data['data']['id']
        hc.assert_that(response_data, hc.has_entries({"data": hc.has_entries({
            "type": "seances",
            "attributes": hc.has_entries(payload),
            "seats": hc.has_items(*seats)
        })}))
        cnx = psycopg2.connect(pytest.postgresql_credentials)
        cursor = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(R'''
            SELECT * FROM seances WHERE id = %(id)s  
        ''', {'id': seance_id})
        payload['id'] = seance_id
        payload['movie_id'] = movie_id
        data = cursor.fetchone()
        data['datetime'] = data['seance_datetime'].strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        data['price'] = int(data['price'])
        del data['seance_datetime']
        hc.assert_that(payload, hc.equal_to(data))
        cnx.commit()
        cursor.close()
        cnx.close()

        def fin(movie, seance):
            async def afin(movie, seance):
                await delete_seance(movie, seance, aiohttp_client, create_mocked_app)

            event_loop.run_until_complete(afin(movie, seance))

        request.addfinalizer(lambda: fin(movie_id, seance_id))
        return seance_id

    return impl


async def delete_seance(movie_id, seance_id, aiohttp_client, create_mocked_app):
    app = create_mocked_app(lambda app: app.router.add_delete('/movies/{movie_id}/seances/{seance_id}',
                                                              movies.delete_movie_seance.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    response = await client.delete(f'/movies/{movie_id}/seances/{seance_id}')
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({"data": hc.has_entries({
        "id": str(seance_id),
        "type": "seances",
    })}))
    cnx = psycopg2.connect(pytest.postgresql_credentials)
    cursor = cnx.cursor()
    cursor.execute(R'''
        SELECT * FROM seances WHERE id = %(id)s  
    ''', {'id': seance_id})
    data = cursor.fetchone()
    hc.assert_that(data, hc.none())
    cursor.close()
    cnx.close()


create_another_seance = create_seance

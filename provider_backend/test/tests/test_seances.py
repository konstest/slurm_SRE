import datetime
from aiohttp import web
import hamcrest as hc
import pytest
from src.api import movies as movies_api


@pytest.mark.asyncio
async def test_get_seances(create_movie, create_seance, create_another_seance, create_seats, create_another_movie,
                           aiohttp_raw_server, aiohttp_client, create_mocked_app):

    def routes(app):
        app.router.add_get('/movies/{movie_id}/seances',
                           movies_api.get_movie_seances.__wrapped__.__wrapped__)
        app.router.add_get('/movies',
                           movies_api.get_movies.__wrapped__.__wrapped__)

    app = create_mocked_app(routes)
    client = await aiohttp_client(app)
    seance_datetime = "2020-01-18T00:00:00.000Z"
    seance = await create_seance(create_movie, seance_datetime)
    another_seance_datetime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '.000Z'
    another_seance = await create_another_seance(create_movie, another_seance_datetime)
    response = await client.get(f'/movies/{create_movie}/seances')
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_key(hc.equal_to('data')))
    seances = response_data['data']
    hc.assert_that(seances, hc.has_length(2))
    seats = [{'id': seat_id, 'vacant': True} for seat_id in create_seats]
    seance_data = {"id": seance,
                   "price": 250,
                   "datetime": seance_datetime,
                   "seats": seats}
    another_seance_data = {"id": another_seance,
                           "price": 250,
                           "datetime": another_seance_datetime,
                           "seats": seats
                           }
    hc.assert_that(seances, hc.has_items(seance_data, another_seance_data))

    response = await client.get(f'/movies/{create_movie}/seances?max_results=1')
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_key(hc.equal_to('data')))
    seances = response_data['data']
    hc.assert_that(seances, hc.has_length(1))
    hc.assert_that(seances, hc.has_items(seance_data if max(seance, another_seance) == seance else another_seance_data))

    response = await client.get(f'/movies?with_seances=1')
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_key(hc.equal_to('data')))
    movies = response_data['data']
    hc.assert_that(movies, hc.has_length(1))
    hc.assert_that(movies, hc.has_items(
        {"id": create_movie,
         "name": "Test Movie",
         "description": "Test description",
         "image_url": "http://example.com/test_image.jpeg",
         "comingSoon": True}
    ))


@pytest.mark.asyncio
async def test_seances_delete_negative(aiohttp_raw_server, aiohttp_client, create_mocked_app):
    app = create_mocked_app(lambda app: app.router.add_delete('/movies/{movie_id}/seances/{seance_id}',
                                                              movies_api.delete_movie_seance.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    response = await client.delete('/movies/1/seances/23232323')
    hc.assert_that(response.status, hc.equal_to(404))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({'errors': [
        {'title': 'Not found',
         'detail': 'seance_id 23232323 not found'}
    ]}))


@pytest.mark.asyncio
async def test_seances_get_by_movie_negative(aiohttp_raw_server, aiohttp_client, create_mocked_app):
    app = create_mocked_app(lambda app: app.router.add_get('/movies/{movie_id}/seances',
                                                           movies_api.get_movie_seances.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    response = await client.get('/movies/4535435576/seances')
    hc.assert_that(response.status, hc.equal_to(404))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({'errors': [
        {'title': 'Not found',
         'detail': 'movie_id 4535435576 not found'}
    ]}))

import hamcrest as hc
import pytest
from src.api import movies as movies_api


@pytest.mark.asyncio
async def test_get_movies(create_movie, create_another_movie, aiohttp_raw_server, aiohttp_client, create_mocked_app,
                          event_loop) -> None:
    app = create_mocked_app(lambda app: app.router.add_get('/movies',
                                                           movies_api.get_movies.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    response = await client.get('/movies')
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    if len(response_data['data']) == 1:
        import time
        time.sleep(2)
        response = await client.get('/movies')
        hc.assert_that(response.status, hc.equal_to(200))
        response_data = await response.json()
    hc.assert_that(response_data, hc.has_key(hc.equal_to('data')))
    movies = response_data['data']
    hc.assert_that(movies, hc.has_length(2))
    hc.assert_that(movies, hc.has_items(
        {"id": create_movie,
         "name": "Test Movie",
         "description": "Test description",
         "image_url": "http://example.com/test_image.jpeg",
         "comingSoon": False},
        {"id": create_another_movie,
         "name": "Test Movie",
         "description": "Test description",
         "image_url": "http://example.com/test_image.jpeg",
         "comingSoon": False}
    ))

    response = await client.get(f'/movies?max_results=1')
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_key(hc.equal_to('data')))
    movies = response_data['data']
    hc.assert_that(movies, hc.has_length(1))
    hc.assert_that(movies, hc.has_items(
        {"id": max(create_movie, create_another_movie),
         "name": "Test Movie",
         "description": "Test description",
         "image_url": "http://example.com/test_image.jpeg",
         "comingSoon": False}
    ))


@pytest.mark.asyncio
async def test_movies_delete_negative(aiohttp_raw_server, aiohttp_client, create_mocked_app, event_loop):
    app = create_mocked_app(lambda app: app.router.add_delete('/movies/{movie_id}',
                                                              movies_api.delete_movie.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    response = await client.delete('/movies/12321321')
    hc.assert_that(response.status, hc.equal_to(404))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({'errors': [
        {'title': 'Not found',
         'detail': 'movie_id 12321321 not found'}
    ]}))

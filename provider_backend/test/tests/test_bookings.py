import hamcrest as hc
import pytest
from src.api import movies as movies_api
from src.api import bookings as bookings_api


async def get_bookings(create_movie, create_seance, create_seats, create_booking, is_short_url,
                       aiohttp_raw_server, aiohttp_client, create_mocked_app):
    app = create_mocked_app(lambda app: app.router.add_get('/movies/{movie_id}/seances',
                                                           movies_api.get_movie_seances.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    seance_datetime = "2020-01-18T00:00:00.000Z"
    seance = await create_seance(create_movie, seance_datetime)
    await create_booking('test_email@slurm.io', [create_seats[0]], seance, is_short_url)
    response = await client.get(f'/movies/{create_movie}/seances')
    hc.assert_that(response.status, hc.equal_to(200))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_key(hc.equal_to('data')))
    seances = response_data['data']
    hc.assert_that(seances, hc.has_length(1))
    seats = [{'id': create_seats[0], 'vacant': False},
             {'id': create_seats[1], 'vacant': True}]
    seance_data = {"id": seance,
                   "price": 250,
                   "datetime": seance_datetime,
                   "seats": seats}
    hc.assert_that(seances, hc.has_items(seance_data))


@pytest.mark.asyncio
async def test_get_bookings_directly(create_movie, create_seance, create_seats, create_booking,
                                     aiohttp_raw_server, aiohttp_client, create_mocked_app):
    await get_bookings(create_movie, create_seance, create_seats, create_booking, True,
                       aiohttp_raw_server, aiohttp_client, create_mocked_app)


@pytest.mark.asyncio
async def test_get_bookings_through_movies(create_movie, create_seance, create_seats, create_booking,
                                           aiohttp_raw_server, aiohttp_client, create_mocked_app):
    await get_bookings(create_movie, create_seance, create_seats, create_booking, False,
                       aiohttp_raw_server, aiohttp_client, create_mocked_app)


@pytest.mark.asyncio
async def test_make_booking_empty_negative(create_movie, create_seance, aiohttp_raw_server, aiohttp_client, create_mocked_app):
    app = create_mocked_app(lambda app: app.router.add_post('/bookings',
                                                            bookings_api.create_booking_directly.__wrapped__.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    seance = await create_seance(create_movie, "2020-01-18T00:00:00.000Z")
    response = await client.post('/bookings', json={"email": 'test_email@slurm.io',
                                                    "seatsIds": [],
                                                    "seance_id": seance})
    hc.assert_that(response.status, hc.equal_to(400))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({'errors': [
        {'title': 'seatsIds must be an non-empty array'}
    ]}))


@pytest.mark.asyncio
async def test_make_booking_no_exist_seat_negative(create_movie, create_seance, aiohttp_raw_server, aiohttp_client, create_mocked_app):
    seance = await create_seance(create_movie, "2020-01-18T00:00:00.000Z")
    app = create_mocked_app(lambda app: app.router.add_post('/bookings', bookings_api.create_booking_directly.__wrapped__.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    response = await client.post(f'/bookings', json={"email": 'test_email@slurm.io',
                                                     "seatsIds": [1, 2],
                                                     "seance_id": seance})
    hc.assert_that(response.status, hc.equal_to(404))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({'errors': [
        {'title': 'Not found',
         'detail': 'seats 1, 2 not found'}
    ]}))


@pytest.mark.asyncio
async def test_make_booking_no_exist_seance_negative(aiohttp_raw_server, aiohttp_client, create_mocked_app, create_seats):
    app = create_mocked_app(lambda app: app.router.add_post('/bookings',
                                                            bookings_api.create_booking_directly.__wrapped__.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    response = await client.post(f'/bookings', json={"email": 'test_email@slurm.io',
                                                     "seatsIds": [create_seats[0]],
                                                     "seance_id": 123123})
    hc.assert_that(response.status, hc.equal_to(404))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({'errors': [
        {'title': 'Not found',
         'detail': 'seance_id 123123 not found'}
    ]}))


@pytest.mark.asyncio
async def test_make_booking_already_taken_negative(create_movie, create_seance, create_seats, create_booking,
                                                   aiohttp_raw_server, aiohttp_client, create_mocked_app):
    app = create_mocked_app(lambda app: app.router.add_post('/bookings',
                                                            bookings_api.create_booking_directly.__wrapped__.__wrapped__.__wrapped__))
    client = await aiohttp_client(app)
    seance_datetime = "2020-01-18T00:00:00.000Z"
    seance = await create_seance(create_movie, seance_datetime)
    await create_booking('test_email@slurm.io', [create_seats[0]], seance)
    response = await client.post('/bookings', json={"email": 'test_email@slurm.io',
                                                    "seatsIds": [create_seats[0]],
                                                    "seance_id": seance})
    hc.assert_that(response.status, hc.equal_to(409))
    response_data = await response.json()
    hc.assert_that(response_data, hc.has_entries({'errors': [
        {'title': 'Seat already taken',
         'detail': f'Taken seats: {create_seats[0]}'}
    ]}))

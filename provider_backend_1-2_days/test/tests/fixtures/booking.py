import hamcrest as hc
import psycopg2
import pytest
import src.api
from src.api import movies as movies_bookings_api
from src.api import bookings as bookings_api


@pytest.fixture(scope='function')
async def create_booking(request: pytest.fixture, create_seats, create_mocked_app, aiohttp_client, monkeypatch):

    async def impl(user_email: str, seats: list, seance_id: int, is_direct_request=False):

        if is_direct_request:
            app = create_mocked_app(lambda app: app.router.add_post('/bookings',
                                                                    bookings_api.create_booking_directly.__wrapped__.__wrapped__.__wrapped__))
        else:
            app = create_mocked_app(lambda app: app.router.add_post('/movies/{movie_id}/seances/{seance_id}/bookings',
                                                                    movies_bookings_api.create_booking_through_movies.__wrapped__.__wrapped__.__wrapped__))
        client = await aiohttp_client(app)

        payload = {"email": user_email,
                   "seatsIds": seats}
        url = f'/movies/1/seances/{seance_id}/bookings'
        if is_direct_request:
            payload["seance_id"] = seance_id
            url = '/bookings'
        response = await client.post(url, json=payload)
        hc.assert_that(response.status, hc.equal_to(200))
        response_data = await response.json()
        hc.assert_that(response_data, hc.has_key(hc.equal_to("data")))
        bookings = response_data['data']
        hc.assert_that(bookings, hc.has_length(len(seats)))
        cnx = psycopg2.connect(pytest.postgresql_credentials)
        cursor = cnx.cursor()
        cursor.execute(R'''
            SELECT bookings.id 
            FROM bookings
            JOIN users ON users.id = bookings.user_id 
            WHERE users.email = %(email)s AND seance_id = %(seance_id)s 
        ''', {'email': user_email,
              'seance_id': seance_id})
        data = cursor.fetchall()
        hc.assert_that([tuple(bookings)], hc.equal_to(data))
        cnx.commit()
        cursor.close()
        cnx.close()
        request.addfinalizer(lambda: delete_booking(bookings))
        return bookings
    return impl


def delete_booking(bookings):
    cnx = psycopg2.connect(pytest.postgresql_credentials)
    cursor = cnx.cursor()
    for _ in range(2):
        cursor.execute(R'DELETE FROM bookings WHERE id IN (%s)', (bookings))
    cnx.commit()
    cursor.close()
    cnx.close()

import psycopg2
import pytest


@pytest.fixture(scope='function')
def create_seats(request):
    cnx = psycopg2.connect(pytest.postgresql_credentials)
    cursor = cnx.cursor()
    seats = []
    for _ in range(2):
        cursor.execute(R'INSERT INTO seats VALUES (DEFAULT) RETURNING id')
        seats.append(int((cursor.fetchone())[0]))
        cnx.commit()
    cursor.close()
    cnx.close()
    request.addfinalizer(remove_seats)
    return seats


def remove_seats():
    cnx = psycopg2.connect(pytest.postgresql_credentials)
    cursor = cnx.cursor()
    cursor.execute(R'DELETE FROM seats')
    cnx.commit()
    cursor.close()
    cnx.close()

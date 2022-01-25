import asyncio
import time
import aiopg
import psycopg2
import pytest


def pool_fin(pool, event_loop):
    async def afin(pool):
        pool.close()
        await pool.wait_closed()
    event_loop.run_until_complete(afin(pool))


@pytest.mark.asyncio
@pytest.fixture(scope='session')
async def primary_db_conn_pool(request: pytest.fixture, event_loop):

    while True:
        try:
            pool = await aiopg.create_pool(pytest.postgresql_credentials, maxsize=50)
            break
        except psycopg2.OperationalError:
            print("Can not connect to DB, wait for 5 seconds")
            time.sleep(5)
    print("Connection established")
    request.addfinalizer(lambda: pool_fin(pool, event_loop))
    return pool


secondary_db_conn_pool = primary_db_conn_pool


async def safe_query(cur, query) -> None:
    """
    Проверка существования индекса
    :param cur: объект курсора к БД
    :param query: запрос
    :return: None
    """
    try:
        await cur.execute(query)
    except (psycopg2.errors.DuplicateObject, psycopg2.errors.DuplicateTable):
        return
    except Exception as err:
        raise err


@pytest.mark.asyncio
@pytest.mark.first
@pytest.fixture(scope='session', autouse=True)
async def db_init(primary_db_conn_pool):
    async with primary_db_conn_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(R'''
                CREATE TABLE IF NOT EXISTS seats
                (
                    id BIGSERIAL,
                    CONSTRAINT seats_pk PRIMARY KEY (id)
                );
                
                CREATE TABLE IF NOT EXISTS cities
                (
                    id BIGSERIAL,
                    name VARCHAR(255),
                    CONSTRAINT cities_pk PRIMARY KEY (id)
                );
                
                CREATE TABLE IF NOT EXISTS users
                (
                    id BIGSERIAL,
                    email VARCHAR(255) NOT NULL,
                    CONSTRAINT users_pk PRIMARY KEY (id)
                );
                
                CREATE TABLE IF NOT EXISTS movies
                (
                    id BIGSERIAL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    image_url VARCHAR(255) NOT NULL,
                    CONSTRAINT movies_pk PRIMARY KEY (id)
                );
    
                CREATE TABLE IF NOT EXISTS seances
                (
                    id BIGSERIAL,
                    movie_id BIGINT NOT NULL,
                    price DECIMAL NOT NULL,
                    seance_datetime TIMESTAMP NOT NULL,
                    CONSTRAINT seances_pk PRIMARY KEY (id)
                );
                
            ''')

            await cursor.execute(R'''
                CREATE TABLE IF NOT EXISTS bookings
                (
                    id BIGSERIAL,
                    seance_id BIGINT NOT NULL,
                    seat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    CONSTRAINT bookings_pk PRIMARY KEY (id)
                );
            ''')
            await safe_query(cursor, R'''
                ALTER TABLE bookings
                    ADD CONSTRAINT bookings_seances_seance_id_fk
                        FOREIGN KEY (seance_id) REFERENCES seances (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE;
                ''')

            await safe_query(cursor, '''
                ALTER TABLE bookings
                    ADD CONSTRAINT bookings_seats_seat_id_fk
                        FOREIGN KEY (seat_id) REFERENCES seats (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE;
               ''')

            await safe_query(cursor, R'''
                ALTER TABLE bookings
                    ADD CONSTRAINT bookings_users_user_id_fk
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE;
                ''')

            await safe_query(cursor, R'''
                CREATE UNIQUE INDEX bookings_seance_id_seat_id_uindex
                    ON bookings (seance_id, seat_id);
                ''')
            tables = 0
            while tables != 6:
                await cursor.execute("SELECT count(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'public'")
                tables = int((await cursor.fetchone())[0])
                await asyncio.sleep(1)

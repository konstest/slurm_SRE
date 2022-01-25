""" Movies API """
from datetime import datetime
from aiojobs.aiohttp import atomic
from aiohttp import web
import aiopg
import psycopg2.extras
from pymysql.err import IntegrityError
from src.api import get_auth_header, track_to_prometheus
from src.api.bookings import create_booking
from src.misc import add_optionally_slashed_route, validatable


class Movies(web.Application):
    """
    API взаимодействия с сущностью "Фильмы"
    """

    def __init__(self):
        super().__init__()
        self['default_headers'] = {'charset': 'utf-8'}
        self.add_routes(
            [*add_optionally_slashed_route(web.post, '', create_movie),
             *add_optionally_slashed_route(web.delete, '/{movie_id}', delete_movie),
             *add_optionally_slashed_route(web.get, '', get_movies),
             *add_optionally_slashed_route(web.post, '/{movie_id}/seances', create_movie_seance),
             *add_optionally_slashed_route(web.delete, '/{movie_id}/seances/{seance_id}', delete_movie_seance),
             *add_optionally_slashed_route(web.get, '/{movie_id}/seances', get_movie_seances),
             *add_optionally_slashed_route(web.post, '/{movie_id}/seances/{seance_id}/bookings',
                                           create_booking_through_movies),
             ])

    def post_init(self, parent) -> None:
        """
        Инициализация асинхронно создаваемых объектов
        :param parent: родительское приложение aiohttp
        :return: None
        """
        self['client_session'] = parent['client_session']
        self['primary_db_conn_pool'] = parent['primary_db_conn_pool']
        self['secondary_db_conn_pool'] = parent['secondary_db_conn_pool']
        self['schemas'] = parent['schemas']
        self['success_bookings_total'] = parent['success_bookings_total']
        self['request_duration_seconds'] = parent['request_duration_seconds']
        self['requests_total'] = parent['requests_total']
        self['request_middle_duration_seconds'] = parent['request_middle_duration_seconds']
        self['requests_middle_total'] = parent['requests_middle_total']
        self['logger'] = parent['logger']


@atomic
@track_to_prometheus
@validatable()
async def create_movie(request: web.Request):
    """
    Создание записи с фильмом
    :param request: объект с параметрами входящего запроса
    :return:
    """
    payload = await request.json()
    additional_headers = await get_auth_header(request)
    async with request.app['primary_db_conn_pool'].acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(R'''
                    INSERT INTO movies (name, description, image_url)
                    VALUES (%(name)s, %(description)s, %(image_url)s)
                    RETURNING id
                    ''', payload)
            last_id = int((await cursor.fetchone())[0])
            request.app["logger"].debug(f"Movie {last_id} created")
            return web.json_response({
                    'data': {
                        'id': last_id,
                        'type': 'movies',
                        'attributes': {
                            **payload
                        }
                    }
                }, headers={**request.app['default_headers'], **additional_headers})


@atomic
@track_to_prometheus
async def delete_movie(request: web.Request):
    """
    Удаление записи с фильмом
    :param request: объект с параметрами входящего запроса
    :return:
    """
    additional_headers = await get_auth_header(request)
    movie_id = request.match_info['movie_id']
    async with request.app['primary_db_conn_pool'].acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute('DELETE FROM movies WHERE id = %s', (movie_id, ))
            if not cursor.rowcount:
                return web.json_response(
                    {'errors': [{'title': 'Not found', 'detail': f'movie_id {movie_id} not found'}]},
                    status=404)
        return web.json_response({
                'data': {
                    'id': movie_id,
                    'type': 'movies'
                }
            }, headers={**request.app['default_headers'], **additional_headers})


@atomic
@track_to_prometheus
async def get_movies(request: web.Request):
    """
    Получение записей с фильмом
    :param request: объект с параметрами входящего запроса
    :return:
    """
    additional_headers = await get_auth_header(request)
    limit = int(request.query.get('max_results', '50'))
    is_with_seances = request.query.get('with_seances', False)
    async with request.app['secondary_db_conn_pool'].acquire() as connection:
        async with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            await cursor.execute(fR'''
                                SELECT m.*, COALESCE(max((seance_datetime >= current_date)::int), 0) as comingSoon
                                FROM movies m
                                LEFT JOIN seances s ON m.id = s.movie_id
                                GROUP BY m.id
                                {'HAVING COALESCE(max((seance_datetime >= current_date)::int), 0) = 1' if is_with_seances else ''}
                                ORDER BY m.id DESC
                                LIMIT %s''', (limit, ))
            result = await cursor.fetchall()
        for movie in result:
            movie['comingSoon'] = bool(movie['comingsoon'])
            del movie['comingsoon']
        return web.json_response({
                'data': result
            }, headers={**request.app['default_headers'], **additional_headers})


@atomic
@track_to_prometheus
@validatable(['movie_id'])
async def create_movie_seance(request: web.Request):
    """
    Создание сеанса на фильм
    :param request: объект с параметрами входящего запроса
    :return:
    """
    payload = await request.json()
    additional_headers = await get_auth_header(request)
    payload['seance_datetime'] = datetime.strptime(payload['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
    payload['movie_id'] = request.match_info['movie_id']
    async with request.app['primary_db_conn_pool'].acquire() as connection:
        async with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            try:
                await cursor.execute(R'''
                        INSERT INTO seances (movie_id, price, seance_datetime)
                        VALUES (%(movie_id)s, %(price)s, %(seance_datetime)s)
                        RETURNING id
                    ''', payload)
            except IntegrityError as err:
                if err.args[0] == 1452:
                    return web.json_response(
                        {'errors': [{'title': 'Not found',
                                     'detail': f'movie_id {payload["movie_id"]} not found'}]},
                        status=404)
                return web.json_response({'errors': [{'title': err.args[1]}]}, status=400)
            del payload['seance_datetime']
            seance_id = (await cursor.fetchone())["id"]
            await cursor.execute('SELECT id, TRUE as vacant FROM seats')
            seats = await cursor.fetchall()
        for seat in seats:
            seat['vacant'] = bool(seat['vacant'])
        return web.json_response({
            'data': {
                'id': seance_id,
                'type': 'seances',
                'attributes': {
                    **payload
                },
                'seats': seats
            }
        }, headers={**request.app['default_headers'], **additional_headers})


@atomic
@track_to_prometheus
async def delete_movie_seance(request: web.Request):
    """
    Удаление сеанса на фильм
    :param request: объект с параметрами входящего запроса
    :return:
    """
    additional_headers = await get_auth_header(request)
    seance_id = request.match_info['seance_id']
    async with request.app['primary_db_conn_pool'].acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute('DELETE FROM seances WHERE id = %s', (seance_id, ))
            if not cursor.rowcount:
                return web.json_response(
                    {'errors': [{'title': 'Not found', 'detail': f'seance_id {seance_id} not found'}]},
                    status=404)
        return web.json_response({
                'data': {
                    'id': seance_id,
                    'type': 'seances'
                }
            }, headers={**request.app['default_headers'], **additional_headers})


@atomic
@track_to_prometheus
async def get_movie_seances(request: web.Request):
    """
    Получение сеансов
    :param request: объект с параметрами входящего запроса
    :return:
    """
    additional_headers = await get_auth_header(request)
    movie_id = request.match_info['movie_id']
    limit = int(request.query.get('max_results', 50))
    async with request.app['secondary_db_conn_pool'].acquire() as connection:
        async with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            await cursor.execute('SELECT count(*) as count FROM movies WHERE id = %s', (movie_id, ))
            is_film_exist_record = await cursor.fetchone()
            is_film_exist = is_film_exist_record['count'] > 0
            request.app['logger'].info(f"Movie with ID {movie_id} {'exists' if is_film_exist else 'NOT exist'}")

            if not is_film_exist:
                return web.json_response(
                    {'errors': [{'title': 'Not found', 'detail': f'movie_id {movie_id} not found'}]},
                    status=404)

            await cursor.execute(R'''
                    SELECT *
                    FROM seances
                    WHERE movie_id = %s
                    ORDER BY id DESC
                    LIMIT %s
            ''', (movie_id, limit))
            rows = await cursor.fetchall()
            if not rows:
                return web.json_response({
                    'data': []
                }, headers={**request.app['default_headers'], **additional_headers})
            data = []
            for seance in rows:
                seance['price'] = int(seance['price'])
                seance['datetime'] = (seance['seance_datetime']
                                      .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')
                del seance['seance_datetime']
                del seance['movie_id']
                await cursor.execute(R'''
                    SELECT seats.*,
                           not exists(SELECT 1
                                  FROM bookings b
                                  WHERE seats.id = b.seat_id AND b.seance_id = %s) as vacant
                    FROM seats;
                ''', (seance['id'], ))
                seats = await cursor.fetchall()
                for seat in seats:
                    seat['vacant'] = bool(seat['vacant'])
                data.append({**seance, 'seats': seats})
        return web.json_response({
                'data': data
            }, headers={**request.app['default_headers'], **additional_headers})


@atomic
@track_to_prometheus
@validatable(['seance_id'])
async def create_booking_through_movies(request):
    """
    Создание бронирования через movies api (/movies/N/seances/M/bookings)
    :param request: объект входящего запроса aiohttp
    :return: http response
    """
    return await create_booking(request, {'seance_id': request.match_info['seance_id']})

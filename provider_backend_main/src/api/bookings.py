""" Bookings API """
from os import getenv
import re

import psycopg2.extras
from aiojobs.aiohttp import atomic
from aiohttp import web
from src.api import get_auth_header, track_to_prometheus
from src.misc import add_optionally_slashed_route, validatable


class Bookings(web.Application):
    """
    API взаимодействия с сущностью "Бронирование"
    """
    seat_err_re = re.compile(R"^DETAIL:\s+Key \(seance_id, seat_id\)=\(\d+, (\d+)\) already exists.*", re.MULTILINE)

    def __init__(self):
        super().__init__()
        self['default_headers'] = {'charset': 'utf-8'}
        self.add_routes([*add_optionally_slashed_route(web.post, '', create_booking_directly)])

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
        self['request_duration_seconds'] = parent['request_duration_seconds']
        self['requests_total'] = parent['requests_total']
        self['success_bookings_total'] = parent['success_bookings_total']


@atomic
@track_to_prometheus
@validatable()
async def create_booking_directly(request):
    """
    Создание бронирования напрямоую (/bookings)
    :param request: объект входящего запроса aiohttp
    :return: http response
    """
    return await create_booking(request)


async def create_booking(request, additional_payload: dict = None):
    """
    Создание записи с сеансом
    :param request: объект входящего запроса aiohttp
    :param additional_payload: дополнительный payload из параметров запроса
    :return: http response
    """
    additional_headers = await get_auth_header(request)
    app = request.app
    payload = await request.json() \
        if additional_payload is None \
        else {**additional_payload, **await request.json()}
    seats = payload.get('seatsIds')
    if not seats:
        return web.json_response({'errors': [{'title': "seatsIds must be an non-empty array"}]},
                                 status=400)

    async with app['primary_db_conn_pool'].acquire() as connection:
        async with app['secondary_db_conn_pool'].acquire() as secondary_connection:
            async with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                async with secondary_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as secondary_cursor:
                    await secondary_cursor.execute(R'''
                        SELECT id FROM users WHERE email = %(email)s
                        ''', payload)
                    user = await secondary_cursor.fetchone()
                    if user is None:
                        await cursor.execute(R'''
                        INSERT INTO users (email) VALUES (%(email)s) RETURNING id
                        ''', payload)
                        user_id = (await cursor.fetchone())['id']
                    else:
                        user_id = user['id']
                    seance_id = payload['seance_id']
                    bookings_id = []
                    is_seat_exists_query = ''
                    for seat in seats:
                        is_seat_exists_query += f'{"UNION" if is_seat_exists_query else ""} SELECT {seat} as seat '
                    await secondary_cursor.execute(fR'''SELECT seat
                                                        FROM ({is_seat_exists_query}) as queried_seats
                                                        WHERE seat NOT IN (SELECT id FROM seats)''')
                    non_exist_seats = await secondary_cursor.fetchall()
                    if len(non_exist_seats) > 0:
                        return web.json_response(
                            {'errors': [{'title': 'Not found',
                                         'detail': f'seats {", ".join([str(entry["seat"]) for entry in non_exist_seats])} not found'}]},
                            status=404)
                    try:
                        for seat_id in seats:
                            trans = await cursor.begin()
                            await cursor.execute(R'''
                                INSERT INTO bookings (seance_id, seat_id, user_id) VALUES (%s, %s, %s) RETURNING id
                            ''', (seance_id, seat_id, user_id))
                            last_id = (await cursor.fetchone())["id"]
                            bookings_id.append(last_id)
                            await trans.commit()
                    except psycopg2.errors.ForeignKeyViolation:
                        await trans.rollback()
                        return web.json_response(
                            {'errors': [{'title': 'Not found',
                                         'detail': f'seance_id {seance_id} not found'}]},
                            status=404)
                    except psycopg2.errors.UniqueViolation as err:
                        taken_seat_id = re.search(Bookings.seat_err_re, err.args[0]).group(1)
                        return web.json_response({'errors': [
                            {'title': 'Seat already taken',
                             'detail': f'Taken seats: {taken_seat_id}'}]},
                            status=409)
                    except Exception as err:
                        return web.json_response({'errors': [{'title': err.args[1]}]}, status=400)

        ###

        return web.json_response({'data': bookings_id},
                                 headers={**app['default_headers'], **additional_headers})

""" App middlewares """
import asyncio
from asyncio import CancelledError, TimeoutError
from datetime import datetime
from functools import wraps
from os import getenv
from traceback import print_exc
from aiohttp import web, client_exceptions, ClientTimeout

STATUS_MESSAGES = {
    404: 'request path not found',
    500: 'internal server error',
    504: 'http gateway timeout',
}


class AuthProblemError(Exception):
    """
    Exception raised for errors in the auth service

    Attributes:
        code -- http code
        details -- explanation of the error
    """

    def __init__(self, code: int, details):
        self.code = code
        self.details = details
        super().__init__(self.details)


def track_to_prometheus(func):
    """
    Отправка метрик в Prometheus
    :return: объект ответа
    """
    @wraps(func)
    async def wrapped(request):
        start = datetime.now()
        response = None
        app = request.app
        try:
            response = await func(request)
            if "seances" in request.url.path or "movies" in request.url.path or "bookings" in request.url.path:
                track_request_in_eventlog()
        except Exception as exc:
            response = error_handler(app, exc)
        finally:
            end = datetime.now() - start
            city = getenv('PROVIDER_CITY', 'unknown')
            prometheus_labels = {'app': 'provider_backend', 'city': city}
            app['request_duration_seconds'].observe(prometheus_labels, end.total_seconds())
            app['requests_total'].inc({**prometheus_labels, 'code': response.status})
            return response
    return wrapped


def error_handler(app, exception):
    """
    Обработка ответов на запросы, завершившихся ошибками
    :param app: объект приложения aiohttp
    :param exception: полученная ошибка
    :return: объект ответа
    """
    if isinstance(exception, web.HTTPException):
        status = exception.status
        if status >= 500:
            app['logger'].error('Failure during HTTP request', exc_info=True)
        return web.json_response({'errors': [{'app': 'provider_backend', 'title': STATUS_MESSAGES.get(status, exception.reason)}]},
                                 status=status)
    elif isinstance(exception, client_exceptions.ClientConnectionError):
        app['logger'].error('Failed to connect', exc_info=True)
        return web.json_response({'errors': [{'app': 'provider_backend', 'title': 'Failed to connect'}]},
                                 status=503)
    elif isinstance(exception, CancelledError) or isinstance(exception, TimeoutError):
        app['logger'].error('Request timeout exceeded', exc_info=True)
        return web.json_response({'errors': [{'app': 'provider_backend', 'title': STATUS_MESSAGES.get(503, "Service Unavailable")}]},
                                 status=200)
    elif isinstance(exception, AuthProblemError):
        app['logger'].error('Auth error', exc_info=True)
        return web.json_response({'errors': [{'title': f"Auth service", 'detail': exception.details}]}, status=exception.code)
    else:
        app['logger'].error('Something went wrong', exc_info=True)
        return web.json_response({'errors': [{'app': 'provider_backend', 'title': str(exception)}]}, status=504)


async def get_auth_header(request: web.Request):
    """
    Авторизация в сервисе авторизации :)
    :param request: объект входящего запроса
    :return: ответ на входящий запрос или ответ с ошибкой
    """
    status = 0
    auth_response = None
    reason = ""
    app = request.app

    tm = float(getenv('AUTH_SERVICE_TIMEOUT', '0'))
    timeout = tm if tm > 0 else 60

    auth_response = await request.app['client_session'] \
                                 .get(getenv('AUTH_SERVICE_URL'),
                                      headers={getenv('PROVIDER_SOURCE_HEADER'): getenv('PROVIDER_SOURCE_TOKEN'), 'Connection': 'close'},
                                      timeout=ClientTimeout(total=timeout))

    status = auth_response.status
    if 200 <= status < 300:
        return {'X-Auth-Operation-Id': auth_response.headers.getone('x-auth-operation-id')}

    if auth_response is not None:
        reason = (await auth_response.json()) if status == 401 else (await auth_response.text())

    raise AuthProblemError(status, reason)

""" Helper-functions """
from datetime import datetime
from functools import wraps
from aiohttp import web
from jsonschema import validate, FormatChecker, ValidationError


def check_datetime(item):
    """
    Проверка формата 2020-01-18T00:00:00.000Z
    :param item: проверяемая строка
    :return: флаг соответствия
    """
    try:
        datetime.strptime(item, '%Y-%m-%dT%H:%M:%S.%fZ')
        return True
    except ValueError:
        return False


CHECKER = FormatChecker()
CHECKER.checks("datetimez")(check_datetime)


def validatable(path_params: list = None):
    """
    Фабрика декторатора validatable
    :param path_params: список валидируемых path params
    :return: декторатор validatable
    """
    def decorator(func):
        @wraps(func)
        async def wrapped(request):
            validatable_struct = await request.json()
            if path_params:
                for path_param in path_params:
                    validatable_struct[path_param] = request.match_info[path_param]
            try:
                validate(instance=validatable_struct,
                         schema=request.app['schemas'][func.__name__],
                         format_checker=CHECKER)
            except ValidationError as err:
                status = 422
                if err.validator == 'required':
                    status = 400
                return web.json_response({'errors': [{'title': "Validation failed",
                                                      'detail': err.message}]}, status=status)
            return await func(request)
        return wrapped
    return decorator


def add_optionally_slashed_route(method, path: str, handler):
    """
    Добавление эндпоинта с опциональным слешем в конце
    :param method: HTTP метод
    :param path: URI эндпоинта
    :param handler: ассоциированный с эндпоинтом хендлер
    """
    return [method(path, handler), method(path + '/', handler)]

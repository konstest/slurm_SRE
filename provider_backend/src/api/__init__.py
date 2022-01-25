""" Индексация API """
from src.api.middlewares import get_auth_header, error_handler, track_to_prometheus
from src.api.bookings import Bookings
from src.api.movies import Movies

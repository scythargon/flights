import functools
import json
from datetime import datetime


def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_list = [repr(arg) for arg in args]
        kwargs_list = [f"{key}={repr(value)}" for key, value in kwargs.items()]
        params = ", ".join(arg_list + kwargs_list)
        print(f"Calling {func.__name__}({params})")
        return func(*args, **kwargs)
    return wrapper


from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS = 6371.0  # Радиус Земли в километрах


def calculate_distance(lat1, lon1, lat2, lon2):
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = EARTH_RADIUS * c
    return distance


def get_city_name(iata):
    with open('lib/airports.json', 'r') as file:
        data = json.load(file)
        if iata in data:
            return data[iata]
        else:
            return None


def get_first_day_of_next_month():
    today = datetime.now()
    if today.month == 12:
        next_month = 1
        next_year = today.year + 1
    else:
        next_month = today.month + 1
        next_year = today.year

    first_day_of_next_month = datetime(next_year, next_month, 1)
    return first_day_of_next_month.strftime('%Y-%m-%d')

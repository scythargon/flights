import calendar
import functools
import json
import os
import sys
from datetime import datetime
from functools import wraps
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path


def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_list = [repr(arg) for arg in args]
        kwargs_list = [f"{key}={repr(value)}" for key, value in kwargs.items()]
        params = ", ".join(arg_list + kwargs_list)
        print(f"Calling {func.__name__}({params})")
        return func(*args, **kwargs)

    return wrapper


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
    with open('lib/data_files/airports.json', 'r') as file:
        data = json.load(file)
        if iata in data:
            return data[iata]
        else:
            return None


def get_first_day_of_next_month():
    today = datetime.now()
    if today.month == 12:
        next_month = 1
        year = today.year + 1
    else:
        next_month = today.month + 1
        year = today.year

    first_day_of_next_month = datetime(year, next_month, 1)
    return first_day_of_next_month.strftime('%Y-%m-%d')


def get_last_day_of_next_month():
    today = datetime.now()
    if today.month == 12:
        next_month = 1
        year = today.year + 1
    else:
        next_month = today.month + 1
        year = today.year

    days_range = calendar.monthrange(year, next_month)
    last_day_of_next_month = datetime(year, next_month, days_range[1])
    return last_day_of_next_month.strftime('%Y-%m-%d')


def check_flush_cache(cache_path):
    if '--flush-cache' in sys.argv and os.path.exists(cache_path):
        os.remove(cache_path)


def cache(cache_dir):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            os.makedirs(cache_dir, exist_ok=True)
            cache_filename = f"{args[0]}_{args[1]}.json"
            cache_path = os.path.join(cache_dir, cache_filename)
            check_flush_cache(cache_path)

            if os.path.exists(cache_path):
                with open(cache_path, "r") as f:
                    response = json.load(f)
            else:
                response = func(*args, **kwargs)
                with open(cache_path, "w") as f:
                    json.dump(response, f)
            return response

        return wrapper

    return decorator


def repair_format(resp):
    """
    Since Aviasales changes the response format sometimes - this function is in charge of fixing it.
    """
    directions = resp['data']['best_directions_v1']['directions']
    data_for_frontend = []
    with open(Path(__file__).parent / 'data_files/airport_coordinates.json', 'r') as f:
        airports = json.load(f)

    for country_data in directions:
        for city_data in country_data['cities']:
            city_iata = city_data['city_iata']
            min_price = city_data['min_price']['value']
            lat = airports.get(city_iata, [None, None])[0]
            lng = airports.get(city_iata, [None, None])[1]
            if lat is None or lng is None:
                print(f"Missing coordinates for {city_iata}")
                continue
            data_for_frontend.append({
                    'iata': city_iata,
                    'min_price': min_price,
                    'lat': lat,
                    'lng': lng
                })
    return data_for_frontend


HEADERS = {
    'authority': 'ariadne.aviasales.ru',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8,de;q=0.7,nl;q=0.6',
    'content-type': 'application/json',
    'origin': 'https://www.aviasales.ru',
    'referer': 'https://www.aviasales.ru/',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'x-auid': 'rBMuQmQIcsakAAAeBcbWAg==',
    'x-user-platform': 'web',
}

import logging

import requests

from .utils import calculate_distance, get_city_name, get_first_day_of_next_month

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

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

QUERY = '''
query GetDirectFlightSchedule($originIata: String!, $destinationIata: String!, $currency: String!, $market: String!, $brand: Brand!) {
    there: direct_flights_v1(
        brand: $brand,
        input: {
            origin_iata: $originIata,
            destination_iata: $destinationIata,
            market: $market,
            currency: $currency,
        })
    {
        schedule {
            flights {
                origin_airport_iata
                destination_airport_iata
                departure_time
                airline
            }
            depart_date
        }
    }

    back: direct_flights_v1(
        brand: $brand,
        input: {
            origin_iata: $destinationIata,
            destination_iata: $originIata,
            market: $market,
            currency: $currency,
        })
    {
        schedule {
            flights {
                origin_airport_iata
                destination_airport_iata
                departure_time
                airline
            }
            depart_date
        }
    }
}
'''

from functools import lru_cache
import json
import os
from functools import wraps


def cache(cache_dir):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            os.makedirs(cache_dir, exist_ok=True)
            cache_filename = f"{args[0]}_{args[1]}.json"
            cache_path = os.path.join(cache_dir, cache_filename)
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


@lru_cache(maxsize=None)
@cache(cache_dir="./cache")
def direct_flights_request(origin, destination):
    variables = {
        "originIata": origin,
        "destinationIata": destination,
        "currency": "rub",
        "market": "ru",
        "brand": "AS"
    }
    data = {
        "query": QUERY,
        "variables": variables,
        "operation_name": "direct_flight_schedule"
    }
    print(f"looking for tickets from {origin} to {destination}", end=': ', flush=True)
    response = requests.post('https://ariadne.aviasales.ru/api/gql', headers=HEADERS, json=data)
    if response.status_code != 200:
        return None
    resp = response.json()['data']
    if resp:
        print('found')
    else:
        print('not found')
    return resp


from termcolor import colored
from search2 import get_map_data

date = get_first_day_of_next_month()

def print_route_prices(route, max_price=None):
    total_price = 0
    if max_price is not None:
        for i in range(len(route) - 1):
            origin, destination = route[i], route[i + 1]
            response = get_map_data(origin, date)
            prices = response['data']['map_v2']['prices']
            for price_data in prices:
                if price_data['destination_city']['iata'] == destination:
                    price = price_data['price']['value']
                    total_price += price
        if total_price > max_price:
            return

    print(colored("Маршрут найден:", "green", attrs=["bold"]), " -> ".join(route))
    for i in range(len(route) - 1):
        origin, destination = route[i], route[i + 1]
        response = get_map_data(origin, date)
        prices = response['data']['map_v2']['prices']
        for price_data in prices:
            if price_data['destination_city']['iata'] == destination:
                price = price_data['price']['value']
                print(f"{origin} ({get_city_name(origin)}) -> {destination} ({get_city_name(destination)}): {price}")

    print("Total price:", total_price)


airports = {
    'DPS': (-8.7482, 115.1672),  # Bali
    'JKT': (-6.1306, 106.7669),  # Jakarta
    'BKK': (13.6811, 100.7475),  # Bangkok
    'HAN': (21.2212, 105.8072),  # Hanoi
    'KUL': (2.7433, 101.6984),   # Kuala Lumpur
    'SIN': (1.3614, 103.9902),   # Singapore
    'KMG': (24.9924, 102.7433),  # Kunming
    'TPE': (25.0778, 121.2336),  # Taipei
    'TAS': (41.2575, 69.2817),   # Tashkent
    'ALA': (43.3521, 77.0405),   # Almaty
    'OVB': (55.0094, 82.6675),  # Novosibirsk
    'TYO': (35.6762, 139.6503),  # Tokyo
    'SEL': (37.4602, 126.4407),  # Seoul
    'NQZ': (51.1703, 71.4493),  # Nur-Sultan (Astana)
}

try:
    with open('airport_coordinates.json', 'r') as f:
        airports = json.load(f)
except FileNotFoundError:
   pass

month = get_first_day_of_next_month()


def find_route(origin, destination, route=None, first_airport=None, last_airport=None):
    if route is None:
        route = []
    route.append(origin)
    if len(route) == 4:
        return
    prefix = ' ' * (len(route) - 1)
    if origin == destination:
        print_route_prices(route, 70000)
        return

    if first_airport is None:
        first_airport = origin
    if last_airport is None:
        last_airport = destination

    map_data = get_map_data(origin, month)  # Получаем данные о прямых перелетах из текущего аэропорта
    prices = map_data['data']['map_v2']['prices']
    lat1, lon1 = airports[origin]

    if route == ['DPS', 'JKT', 'TAS', 'OVB']:
        print(route)

    for price_info in prices:
        next_airport = price_info['destination_city']['iata']
        if next_airport not in route:
            lat2, lon2 = price_info['destination_city']['coordinates']['lat'], price_info['destination_city']['coordinates']['lon']
            # if lat2 > lat1 and lat2 > airports[first_airport][0] and lat2 <= airports[last_airport][0]:
            distance_current = calculate_distance(lat1, lon1, airports[last_airport][0], airports[last_airport][1])
            distance_next = calculate_distance(lat2, lon2, airports[last_airport][0], airports[last_airport][1])
            if distance_next <= distance_current:
                aiport_city = get_city_name(next_airport)
                current_city = get_city_name(origin)
                # print(f'from {current_city  } checking', aiport_city, int(distance_next), int(distance_current))
                airports[next_airport] = (lat2, lon2)  # Добавляем координаты нового аэропорта в словарь airports
                found = True
                find_route(next_airport, destination, route.copy(), origin, destination)

    route.pop()




find_route('OVB', 'AER')

with open('airport_coordinates.json', 'w') as f:
    json.dump(airports, f)

# print(direct_flights_request('TAS', 'OVB'))
import json
import logging

from termcolor import colored

from .find_all_destinations import get_map_data
from .utils import calculate_distance, get_city_name, get_first_day_of_next_month, get_last_day_of_next_month

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)


def print_route_prices(route, max_price=None):
    total_price = 0
    if max_price is not None:
        for i in range(len(route) - 1):
            origin, destination = route[i], route[i + 1]
            prices = get_map_data(origin, get_first_day_of_next_month(), get_last_day_of_next_month())
            for price_data in prices:
                if price_data['iata'] == destination:
                    price = price_data['min_price']
                    total_price += price
        if total_price > max_price:
            return

    print(colored("Маршрут найден:", "green", attrs=["bold"]), " -> ".join(route))
    for i in range(len(route) - 1):
        origin, destination = route[i], route[i + 1]
        prices = get_map_data(origin, get_first_day_of_next_month(), get_last_day_of_next_month())
        for price_data in prices:
            if price_data['iata'] == destination:
                price = price_data['min_price']
                print(f"{origin} ({get_city_name(origin)}) -> {destination} ({get_city_name(destination)}): {price}")

    print("Total price:", total_price)


airports = {
    'DPS': (-8.7482, 115.1672),  # Bali
    'JKT': (-6.1306, 106.7669),  # Jakarta
    'BKK': (13.6811, 100.7475),  # Bangkok
    'HAN': (21.2212, 105.8072),  # Hanoi
    'KUL': (2.7433, 101.6984),  # Kuala Lumpur
    'SIN': (1.3614, 103.9902),  # Singapore
    'KMG': (24.9924, 102.7433),  # Kunming
    'TPE': (25.0778, 121.2336),  # Taipei
    'TAS': (41.2575, 69.2817),  # Tashkent
    'ALA': (43.3521, 77.0405),  # Almaty
    'OVB': (55.0094, 82.6675),  # Novosibirsk
    'TYO': (35.6762, 139.6503),  # Tokyo
    'SEL': (37.4602, 126.4407),  # Seoul
    'NQZ': (51.1703, 71.4493),  # Nur-Sultan (Astana)
}

try:
    # File with the airport coordinates previously parsed from Aviasales.
    # Now they don't include it in the response anymore.
    with open('lib/data_files/airport_coordinates.json', 'r') as f:
        airports = json.load(f)
except FileNotFoundError:
    pass


def find_route(origin, destination, route=None, final_destination=None,
               max_price=70 * 1000, max_flights=4):
    """
    Recursively find the best route from the origin to the destination.

    Currently, this file can only be run from CLI - it's not a part of the web app.
    It can be run like this from the project root:

    python scripts/find_best_route.py DPS OVB [--max-price=70000] [--max-flights=2]
    """
    if route is None:
        route = []
    route.append(origin) # add the current or the very first airport to the route

    # Stop if the route is too long. Number of flights = Number of airports minus 2.
    if len(route) == max_flights + 2:
        return

    if origin == destination: # found the route!
        print_route_prices(route, max_price)
        return

    if final_destination is None:
        final_destination = destination

    prices = get_map_data(origin, get_first_day_of_next_month(), get_last_day_of_next_month())
    lat1, lon1 = airports[origin]

    for price_info in prices:
        next_airport = price_info['iata']
        if next_airport not in route:
            lat2, lon2 = price_info['lat'], price_info['lng']
            # if lat2 > lat1 and lat2 > airports[first_airport][0] and lat2 <= airports[last_airport][0]:
            distance_current = calculate_distance(lat1, lon1, airports[final_destination][0], airports[final_destination][1])
            distance_next = calculate_distance(lat2, lon2, airports[final_destination][0], airports[final_destination][1])
            if distance_next <= distance_current:
                found = True
                find_route(next_airport, destination, route.copy(), destination, max_price, max_flights)

    route.pop()

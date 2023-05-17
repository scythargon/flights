import requests

from utils import log_call, get_city_name

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

import json
import os
from functools import wraps
from functools import lru_cache


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
@cache(cache_dir=os.path.join(os.path.dirname(__file__), "map_cache"))
@log_call
def get_map_data(city, month):
    query = """
        query GetMapV2(
            $input: MapV2Input!
            $brand: Brand!
        ) {
            map_v2(
                input: $input
                brand: $brand
            ) {
                origin_city {
                    iata
                }
                prices {
                    price {
                        value
                    }
                    destination_city {
                        iata
                        country {
                            iata
                        }
                        coordinates {
                            lat
                            lon
                        }
                    }
                    travel_restrictions {
                        city_travel_restrictions {
                            open
                        }
                        country_travel_restrictions {
                            open
                        }
                    }
                }
            }
        }
    """
    url = "https://ariadne.aviasales.ru/api/gql"

    data = {
        "query": query,
        "variables": {
            "brand": "AS",
            "language": "ru",
            "input": {
                "passport_country_iata": "RU",
                "currency": "rub",
                "origin_iata": city,
                "origin_type": "CITY",
                "trip_class": "Y",
                "market": "ru",
                "dates": {
                    "depart_months": [month]
                },
                "one_way": True,
                "filters": {
                    "direct": True
                }
            }
        },
        "operation_name": "map_v2"
    }

    aiport_city = get_city_name(city)
    print(aiport_city)
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

# print(get_map_data('OVB', '2023-05-01'))
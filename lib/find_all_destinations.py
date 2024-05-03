import os
from functools import lru_cache

import requests

from .utils import cache, repair_format, HEADERS, log_call


@lru_cache(maxsize=None)
@cache(cache_dir=os.path.join(os.path.dirname(__file__), "map_cache"))
@log_call
def get_map_data(city, start_date, end_date):
    resp = query_aviasales(city, start_date, end_date)
    return repair_format(resp)


def query_aviasales(city, start_date, end_date):
    """
    Without any caching decorators for testing.
    """
    query = """
      query BestDirectionsV1($input: BestDirectionsV1Input!, $brand: Brand!, $locales: [String!]) {
        best_directions_v1(input: $input, brand: $brand) {
          origin_city {
            iata
            translations(filters: {locales: $locales})
          }
          directions {
            country_iata
            min_price {
              value
              currency
            }
            cities {
              city_iata
              min_price {
                value
                currency
              }
            }
          }
          places {
            cities {
              city {
                iata
                translations(filters: {locales: $locales})
                coordinates {
                  lat
                  lon
                }
              }
            }
            countries {
              ...countriesFields
            }
          }
        }
      }
      
      fragment countriesFields on Country {
        iata
        translations(filters: {locales: $locales})
      }
    """
    url = "https://ariadne.aviasales.ru/api/gql"

    data = {
        "query": query,
        "variables": {
            "brand": "AS",
            "locales": [
                "en"
            ],
            "input": {
                "origin_iata": city,
                "origin_type": "CITY",
                "dates": {
                    "depart_date_from": start_date,
                    "depart_date_to": end_date
                },
                "one_way": True,
                "currency": "rub",
                "market": "ru",
                "passport_country": "RU",
                "trip_class": "Y",
                "sorting": "PRICE_ASC",
                "filters": {
                    "direct": True,
                    "no_visa_at_transfer": False,
                    "with_baggage": False
                }
            }
        },
        "operation_name": "best_directions_v1"
    }

    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

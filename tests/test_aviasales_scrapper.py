from pprint import pprint
from lib.find_all_destinations import query_aviasales, get_map_data
from lib.utils import get_first_day_of_next_month, get_last_day_of_next_month


def test_scrapper():
    result = query_aviasales('OVB', get_first_day_of_next_month(), get_last_day_of_next_month())
    assert 'errors' not in result
    assert 'data' in result
    pprint(result)


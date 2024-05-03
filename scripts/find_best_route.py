from pathlib import Path
import sys
import argparse

# To allow the import from the lib dir.
current_file = Path(__file__)
project_root = current_file.parent.parent.resolve()
sys.path.insert(0, str(project_root))

from lib.find_best_route import find_route

if __name__ == "__main__":
    """
    Currently this file can only be run from CLI - it's not a part of the web app.
    It can be run like this from the project root:

    python scripts/find_best_route.py DPS OVB [--max-price=70000] [--max-flights=2]
    """
    parser = argparse.ArgumentParser(description="Find the best route")
    parser.add_argument("origin", help="Origin airport IATA code")
    parser.add_argument("destination", help="Destination airport IATA code")
    parser.add_argument("--max-price", type=int, default=70000, help="Maximum price for the route")
    parser.add_argument("--max-flights", type=int, default=2, help="Maximum number of flights")

    args = parser.parse_args()

    find_route(args.origin, args.destination, max_price=args.max_price, max_flights=args.max_flights)

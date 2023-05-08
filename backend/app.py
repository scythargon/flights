from flask import Flask, jsonify, request
from flask_cors import CORS

from lib.search2 import get_map_data

app = Flask(__name__)
CORS(app)


@app.route('/api/marker')
def marker():
    origin = request.args.get('origin', '')
    destinations = get_map_data(origin, '2023-05-01')
    return jsonify(destinations['data']['map_v2']['prices'])


if __name__ == '__main__':
    app.run(port=8000, debug=True)
import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app: Flask):
    return app.test_client()

def test_direct_flights_view(client: FlaskClient):
    """
    Json structure expected by frontend:
    [{'iata': 'LON', 'lat': 51.51, 'lng': 0.06, 'min_price': 15243}, ...]
    """
    response = client.get('/api/marker?origin=NYC')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0

    assert 'iata' in data[0]
    assert 'lat' in data[0]
    assert 'lng' in data[0]
    assert 'min_price' in data[0]
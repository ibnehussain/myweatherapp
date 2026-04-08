"""
Tests for the Weather Dashboard Flask application.

Uses realistic dummy weather data (no live API calls required).
All external HTTP calls are intercepted with pytest-mock / unittest.mock.
"""

import pytest
import requests

from app import app, cache


# ---------------------------------------------------------------------------
# Realistic dummy weather payloads (mimic OpenWeatherMap API responses)
# ---------------------------------------------------------------------------

DUMMY_OWM_RESPONSES = {
    "london": {
        "name": "London",
        "main": {"temp": 14.2, "humidity": 72},
        "wind": {"speed": 5.1},
        "weather": [{"description": "light rain", "icon": "10d"}],
    },
    "new york": {
        "name": "New York",
        "main": {"temp": 22.5, "humidity": 58},
        "wind": {"speed": 4.6},
        "weather": [{"description": "clear sky", "icon": "01d"}],
    },
    "tokyo": {
        "name": "Tokyo",
        "main": {"temp": 28.0, "humidity": 80},
        "wind": {"speed": 3.2},
        "weather": [{"description": "few clouds", "icon": "02d"}],
    },
    "sydney": {
        "name": "Sydney",
        "main": {"temp": 18.7, "humidity": 65},
        "wind": {"speed": 6.8},
        "weather": [{"description": "scattered clouds", "icon": "03d"}],
    },
    "paris": {
        "name": "Paris",
        "main": {"temp": 11.3, "humidity": 68},
        "wind": {"speed": 4.0},
        "weather": [{"description": "overcast clouds", "icon": "04d"}],
    },
}

# Expected clean response shapes produced by the Flask app
DUMMY_CLEAN_RESPONSES = {
    "london": {
        "city": "London",
        "temperature": 14.2,
        "humidity": 72,
        "wind_speed": 5.1,
        "condition": "light rain",
        "icon": "10d",
    },
    "new york": {
        "city": "New York",
        "temperature": 22.5,
        "humidity": 58,
        "wind_speed": 4.6,
        "condition": "clear sky",
        "icon": "01d",
    },
    "tokyo": {
        "city": "Tokyo",
        "temperature": 28.0,
        "humidity": 80,
        "wind_speed": 3.2,
        "condition": "few clouds",
        "icon": "02d",
    },
    "sydney": {
        "city": "Sydney",
        "temperature": 18.7,
        "humidity": 65,
        "wind_speed": 6.8,
        "condition": "scattered clouds",
        "icon": "03d",
    },
    "paris": {
        "city": "Paris",
        "temperature": 11.3,
        "humidity": 68,
        "wind_speed": 4.0,
        "condition": "overcast clouds",
        "icon": "04d",
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(monkeypatch):
    """Return a test client with caching disabled and a fake API key."""
    app.config["TESTING"] = True
    app.config["CACHE_TYPE"] = "NullCache"
    monkeypatch.setenv("OWM_API_KEY", "test-api-key-12345")
    cache.init_app(app)
    with app.test_client() as c:
        yield c


def _make_mock_response(mocker, status_code, json_data=None):
    """Build a mock requests.Response object."""
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = status_code
    mock_resp.ok = (200 <= status_code < 300)
    mock_resp.json.return_value = json_data or {}
    return mock_resp


# ---------------------------------------------------------------------------
# Index route
# ---------------------------------------------------------------------------

class TestIndexRoute:
    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_html(self, client):
        response = client.get("/")
        assert b"<!DOCTYPE html>" in response.data or b"html" in response.data.lower()


# ---------------------------------------------------------------------------
# /api/weather -- input validation
# ---------------------------------------------------------------------------

class TestWeatherInputValidation:
    def test_missing_city_returns_400(self, client):
        response = client.get("/api/weather")
        assert response.status_code == 400
        assert b"City name is required" in response.data

    def test_empty_city_returns_400(self, client):
        response = client.get("/api/weather?city=")
        assert response.status_code == 400
        assert b"City name is required" in response.data

    def test_whitespace_only_city_returns_400(self, client):
        response = client.get("/api/weather?city=   ")
        assert response.status_code == 400
        assert b"City name is required" in response.data

    def test_invalid_units_returns_400(self, client):
        response = client.get("/api/weather?city=London&units=kelvin")
        assert response.status_code == 400
        assert b"Invalid units" in response.data

    def test_valid_metric_unit_accepted(self, client, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 200, DUMMY_OWM_RESPONSES["london"]),
        )
        response = client.get("/api/weather?city=London&units=metric")
        assert response.status_code == 200

    def test_valid_imperial_unit_accepted(self, client, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 200, DUMMY_OWM_RESPONSES["london"]),
        )
        response = client.get("/api/weather?city=London&units=imperial")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# /api/weather -- missing API key
# ---------------------------------------------------------------------------

class TestWeatherMissingApiKey:
    def test_no_api_key_returns_503(self, client, monkeypatch):
        monkeypatch.delenv("OWM_API_KEY", raising=False)
        response = client.get("/api/weather?city=London")
        assert response.status_code == 503
        assert b"not configured" in response.data


# ---------------------------------------------------------------------------
# /api/weather -- successful responses (realistic dummy data)
# ---------------------------------------------------------------------------

class TestWeatherSuccess:
    @pytest.mark.parametrize("city_key", DUMMY_OWM_RESPONSES.keys())
    def test_returns_200_for_known_cities(self, client, mocker, city_key):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 200, DUMMY_OWM_RESPONSES[city_key]),
        )
        response = client.get(f"/api/weather?city={city_key}")
        assert response.status_code == 200

    @pytest.mark.parametrize("city_key", DUMMY_CLEAN_RESPONSES.keys())
    def test_response_shape_matches_expected(self, client, mocker, city_key):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 200, DUMMY_OWM_RESPONSES[city_key]),
        )
        response = client.get(f"/api/weather?city={city_key}")
        data = response.get_json()
        expected = DUMMY_CLEAN_RESPONSES[city_key]
        assert data["city"] == expected["city"]
        assert data["temperature"] == expected["temperature"]
        assert data["humidity"] == expected["humidity"]
        assert data["wind_speed"] == expected["wind_speed"]
        assert data["condition"] == expected["condition"]
        assert data["icon"] == expected["icon"]

    def test_london_metric_temperature(self, client, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 200, DUMMY_OWM_RESPONSES["london"]),
        )
        data = client.get("/api/weather?city=London&units=metric").get_json()
        assert data["temperature"] == 14.2
        assert data["condition"] == "light rain"
        assert data["icon"] == "10d"

    def test_tokyo_high_humidity(self, client, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 200, DUMMY_OWM_RESPONSES["tokyo"]),
        )
        data = client.get("/api/weather?city=Tokyo").get_json()
        assert data["humidity"] == 80
        assert data["city"] == "Tokyo"


# ---------------------------------------------------------------------------
# /api/weather -- error responses from OWM
# ---------------------------------------------------------------------------

class TestWeatherErrorResponses:
    def test_city_not_found_returns_404(self, client, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 404),
        )
        response = client.get("/api/weather?city=Atlantis")
        assert response.status_code == 404
        assert b"not found" in response.data

    def test_invalid_api_key_returns_503(self, client, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 401),
        )
        response = client.get("/api/weather?city=London")
        assert response.status_code == 503
        assert b"Invalid API key" in response.data

    def test_owm_server_error_returns_503(self, client, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, 500),
        )
        response = client.get("/api/weather?city=London")
        assert response.status_code == 503

    def test_request_timeout_returns_503(self, client, mocker):
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.Timeout,
        )
        response = client.get("/api/weather?city=London")
        assert response.status_code == 503
        assert b"timed out" in response.data

    def test_connection_error_returns_503(self, client, mocker):
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.ConnectionError,
        )
        response = client.get("/api/weather?city=London")
        assert response.status_code == 503
        assert b"Unable to reach" in response.data


# ---------------------------------------------------------------------------
# /api/weather -- caching behaviour
# ---------------------------------------------------------------------------

class TestWeatherCaching:
    def test_cached_response_skips_api_call(self, monkeypatch, mocker):
        """Pre-populate the cache; the API must NOT be called."""
        app.config["TESTING"] = True
        app.config["CACHE_TYPE"] = "SimpleCache"
        monkeypatch.setenv("OWM_API_KEY", "test-api-key-12345")
        cache.init_app(app)

        with app.test_client() as c:
            # Seed the cache directly
            with app.app_context():
                cache.set("weather:london:metric", DUMMY_CLEAN_RESPONSES["london"])

            mock_get = mocker.patch("requests.get")
            response = c.get("/api/weather?city=london&units=metric")

            mock_get.assert_not_called()
            assert response.status_code == 200
            data = response.get_json()
            assert data["city"] == "London"

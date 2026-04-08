import os
"""
Weather API Flask Application
A Flask web application that provides a REST API for retrieving weather information
using the OpenWeatherMap API. The application includes caching, CORS support, and
error handling for robust weather data retrieval.
Features:
    - Serves an HTML index page at the root route
    - Provides weather data via /api/weather endpoint with caching
    - Supports metric and imperial units
    - Implements CORS with configurable allowed origins
    - Includes request timeout and error handling
    - Caches weather data for 10 minutes to reduce API calls
Routes:
    GET /: Renders the main index.html template
    GET /api/weather: Returns weather data for a specified city
        Query Parameters:
            - city (required): The name of the city to get weather for
            - units (optional): Temperature units - 'metric' (default) or 'imperial'
        Returns:
            - 200: JSON object with weather data (city, temperature, humidity, wind_speed, condition, icon)
            - 400: JSON error if city is missing or units are invalid
            - 404: JSON error if city is not found
            - 503: JSON error if API key is missing, is invalid, or service is unavailable
Environment Variables:
    - ALLOWED_ORIGIN: CORS allowed origin (default: http://localhost:5000)
    - OWM_API_KEY: OpenWeatherMap API key (required for weather endpoint)
    - FLASK_DEBUG: Enable Flask debug mode (default: false)
Dependencies:
    - flask: Web framework
    - flask_caching: Caching support
    - flask_cors: CORS support
    - requests: HTTP client library
    - python-dotenv: Environment variable loading
"""
import requests
from flask import Flask, jsonify, render_template, request
from flask_caching import Cache
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("ALLOWED_ORIGIN", "http://localhost:5000")}})

app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 600  # 10 minutes
cache = Cache(app)

OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def get_weather():
    city = request.args.get("city", "").strip()
    units = request.args.get("units", "metric")

    if not city:
        return jsonify({"error": "City name is required."}), 400

    if units not in ("metric", "imperial"):
        return jsonify({"error": "Invalid units. Use 'metric' or 'imperial'."}), 400

    cache_key = f"weather:{city.lower()}:{units}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify(cached)

    api_key = os.getenv("OWM_API_KEY")
    if not api_key:
        return jsonify({"error": "Weather service is not configured."}), 503

    try:
        response = requests.get(
            OWM_BASE_URL,
            params={"q": city, "appid": api_key, "units": units},
            timeout=5,
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": "Weather service timed out. Please try again."}), 503
    except requests.exceptions.RequestException:
        return jsonify({"error": "Unable to reach weather service."}), 503

    if response.status_code == 404:
        return jsonify({"error": f"City '{city}' not found."}), 404
    if response.status_code == 401:
        return jsonify({"error": "Invalid API key."}), 503
    if not response.ok:
        return jsonify({"error": "Weather service returned an unexpected error."}), 503

    raw = response.json()

    data = {
        "city":        raw["name"],
        "temperature": raw["main"]["temp"],
        "humidity":    raw["main"]["humidity"],
        "wind_speed":  raw["wind"]["speed"],
        "condition":   raw["weather"][0]["description"],
        "icon":        raw["weather"][0]["icon"],
    }

    cache.set(cache_key, data)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")

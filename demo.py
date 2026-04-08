"""
demo.py — Run the Weather Dashboard with pre-loaded dummy data.

Starts the Flask development server with realistic dummy weather data
already seeded into the in-memory cache, so the application can be
explored without a live OpenWeatherMap API key.

Usage:
    python demo.py

Then open http://localhost:5000 and search for any of the pre-loaded cities:
    London, New York, Tokyo, Sydney, Paris, Berlin, Dubai, Mumbai, Toronto, Rio de Janeiro
"""

import os
from app import app, cache

# ---------------------------------------------------------------------------
# Realistic dummy weather data for ten major cities
# ---------------------------------------------------------------------------

DUMMY_DATA = [
    {
        "city": "London",
        "units": "metric",
        "data": {
            "city": "London",
            "temperature": 14.2,
            "humidity": 72,
            "wind_speed": 5.1,
            "condition": "light rain",
            "icon": "10d",
        },
    },
    {
        "city": "New York",
        "units": "metric",
        "data": {
            "city": "New York",
            "temperature": 22.5,
            "humidity": 58,
            "wind_speed": 4.6,
            "condition": "clear sky",
            "icon": "01d",
        },
    },
    {
        "city": "Tokyo",
        "units": "metric",
        "data": {
            "city": "Tokyo",
            "temperature": 28.0,
            "humidity": 80,
            "wind_speed": 3.2,
            "condition": "few clouds",
            "icon": "02d",
        },
    },
    {
        "city": "Sydney",
        "units": "metric",
        "data": {
            "city": "Sydney",
            "temperature": 18.7,
            "humidity": 65,
            "wind_speed": 6.8,
            "condition": "scattered clouds",
            "icon": "03d",
        },
    },
    {
        "city": "Paris",
        "units": "metric",
        "data": {
            "city": "Paris",
            "temperature": 11.3,
            "humidity": 68,
            "wind_speed": 4.0,
            "condition": "overcast clouds",
            "icon": "04d",
        },
    },
    {
        "city": "Berlin",
        "units": "metric",
        "data": {
            "city": "Berlin",
            "temperature": 9.8,
            "humidity": 74,
            "wind_speed": 5.5,
            "condition": "broken clouds",
            "icon": "04d",
        },
    },
    {
        "city": "Dubai",
        "units": "metric",
        "data": {
            "city": "Dubai",
            "temperature": 38.4,
            "humidity": 35,
            "wind_speed": 4.2,
            "condition": "sunny",
            "icon": "01d",
        },
    },
    {
        "city": "Mumbai",
        "units": "metric",
        "data": {
            "city": "Mumbai",
            "temperature": 31.6,
            "humidity": 88,
            "wind_speed": 7.3,
            "condition": "moderate rain",
            "icon": "10d",
        },
    },
    {
        "city": "Toronto",
        "units": "metric",
        "data": {
            "city": "Toronto",
            "temperature": 5.2,
            "humidity": 60,
            "wind_speed": 8.9,
            "condition": "light snow",
            "icon": "13d",
        },
    },
    {
        "city": "Rio de Janeiro",
        "units": "metric",
        "data": {
            "city": "Rio de Janeiro",
            "temperature": 29.1,
            "humidity": 75,
            "wind_speed": 3.8,
            "condition": "partly cloudy",
            "icon": "02d",
        },
    },
]


def seed_cache():
    """Populate the in-memory cache with dummy weather entries."""
    with app.app_context():
        for entry in DUMMY_DATA:
            key = f"weather:{entry['city'].lower()}:{entry['units']}"
            cache.set(key, entry["data"])
    print("Demo cache seeded with data for:")
    for entry in DUMMY_DATA:
        d = entry["data"]
        print(
            f"  {d['city']:<18} {d['temperature']:>5} °C  "
            f"Humidity {d['humidity']}%  Wind {d['wind_speed']} m/s  "
            f"— {d['condition']}"
        )


if __name__ == "__main__":
    # Provide a placeholder key so the app does not return 503 when the
    # cache is missed (e.g. a city not in the seed list).
    if not os.getenv("OWM_API_KEY"):
        os.environ["OWM_API_KEY"] = "DEMO_KEY_NOT_REAL"

    seed_cache()
    print("\nStarting demo server at http://localhost:5000")
    print("Try searching for: London, New York, Tokyo, Sydney, Paris, ...")
    print("Press Ctrl+C to stop.\n")
    app.run(debug=False, port=5000)

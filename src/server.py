#!/usr/bin/env python3
"""
meteo-static: Mock meteorological MCP server with fixed weather data.

Exposes tools for querying current weather, forecasts, and supported cities.
Supports stdio and streamable HTTP transports.

Usage:
    # STDIO (default)
    python src/server.py

    # Streamable HTTP
    python src/server.py --transport http --port 8000
"""

import argparse
from typing import Any

from mcp.server.fastmcp import FastMCP

# Fixed weather data for demo/validation purposes
CITIES: dict[str, dict[str, Any]] = {
    "paris": {
        "name": "Paris",
        "country": "FR",
        "lat": 48.85,
        "lon": 2.35,
        "temp_c": 15.0,
        "feels_like_c": 13.5,
        "humidity_pct": 72,
        "wind_kph": 11.0,
        "condition": "Partly cloudy",
        "precip_mm": 1.2,
    },
    "sydney": {
        "name": "Sydney",
        "country": "AU",
        "lat": -33.87,
        "lon": 151.21,
        "temp_c": 24.0,
        "feels_like_c": 25.5,
        "humidity_pct": 65,
        "wind_kph": 17.0,
        "condition": "Sunny",
        "precip_mm": 0.0,
    },
    "dubai": {
        "name": "Dubai",
        "country": "AE",
        "lat": 25.20,
        "lon": 55.27,
        "temp_c": 38.0,
        "feels_like_c": 42.0,
        "humidity_pct": 45,
        "wind_kph": 13.0,
        "condition": "Clear",
        "precip_mm": 0.0,
    },
    "moscow": {
        "name": "Moscow",
        "country": "RU",
        "lat": 55.75,
        "lon": 37.62,
        "temp_c": -3.0,
        "feels_like_c": -8.0,
        "humidity_pct": 85,
        "wind_kph": 20.0,
        "condition": "Snow",
        "precip_mm": 3.5,
    },
    "sao_paulo": {
        "name": "São Paulo",
        "country": "BR",
        "lat": -23.55,
        "lon": -46.63,
        "temp_c": 28.0,
        "feels_like_c": 31.0,
        "humidity_pct": 80,
        "wind_kph": 9.0,
        "condition": "Thunderstorm",
        "precip_mm": 12.0,
    },
    "cape_town": {
        "name": "Cape Town",
        "country": "ZA",
        "lat": -33.93,
        "lon": 18.42,
        "temp_c": 20.0,
        "feels_like_c": 19.0,
        "humidity_pct": 58,
        "wind_kph": 25.0,
        "condition": "Windy",
        "precip_mm": 0.0,
    },
    "tokyo": {
        "name": "Tokyo",
        "country": "JP",
        "lat": 35.68,
        "lon": 139.69,
        "temp_c": 8.5,
        "feels_like_c": 5.0,
        "humidity_pct": 62,
        "wind_kph": 15.0,
        "condition": "Partly cloudy",
        "precip_mm": 0.0,
    },
    "new_york": {
        "name": "New York",
        "country": "US",
        "lat": 40.71,
        "lon": -74.01,
        "temp_c": 22.5,
        "feels_like_c": 24.0,
        "humidity_pct": 78,
        "wind_kph": 8.0,
        "condition": "Sunny",
        "precip_mm": 0.0,
    },
    "london": {
        "name": "London",
        "country": "GB",
        "lat": 51.51,
        "lon": -0.13,
        "temp_c": 12.0,
        "feels_like_c": 10.0,
        "humidity_pct": 81,
        "wind_kph": 22.0,
        "condition": "Rainy",
        "precip_mm": 5.2,
    },
    "san_francisco": {
        "name": "San Francisco",
        "country": "US",
        "lat": 37.77,
        "lon": -122.42,
        "temp_c": 18.0,
        "feels_like_c": 17.5,
        "humidity_pct": 68,
        "wind_kph": 19.0,
        "condition": "Foggy",
        "precip_mm": 0.0,
    },
}

# Mock forecasts (3-day)
FORECASTS: dict[str, list[dict[str, Any]]] = {
    "paris": [
        {"day": "Monday", "high_c": 16.0, "low_c": 10.0, "condition": "Cloudy"},
        {"day": "Tuesday", "high_c": 18.0, "low_c": 11.0, "condition": "Partly cloudy"},
        {"day": "Wednesday", "high_c": 17.0, "low_c": 10.0, "condition": "Rainy"},
    ],
    "sydney": [
        {"day": "Monday", "high_c": 25.0, "low_c": 18.0, "condition": "Sunny"},
        {"day": "Tuesday", "high_c": 26.0, "low_c": 19.0, "condition": "Sunny"},
        {"day": "Wednesday", "high_c": 23.0, "low_c": 17.0, "condition": "Partly cloudy"},
    ],
    "dubai": [
        {"day": "Monday", "high_c": 39.0, "low_c": 30.0, "condition": "Clear"},
        {"day": "Tuesday", "high_c": 38.0, "low_c": 29.0, "condition": "Clear"},
        {"day": "Wednesday", "high_c": 40.0, "low_c": 31.0, "condition": "Clear"},
    ],
    "moscow": [
        {"day": "Monday", "high_c": -2.0, "low_c": -7.0, "condition": "Snow"},
        {"day": "Tuesday", "high_c": 0.0, "low_c": -5.0, "condition": "Cloudy"},
        {"day": "Wednesday", "high_c": 1.0, "low_c": -4.0, "condition": "Partly cloudy"},
    ],
    "sao_paulo": [
        {"day": "Monday", "high_c": 29.0, "low_c": 22.0, "condition": "Thunderstorm"},
        {"day": "Tuesday", "high_c": 30.0, "low_c": 23.0, "condition": "Partly cloudy"},
        {"day": "Wednesday", "high_c": 28.0, "low_c": 21.0, "condition": "Sunny"},
    ],
    "cape_town": [
        {"day": "Monday", "high_c": 21.0, "low_c": 14.0, "condition": "Windy"},
        {"day": "Tuesday", "high_c": 22.0, "low_c": 15.0, "condition": "Sunny"},
        {"day": "Wednesday", "high_c": 20.0, "low_c": 13.0, "condition": "Partly cloudy"},
    ],
    "tokyo": [
        {"day": "Monday", "high_c": 10.0, "low_c": 4.0, "condition": "Cloudy"},
        {"day": "Tuesday", "high_c": 11.0, "low_c": 5.0, "condition": "Partly cloudy"},
        {"day": "Wednesday", "high_c": 9.0, "low_c": 3.0, "condition": "Rainy"},
    ],
    "new_york": [
        {"day": "Monday", "high_c": 24.0, "low_c": 18.0, "condition": "Sunny"},
        {"day": "Tuesday", "high_c": 25.0, "low_c": 19.0, "condition": "Sunny"},
        {"day": "Wednesday", "high_c": 23.0, "low_c": 17.0, "condition": "Partly cloudy"},
    ],
    "london": [
        {"day": "Monday", "high_c": 13.0, "low_c": 8.0, "condition": "Rainy"},
        {"day": "Tuesday", "high_c": 14.0, "low_c": 9.0, "condition": "Cloudy"},
        {"day": "Wednesday", "high_c": 15.0, "low_c": 10.0, "condition": "Partly cloudy"},
    ],
    "san_francisco": [
        {"day": "Monday", "high_c": 19.0, "low_c": 12.0, "condition": "Foggy"},
        {"day": "Tuesday", "high_c": 20.0, "low_c": 13.0, "condition": "Sunny"},
        {"day": "Wednesday", "high_c": 21.0, "low_c": 14.0, "condition": "Sunny"},
    ],
}


# -- MCP tools ------------------------------------------------------------

mcp = FastMCP("meteo-static")


@mcp.tool()
def list_cities() -> list[str]:
    """List all supported cities for weather queries.

    Returns display names that can be used directly with get_weather and get_forecast.
    """
    return [info["name"] for info in CITIES.values()]


@mcp.tool()
def get_weather(city: str) -> dict[str, Any]:
    """Get current weather for a city.

    Args:
        city: City key or display name (e.g. 'tokyo', 'Tokyo', 'New York').
    """
    # Try direct key match first (case-insensitive)
    info = CITIES.get(city.lower())
    if info is None:
        # Fallback: match by display name (case-insensitive)
        for key, val in CITIES.items():
            if val["name"].lower() == city.lower():
                info = val
                break
    if info is None:
        return {"error": f"Unknown city: {city}"}
    return {
        "city": info["name"],
        "country": info["country"],
        "temp_c": info["temp_c"],
        "feels_like_c": info["feels_like_c"],
        "humidity_pct": info["humidity_pct"],
        "wind_kph": info["wind_kph"],
        "condition": info["condition"],
        "precip_mm": info["precip_mm"],
    }


@mcp.tool()
def get_forecast(city: str) -> list[dict[str, Any]]:
    """Get a 3-day forecast for a city.

    Args:
        city: City key or display name (e.g. 'tokyo', 'Tokyo', 'New York').
    """
    # Try direct key match first (case-insensitive)
    data = FORECASTS.get(city.lower())
    if data is None:
        # Fallback: match by display name (case-insensitive)
        for key, val in CITIES.items():
            if val["name"].lower() == city.lower():
                data = FORECASTS.get(key)
                break
    if data is None:
        return [{"error": f"Unknown city: {city}"}]
    return data


@mcp.tool()
def get_air_quality(city: str) -> dict[str, Any]:
    """Get current air quality index (AQI) for a city.

    Args:
        city: City key or display name (e.g. 'tokyo', 'London').
    """
    _AQI: dict[str, dict[str, Any]] = {
        "tokyo": {
            "aqi": 42,
            "category": "Good",
            "pm2_5_ugm3": 8.1,
            "pm10_ugm3": 14.3,
            "o3_ppb": 28,
        },
        "new_york": {
            "aqi": 55,
            "category": "Moderate",
            "pm2_5_ugm3": 12.4,
            "pm10_ugm3": 21.0,
            "o3_ppb": 34,
        },
        "london": {
            "aqi": 61,
            "category": "Moderate",
            "pm2_5_ugm3": 15.2,
            "pm10_ugm3": 24.8,
            "o3_ppb": 30,
        },
        "san_francisco": {
            "aqi": 38,
            "category": "Good",
            "pm2_5_ugm3": 7.0,
            "pm10_ugm3": 11.5,
            "o3_ppb": 22,
        },
        "paris": {
            "aqi": 67,
            "category": "Moderate",
            "pm2_5_ugm3": 16.0,
            "pm10_ugm3": 26.2,
            "o3_ppb": 36,
        },
        "sydney": {
            "aqi": 29,
            "category": "Good",
            "pm2_5_ugm3": 5.3,
            "pm10_ugm3": 9.1,
            "o3_ppb": 18,
        },
        "dubai": {
            "aqi": 110,
            "category": "Unhealthy for Sensitive Groups",
            "pm2_5_ugm3": 38.0,
            "pm10_ugm3": 82.0,
            "o3_ppb": 44,
        },
        "moscow": {
            "aqi": 73,
            "category": "Moderate",
            "pm2_5_ugm3": 18.5,
            "pm10_ugm3": 30.0,
            "o3_ppb": 25,
        },
        "sao_paulo": {
            "aqi": 95,
            "category": "Unhealthy for Sensitive Groups",
            "pm2_5_ugm3": 28.0,
            "pm10_ugm3": 52.0,
            "o3_ppb": 41,
        },
        "cape_town": {
            "aqi": 33,
            "category": "Good",
            "pm2_5_ugm3": 6.0,
            "pm10_ugm3": 10.4,
            "o3_ppb": 20,
        },
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _AQI.get(key)
    if data is None:
        return {"error": f"No air quality data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_uv_index(city: str) -> dict[str, Any]:
    """Get the current UV index for a city.

    Args:
        city: City key or display name (e.g. 'sydney', 'Dubai').
    """
    _UV: dict[str, dict[str, Any]] = {
        "tokyo": {"uv_index": 2, "exposure_category": "Low"},
        "new_york": {"uv_index": 5, "exposure_category": "Moderate"},
        "london": {"uv_index": 1, "exposure_category": "Low"},
        "san_francisco": {"uv_index": 6, "exposure_category": "High"},
        "paris": {"uv_index": 3, "exposure_category": "Moderate"},
        "sydney": {"uv_index": 11, "exposure_category": "Extreme"},
        "dubai": {"uv_index": 10, "exposure_category": "Very High"},
        "moscow": {"uv_index": 1, "exposure_category": "Low"},
        "sao_paulo": {"uv_index": 9, "exposure_category": "Very High"},
        "cape_town": {"uv_index": 7, "exposure_category": "High"},
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _UV.get(key)
    if data is None:
        return {"error": f"No UV data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_wind_detail(city: str) -> dict[str, Any]:
    """Get detailed wind information for a city, including direction and gusts.

    Args:
        city: City key or display name (e.g. 'london', 'Cape Town').
    """
    _WIND: dict[str, dict[str, Any]] = {
        "tokyo": {
            "speed_kph": 15.0,
            "direction_deg": 270,
            "direction_label": "W",
            "gust_kph": 24.0,
        },
        "new_york": {
            "speed_kph": 8.0,
            "direction_deg": 200,
            "direction_label": "SSW",
            "gust_kph": 13.0,
        },
        "london": {
            "speed_kph": 22.0,
            "direction_deg": 240,
            "direction_label": "WSW",
            "gust_kph": 35.0,
        },
        "san_francisco": {
            "speed_kph": 19.0,
            "direction_deg": 300,
            "direction_label": "WNW",
            "gust_kph": 28.0,
        },
        "paris": {
            "speed_kph": 11.0,
            "direction_deg": 220,
            "direction_label": "SW",
            "gust_kph": 18.0,
        },
        "sydney": {
            "speed_kph": 17.0,
            "direction_deg": 135,
            "direction_label": "SE",
            "gust_kph": 25.0,
        },
        "dubai": {
            "speed_kph": 13.0,
            "direction_deg": 315,
            "direction_label": "NW",
            "gust_kph": 20.0,
        },
        "moscow": {
            "speed_kph": 20.0,
            "direction_deg": 10,
            "direction_label": "N",
            "gust_kph": 30.0,
        },
        "sao_paulo": {
            "speed_kph": 9.0,
            "direction_deg": 90,
            "direction_label": "E",
            "gust_kph": 15.0,
        },
        "cape_town": {
            "speed_kph": 25.0,
            "direction_deg": 180,
            "direction_label": "S",
            "gust_kph": 42.0,
        },
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _WIND.get(key)
    if data is None:
        return {"error": f"No wind data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_humidity(city: str) -> dict[str, Any]:
    """Get current humidity and dew point for a city.

    Args:
        city: City key or display name (e.g. 'tokyo', 'São Paulo').
    """
    _HUMIDITY: dict[str, dict[str, Any]] = {
        "tokyo": {"humidity_pct": 62, "dew_point_c": 1.6, "comfort": "Comfortable"},
        "new_york": {"humidity_pct": 78, "dew_point_c": 18.6, "comfort": "Humid"},
        "london": {"humidity_pct": 81, "dew_point_c": 9.1, "comfort": "Humid"},
        "san_francisco": {"humidity_pct": 68, "dew_point_c": 11.9, "comfort": "Comfortable"},
        "paris": {"humidity_pct": 72, "dew_point_c": 10.0, "comfort": "Comfortable"},
        "sydney": {"humidity_pct": 65, "dew_point_c": 17.1, "comfort": "Comfortable"},
        "dubai": {"humidity_pct": 45, "dew_point_c": 24.3, "comfort": "Dry"},
        "moscow": {"humidity_pct": 85, "dew_point_c": -5.1, "comfort": "Comfortable"},
        "sao_paulo": {"humidity_pct": 80, "dew_point_c": 24.5, "comfort": "Very Humid"},
        "cape_town": {"humidity_pct": 58, "dew_point_c": 11.7, "comfort": "Comfortable"},
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _HUMIDITY.get(key)
    if data is None:
        return {"error": f"No humidity data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_precipitation_chance(city: str) -> dict[str, Any]:
    """Get the hourly precipitation probability for the next 6 hours for a city.

    Args:
        city: City key or display name (e.g. 'london', 'Moscow').
    """
    _PRECIP: dict[str, list[dict[str, Any]]] = {
        "tokyo": [
            {"hour": "+1h", "prob_pct": 5},
            {"hour": "+2h", "prob_pct": 5},
            {"hour": "+3h", "prob_pct": 10},
            {"hour": "+4h", "prob_pct": 10},
            {"hour": "+5h", "prob_pct": 15},
            {"hour": "+6h", "prob_pct": 20},
        ],
        "new_york": [
            {"hour": "+1h", "prob_pct": 0},
            {"hour": "+2h", "prob_pct": 0},
            {"hour": "+3h", "prob_pct": 5},
            {"hour": "+4h", "prob_pct": 5},
            {"hour": "+5h", "prob_pct": 10},
            {"hour": "+6h", "prob_pct": 10},
        ],
        "london": [
            {"hour": "+1h", "prob_pct": 70},
            {"hour": "+2h", "prob_pct": 75},
            {"hour": "+3h", "prob_pct": 80},
            {"hour": "+4h", "prob_pct": 65},
            {"hour": "+5h", "prob_pct": 60},
            {"hour": "+6h", "prob_pct": 50},
        ],
        "san_francisco": [
            {"hour": "+1h", "prob_pct": 10},
            {"hour": "+2h", "prob_pct": 10},
            {"hour": "+3h", "prob_pct": 5},
            {"hour": "+4h", "prob_pct": 5},
            {"hour": "+5h", "prob_pct": 0},
            {"hour": "+6h", "prob_pct": 0},
        ],
        "paris": [
            {"hour": "+1h", "prob_pct": 40},
            {"hour": "+2h", "prob_pct": 45},
            {"hour": "+3h", "prob_pct": 50},
            {"hour": "+4h", "prob_pct": 55},
            {"hour": "+5h", "prob_pct": 45},
            {"hour": "+6h", "prob_pct": 35},
        ],
        "sydney": [
            {"hour": "+1h", "prob_pct": 0},
            {"hour": "+2h", "prob_pct": 0},
            {"hour": "+3h", "prob_pct": 0},
            {"hour": "+4h", "prob_pct": 5},
            {"hour": "+5h", "prob_pct": 5},
            {"hour": "+6h", "prob_pct": 10},
        ],
        "dubai": [
            {"hour": "+1h", "prob_pct": 0},
            {"hour": "+2h", "prob_pct": 0},
            {"hour": "+3h", "prob_pct": 0},
            {"hour": "+4h", "prob_pct": 0},
            {"hour": "+5h", "prob_pct": 0},
            {"hour": "+6h", "prob_pct": 0},
        ],
        "moscow": [
            {"hour": "+1h", "prob_pct": 60},
            {"hour": "+2h", "prob_pct": 65},
            {"hour": "+3h", "prob_pct": 70},
            {"hour": "+4h", "prob_pct": 60},
            {"hour": "+5h", "prob_pct": 55},
            {"hour": "+6h", "prob_pct": 50},
        ],
        "sao_paulo": [
            {"hour": "+1h", "prob_pct": 85},
            {"hour": "+2h", "prob_pct": 90},
            {"hour": "+3h", "prob_pct": 80},
            {"hour": "+4h", "prob_pct": 70},
            {"hour": "+5h", "prob_pct": 60},
            {"hour": "+6h", "prob_pct": 50},
        ],
        "cape_town": [
            {"hour": "+1h", "prob_pct": 10},
            {"hour": "+2h", "prob_pct": 10},
            {"hour": "+3h", "prob_pct": 5},
            {"hour": "+4h", "prob_pct": 5},
            {"hour": "+5h", "prob_pct": 0},
            {"hour": "+6h", "prob_pct": 0},
        ],
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _PRECIP.get(key)
    if data is None:
        return {"error": f"No precipitation data for: {city}"}
    return {"city": CITIES[key]["name"], "hourly": data}


@mcp.tool()
def get_sunrise_sunset(city: str) -> dict[str, Any]:
    """Get today's sunrise and sunset times (UTC) for a city.

    Args:
        city: City key or display name (e.g. 'tokyo', 'Sydney').
    """
    _SUNTIMES: dict[str, dict[str, str]] = {
        "tokyo": {"sunrise_utc": "20:48", "sunset_utc": "08:15"},
        "new_york": {"sunrise_utc": "09:52", "sunset_utc": "23:45"},
        "london": {"sunrise_utc": "05:14", "sunset_utc": "20:04"},
        "san_francisco": {"sunrise_utc": "13:01", "sunset_utc": "03:09"},
        "paris": {"sunrise_utc": "04:29", "sunset_utc": "19:54"},
        "sydney": {"sunrise_utc": "21:01", "sunset_utc": "07:15"},
        "dubai": {"sunrise_utc": "02:21", "sunset_utc": "14:48"},
        "moscow": {"sunrise_utc": "02:21", "sunset_utc": "17:20"},
        "sao_paulo": {"sunrise_utc": "08:53", "sunset_utc": "21:08"},
        "cape_town": {"sunrise_utc": "05:10", "sunset_utc": "15:41"},
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _SUNTIMES.get(key)
    if data is None:
        return {"error": f"No sun time data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_visibility(city: str) -> dict[str, Any]:
    """Get current atmospheric visibility for a city.

    Args:
        city: City key or display name (e.g. 'san_francisco', 'Dubai').
    """
    _VIS: dict[str, dict[str, Any]] = {
        "tokyo": {"visibility_km": 14.0, "description": "Clear"},
        "new_york": {"visibility_km": 16.0, "description": "Clear"},
        "london": {"visibility_km": 8.0, "description": "Mist"},
        "san_francisco": {"visibility_km": 4.0, "description": "Foggy"},
        "paris": {"visibility_km": 10.0, "description": "Haze"},
        "sydney": {"visibility_km": 20.0, "description": "Clear"},
        "dubai": {"visibility_km": 6.0, "description": "Haze / Dust"},
        "moscow": {"visibility_km": 5.0, "description": "Snow / Haze"},
        "sao_paulo": {"visibility_km": 7.0, "description": "Haze"},
        "cape_town": {"visibility_km": 18.0, "description": "Clear"},
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _VIS.get(key)
    if data is None:
        return {"error": f"No visibility data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_pressure(city: str) -> dict[str, Any]:
    """Get current atmospheric pressure for a city.

    Args:
        city: City key or display name (e.g. 'london', 'Moscow').
    """
    _PRESSURE: dict[str, dict[str, Any]] = {
        "tokyo": {"pressure_hpa": 1018.0, "trend": "Steady"},
        "new_york": {"pressure_hpa": 1012.5, "trend": "Rising"},
        "london": {"pressure_hpa": 1005.0, "trend": "Falling"},
        "san_francisco": {"pressure_hpa": 1016.0, "trend": "Steady"},
        "paris": {"pressure_hpa": 1008.0, "trend": "Falling"},
        "sydney": {"pressure_hpa": 1020.5, "trend": "Rising"},
        "dubai": {"pressure_hpa": 1005.0, "trend": "Steady"},
        "moscow": {"pressure_hpa": 1000.0, "trend": "Falling"},
        "sao_paulo": {"pressure_hpa": 1010.0, "trend": "Steady"},
        "cape_town": {"pressure_hpa": 1022.0, "trend": "Rising"},
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _PRESSURE.get(key)
    if data is None:
        return {"error": f"No pressure data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_moon_phase(city: str) -> dict[str, Any]:
    """Get the current lunar (moon) phase for a city's location.

    Args:
        city: City key or display name (e.g. 'tokyo', 'London').
    """
    _MOON: dict[str, dict[str, Any]] = {
        "tokyo": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "new_york": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "london": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "san_francisco": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "paris": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "sydney": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "dubai": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "moscow": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "sao_paulo": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
        "cape_town": {"phase": "Waxing Gibbous", "illumination_pct": 72, "age_days": 10},
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _MOON.get(key)
    if data is None:
        return {"error": f"No moon phase data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_pollen_forecast(city: str) -> dict[str, Any]:
    """Get current pollen levels and dominant pollen type for a city.

    Args:
        city: City key or display name (e.g. 'paris', 'Sydney').
    """
    _POLLEN: dict[str, dict[str, Any]] = {
        "tokyo": {"level": "High", "score": 7, "dominant_type": "Cedar", "risk": "Moderate"},
        "new_york": {"level": "Moderate", "score": 5, "dominant_type": "Grass", "risk": "Moderate"},
        "london": {"level": "Low", "score": 2, "dominant_type": "Tree", "risk": "Low"},
        "san_francisco": {"level": "Low", "score": 3, "dominant_type": "Grass", "risk": "Low"},
        "paris": {"level": "High", "score": 8, "dominant_type": "Birch", "risk": "High"},
        "sydney": {"level": "Moderate", "score": 5, "dominant_type": "Grass", "risk": "Moderate"},
        "dubai": {"level": "Low", "score": 1, "dominant_type": "Weed", "risk": "Low"},
        "moscow": {"level": "Low", "score": 2, "dominant_type": "Tree", "risk": "Low"},
        "sao_paulo": {
            "level": "Moderate",
            "score": 4,
            "dominant_type": "Grass",
            "risk": "Moderate",
        },
        "cape_town": {
            "level": "Moderate",
            "score": 5,
            "dominant_type": "Grass",
            "risk": "Moderate",
        },
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _POLLEN.get(key)
    if data is None:
        return {"error": f"No pollen data for: {city}"}
    return {"city": CITIES[key]["name"], **data}


@mcp.tool()
def get_feels_like_detail(city: str) -> dict[str, Any]:
    """Get detailed apparent temperature breakdown (wind chill, heat index) for a city.

    Args:
        city: City key or display name (e.g. 'moscow', 'Dubai').
    """
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    info = CITIES.get(key)
    if info is None:
        return {"error": f"Unknown city: {city}"}
    temp = info["temp_c"]
    feels = info["feels_like_c"]
    diff = round(feels - temp, 1)
    factor = "Wind chill" if diff < 0 else ("Heat index" if diff > 0 else "Neutral")
    return {
        "city": info["name"],
        "temp_c": temp,
        "feels_like_c": feels,
        "difference_c": diff,
        "dominant_factor": factor,
    }


@mcp.tool()
def get_hourly_temperature(city: str) -> dict[str, Any]:
    """Get hourly temperature for the next 6 hours for a city.

    Args:
        city: City key or display name (e.g. 'new_york', 'Sydney').
    """
    _HOURLY: dict[str, list[dict[str, Any]]] = {
        "tokyo": [
            {"hour": "+1h", "temp_c": 8.8},
            {"hour": "+2h", "temp_c": 9.1},
            {"hour": "+3h", "temp_c": 9.5},
            {"hour": "+4h", "temp_c": 9.2},
            {"hour": "+5h", "temp_c": 8.9},
            {"hour": "+6h", "temp_c": 8.5},
        ],
        "new_york": [
            {"hour": "+1h", "temp_c": 22.8},
            {"hour": "+2h", "temp_c": 23.0},
            {"hour": "+3h", "temp_c": 23.5},
            {"hour": "+4h", "temp_c": 23.2},
            {"hour": "+5h", "temp_c": 22.9},
            {"hour": "+6h", "temp_c": 22.5},
        ],
        "london": [
            {"hour": "+1h", "temp_c": 12.2},
            {"hour": "+2h", "temp_c": 12.4},
            {"hour": "+3h", "temp_c": 12.1},
            {"hour": "+4h", "temp_c": 11.8},
            {"hour": "+5h", "temp_c": 11.5},
            {"hour": "+6h", "temp_c": 11.2},
        ],
        "san_francisco": [
            {"hour": "+1h", "temp_c": 18.2},
            {"hour": "+2h", "temp_c": 18.5},
            {"hour": "+3h", "temp_c": 19.0},
            {"hour": "+4h", "temp_c": 19.3},
            {"hour": "+5h", "temp_c": 19.0},
            {"hour": "+6h", "temp_c": 18.7},
        ],
        "paris": [
            {"hour": "+1h", "temp_c": 15.2},
            {"hour": "+2h", "temp_c": 15.5},
            {"hour": "+3h", "temp_c": 15.8},
            {"hour": "+4h", "temp_c": 15.5},
            {"hour": "+5h", "temp_c": 15.2},
            {"hour": "+6h", "temp_c": 14.9},
        ],
        "sydney": [
            {"hour": "+1h", "temp_c": 24.3},
            {"hour": "+2h", "temp_c": 24.6},
            {"hour": "+3h", "temp_c": 25.0},
            {"hour": "+4h", "temp_c": 24.8},
            {"hour": "+5h", "temp_c": 24.5},
            {"hour": "+6h", "temp_c": 24.1},
        ],
        "dubai": [
            {"hour": "+1h", "temp_c": 38.2},
            {"hour": "+2h", "temp_c": 38.5},
            {"hour": "+3h", "temp_c": 38.8},
            {"hour": "+4h", "temp_c": 39.0},
            {"hour": "+5h", "temp_c": 38.7},
            {"hour": "+6h", "temp_c": 38.3},
        ],
        "moscow": [
            {"hour": "+1h", "temp_c": -2.8},
            {"hour": "+2h", "temp_c": -3.0},
            {"hour": "+3h", "temp_c": -3.3},
            {"hour": "+4h", "temp_c": -3.5},
            {"hour": "+5h", "temp_c": -3.2},
            {"hour": "+6h", "temp_c": -3.0},
        ],
        "sao_paulo": [
            {"hour": "+1h", "temp_c": 28.2},
            {"hour": "+2h", "temp_c": 28.5},
            {"hour": "+3h", "temp_c": 28.0},
            {"hour": "+4h", "temp_c": 27.5},
            {"hour": "+5h", "temp_c": 27.8},
            {"hour": "+6h", "temp_c": 28.0},
        ],
        "cape_town": [
            {"hour": "+1h", "temp_c": 20.2},
            {"hour": "+2h", "temp_c": 20.5},
            {"hour": "+3h", "temp_c": 21.0},
            {"hour": "+4h", "temp_c": 21.3},
            {"hour": "+5h", "temp_c": 20.8},
            {"hour": "+6h", "temp_c": 20.4},
        ],
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    data = _HOURLY.get(key)
    if data is None:
        return {"error": f"No hourly data for: {city}"}
    return {"city": CITIES[key]["name"], "hourly": data}


@mcp.tool()
def get_weather_alert(city: str) -> dict[str, Any]:
    """Get any active meteorological alerts or warnings for a city.

    Args:
        city: City key or display name (e.g. 'london', 'São Paulo').
    """
    _ALERTS: dict[str, list[dict[str, str]]] = {
        "tokyo": [],
        "new_york": [],
        "london": [
            {
                "type": "Wind Advisory",
                "severity": "Moderate",
                "message": "Sustained SW winds 20–25 kph; gusts to 35 kph through midnight.",
            }
        ],
        "san_francisco": [
            {
                "type": "Dense Fog Advisory",
                "severity": "Low",
                "message": "Visibility below 400 m near the Bay until 10:00 local time.",
            }
        ],
        "paris": [
            {
                "type": "Rain Warning",
                "severity": "Moderate",
                "message": "20–30 mm of rain expected over the next 12 hours.",
            }
        ],
        "sydney": [],
        "dubai": [
            {
                "type": "Heat Advisory",
                "severity": "High",
                "message": (
                    "Temperatures exceeding 38 °C; limit outdoor activity and stay hydrated."
                ),
            }
        ],
        "moscow": [
            {
                "type": "Winter Storm Watch",
                "severity": "High",
                "message": "Heavy snowfall (10–15 cm) and blowing snow expected tonight.",
            }
        ],
        "sao_paulo": [
            {
                "type": "Thunderstorm Warning",
                "severity": "High",
                "message": (
                    "Severe thunderstorms with lightning and 50 mm of rain possible this afternoon."
                ),
            }
        ],
        "cape_town": [],
    }
    key = city.lower().replace(" ", "_")
    for k, val in CITIES.items():
        if val["name"].lower() == city.lower():
            key = k
            break
    alerts = _ALERTS.get(key)
    if alerts is None:
        return {"error": f"Unknown city: {city}"}
    return {"city": CITIES[key]["name"], "alerts": alerts, "count": len(alerts)}


# -- Entry point ----------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="meteo-static: mock weather MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport to use (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP port (default: 8000)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.transport == "http":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

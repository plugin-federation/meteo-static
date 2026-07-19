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

# Provides a function to get the day-ahead weather forecast

import requests
from datetime import datetime
from typing import TypedDict, cast


class DailyForecast(TypedDict):
    """
    The "daily" section of an open-meteo forecast response.
    Each list has one entry per day requested.
    """
    time: list[str]                             # "2026-01-01"
    temperature_2m_max: list[float]             # °C
    temperature_2m_min: list[float]             # °C
    apparent_temperature_max: list[float]       # °C
    apparent_temperature_min: list[float]       # °C
    sunrise: list[str]                          # "2026-01-01T08:00", local time
    sunset: list[str]                           # "2026-01-01T17:52", local time
    daylight_duration: list[float]              # seconds
    precipitation_hours: list[float]            # hours
    precipitation_probability_max: list[int]    # %
    precipitation_sum: list[float]              # mm
    wind_speed_10m_max: list[float]             # km/h
    wind_gusts_10m_max: list[float]             # km/h


class ForecastResponse(TypedDict):
    """
    The parts of an open-meteo forecast response that are used here
    """
    daily: DailyForecast


def fetch_weather_data(lat_long: tuple[float, float]) -> ForecastResponse:
    """
    Fetches a set list of weather forecast data for today from open-meteo.com

    lat_long: The location to give weather data for
    """

    url = "https://api.open-meteo.com/v1/forecast"
    today_str = datetime.now().strftime("%Y-%m-%d")

    request_payload: dict[str, str | float] = {
        "latitude": lat_long[0],
        "longitude": lat_long[1],
        "start_date": today_str,
        "end_date": today_str,
        "daily": "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min," \
        "sunrise,sunset,daylight_duration," \
        "precipitation_hours,precipitation_probability_max,precipitation_sum," \
        "wind_speed_10m_max,wind_gusts_10m_max",
        "timezone":"auto"
    }

    response = requests.get(url, params=request_payload)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object, got {type(data).__name__}")

    return cast(ForecastResponse, data)

def format_weather_data(data: ForecastResponse) -> str:

    daily = data["daily"]

    temperature_2m_max = round(daily["temperature_2m_max"][0])
    temperature_2m_min = round(daily["temperature_2m_min"][0])
    apparent_temperature_max = round(daily["apparent_temperature_max"][0])
    apparent_temperature_min = round(daily["apparent_temperature_min"][0])

    sunrise = datetime.strptime(daily["sunrise"][0], "%Y-%m-%dT%H:%M").strftime("%H:%M")
    sunset = datetime.strptime(daily["sunset"][0], "%Y-%m-%dT%H:%M").strftime("%H:%M")
    daylight_duration_seconds =  round(daily["daylight_duration"][0])
    daylight_duration = f"{daylight_duration_seconds//3600}h{(daylight_duration_seconds%3600)//60}m"

    precipitation_hours = round(daily["precipitation_hours"][0])
    precipitation_probability_max = round(daily["precipitation_probability_max"][0])
    precipitation_sum = round(daily["precipitation_sum"][0])

    wind_speed_10m_max = round(daily["wind_speed_10m_max"][0])
    wind_gusts_10m_max = round(daily["wind_gusts_10m_max"][0])

    data_string = f"Temp: {temperature_2m_min} °C - {temperature_2m_max} °C"
    data_string += f"\nFeels Like: {apparent_temperature_min} °C - {apparent_temperature_max} °C"
    data_string += f"\nDaylight: {sunrise} - {sunset} ({daylight_duration})"
    data_string += f"\nPrecipitation: {precipitation_probability_max} %, {precipitation_hours} h, {precipitation_sum} mm"
    data_string += f"\nWind: {wind_speed_10m_max} km/h ({wind_gusts_10m_max} km/h gusts)"

    return data_string


def get_day_forecast(lat_long: tuple[float, float]) -> tuple[str, str]:

    data = fetch_weather_data(lat_long)
    return (format_weather_data(data), "body")


if __name__ == "__main__":
    
    from config import LAT_LONG

    forecast = get_day_forecast(LAT_LONG)

    print("\n\n")
    print(forecast[0])
    print("\n\n")

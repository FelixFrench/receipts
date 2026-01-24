# Provides a function to get the day-ahead weather forecast

import requests
from datetime import datetime

def fetch_weather_data(lat_long: tuple[float, float]) -> dict:
    """
    Fetches a set list of weather forecast data for today from open-meteo.com

    lat_long: The location to give weather data for
    """

    url = "https://api.open-meteo.com/v1/forecast"
    today_str = datetime.now().strftime("%Y-%m-%d")

    request_payload = {
        "latitude": lat_long[0],
        "longitude": lat_long[1],
        "start_date": today_str,
        "end_date": today_str,
        "daily": "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min," \
        "sunrise,sunset,daylight_duration," \
        "precipitation_hours,precipitation_probability_max,precipitation_sum," \
        "wind_speed_10m_max,wind_gusts_10m_max",
        "timezone":"GMT"
    }

    response = requests.get(url,params=request_payload)
    response.raise_for_status()
    return response.json()

def format_weather_data(data: dict) -> str:

    daily = data.get("daily")

    temperature_2m_max = int(daily["temperature_2m_max"][0])
    temperature_2m_min = int(daily["temperature_2m_min"][0])
    apparent_temperature_max = int(daily["apparent_temperature_max"][0])
    apparent_temperature_min = int(daily["apparent_temperature_min"][0])

    sunrise = datetime.strptime(daily["sunrise"][0], "%Y-%m-%dT%H:%M").strftime("%H:%M")
    sunset = datetime.strptime(daily["sunset"][0], "%Y-%m-%dT%H:%M").strftime("%H:%M")
    daylight_duration_seconds =  int(daily["daylight_duration"][0])
    daylight_duration = f"{daylight_duration_seconds//3600}h{(daylight_duration_seconds%3600)//60}m"

    precipitation_hours = int(daily["precipitation_hours"][0])
    precipitation_probability_max = int(daily["precipitation_probability_max"][0])
    precipitation_sum = int(daily["precipitation_sum"][0])

    wind_speed_10m_max = int(daily["wind_speed_10m_max"][0])
    wind_gusts_10m_max = int(daily["wind_gusts_10m_max"][0])

    data_string = f"Temp: {temperature_2m_min} °C - {temperature_2m_max} °C"
    data_string += f"\nFeels Like: {apparent_temperature_min} °C - {apparent_temperature_max} °C"
    data_string += f"\nDaylight: {sunrise} - {sunset} ({daylight_duration})"
    data_string += f"\nPrecipitation: {precipitation_probability_max} %, {precipitation_hours} h, {precipitation_sum} mm"
    data_string += f"\nWind: {wind_speed_10m_max} km/h ({wind_gusts_10m_max} km/h gusts)"

    return data_string


def get_day_forecast(lat_long: tuple[float, float]) -> str:

    data = fetch_weather_data(lat_long)
    return format_weather_data(data)


if __name__ == "__main__":
    from Secrets import lat_long
    forecast = get_day_forecast(lat_long)

    print("\n\n")
    print(forecast)
    print("\n\n")
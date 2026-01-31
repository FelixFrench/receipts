import requests

def reverse_geocode_label(lat_long: tuple[float,float]) -> str:
    """
    Return a human-readable location label for the given latitude/longitude
    using Nominatim reverse geocoding.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat_long[0],
        "lon": lat_long[1],
        "zoom": 12,
        "layer": "address",
        "format": "json"
    }
    headers = {
        "User-Agent": "receipts"
    }

    response = requests.get(url, params=params, headers=headers, timeout=5)
    response.raise_for_status()

    data = response.json()
    return data.get("name", "Unrecognised location")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv("../.env")
    LAT_LONG = tuple(map(float, os.getenv("LAT_LONG").split(",")))

    print(reverse_geocode_label(LAT_LONG))
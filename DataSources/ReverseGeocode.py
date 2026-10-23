import requests

def reverse_geocode_label(lat_long: tuple[float,float]) -> str:
    """
    Return a human-readable location label for the given latitude/longitude
    using Nominatim reverse geocoding.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params: dict[str, str | float] = {
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
    location_name = data.get("name")
    if not isinstance(location_name, str) or not location_name:
        return "Unrecognised location"
    return location_name


if __name__ == "__main__":
    from config import LAT_LONG

    print(reverse_geocode_label(LAT_LONG))
    
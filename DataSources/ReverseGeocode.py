import requests
from blocks import Block, ImageBlock, TextBlock, Style
from typing import assert_never

def reverse_geocode_label(lat_long: tuple[float,float]) -> list[Block]:
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
        return [TextBlock("Unrecognised location", Style.SUBHEADING)]

    return [TextBlock(location_name, Style.SUBHEADING)]


if __name__ == "__main__":
    from config import load_config

    cfg = load_config()

    location_blocks = reverse_geocode_label(cfg.lat_long)

    print("\n\n")
    for block in location_blocks:
        match block:
            case ImageBlock():
                print("<image>")
            case TextBlock():
                print(block.text)
            case _:
                assert_never(block)
    print("\n\n")
    
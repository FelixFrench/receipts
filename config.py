from dotenv import load_dotenv
import os
from pathlib import Path

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing {name} environment variable")
    return value

def parse_lat_long(value: str | None) -> tuple[float, float]:

    if value is None:
        raise ValueError("Missing LAT_LONG environment variable")

    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"LAT_LONG must be 'lat,long', got {value!r}")

    try:
        lat, lon = (float(p) for p in parts)
    except ValueError:
        raise ValueError(f"LAT_LONG must be floats 'lat,long', got {value!r}") from None

    return (lat, lon)

load_dotenv(Path(__file__).parent / ".env")
LAT_LONG = parse_lat_long(os.getenv("LAT_LONG"))
ENERGY_API_KEY = require_env("ENERGY_API_KEY")
ENERGY_PRODUCT = require_env("ENERGY_PRODUCT")
POSTCODE = require_env("POSTCODE")
ENERGY_MPAN = require_env("ENERGY_MPAN")
ENERGY_MSN = require_env("ENERGY_MSN")
NEWS_NATIONAL = require_env("NEWS_NATIONAL")
NEWS_LOCAL = require_env("NEWS_LOCAL")
NEWS_SPORT = require_env("NEWS_SPORT")
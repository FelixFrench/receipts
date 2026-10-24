from dotenv import load_dotenv
import os
from pathlib import Path
from dataclasses import dataclass

ENV_FILE = Path(__file__).parent / ".env"

@dataclass(frozen=True)
class Config:
    lat_long: tuple[float, float]
    energy_api_key: str
    energy_product: str
    postcode: str
    energy_mpan: str
    energy_msn: str
    news_national: str
    news_local: str
    news_sport: str

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

def load_config(env_file: Path = ENV_FILE) -> Config:
    load_dotenv(env_file)
    return Config(
        lat_long = parse_lat_long(os.getenv("LAT_LONG")),
        energy_api_key = require_env("ENERGY_API_KEY"),
        energy_product = require_env("ENERGY_PRODUCT"),
        postcode = require_env("POSTCODE"),
        energy_mpan = require_env("ENERGY_MPAN"),
        energy_msn = require_env("ENERGY_MSN"),
        news_national = require_env("NEWS_NATIONAL"),
        news_local = require_env("NEWS_LOCAL"),
        news_sport = require_env("NEWS_SPORT")
    )
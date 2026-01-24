# Gather data from various sources across the internet to be printed onto a receipt for some breakfast reading

# TODO:
# Add https://api.edinburghfestivalcity.com/ results?
# Carbon intensity API?
# Worldometer? https://worldometer.readthedocs.io/en/latest/

from DataSources.ReverseGeocode import reverse_geocode_label
from DataSources.Weather import get_day_forecast
from DataSources.Energy import get_energy_consumption
from DataSources.Word import get_word_of_the_day
from DataSources.News import get_headlines
from DataSources.Wikipedia import get_wikipedia_info
from DataSources.Burns import get_burns_poem
from DataSources import Secrets
from datetime import datetime
from time import sleep

# Maximum characters per line
width = 34


# ---------- Data Gathering ----------
def safe_call(func, *args, default="Not available", **kwargs):
    """
    Call a function and return a default value if it raises an exception.

    Args:
        func (callable): The function to invoke.
        *args: Positional arguments passed to the function.
        default (Any): Value to return if an exception is raised.
        **kwargs: Keyword arguments passed to the function.

    Returns:
        Any: The function's return value if successful, otherwise `default`.
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        return default
    
print("Location")
location_string = safe_call(reverse_geocode_label, Secrets.lat_long, default="Unrecognised location")
    
print("Weather")
weather = safe_call(get_day_forecast, Secrets.lat_long)

print("Energy")
dual_tariff_energy_data = safe_call(
    get_energy_consumption,
    Secrets.energy_api_key,
    Secrets.energy_product,
    Secrets.postcode,
    Secrets.energy_mpan,
    Secrets.energy_msn,
    width
)

print("Word")
wotd = safe_call(get_word_of_the_day, 34)

print("News")
news_headlines = safe_call(
    get_headlines,
    Secrets.newsapi_org_key,
    "bbc-news",
    width
)

print("Sports")
sport_headlines = safe_call(
    get_headlines,
    Secrets.newsapi_org_key,
    "bbc-sport",
    width
)

print("Wikipedia")
wikipedia_text = safe_call(get_wikipedia_info, width)

print("Poem")
poem = safe_call(get_burns_poem)


# ---------- Helper functions ----------
def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def get_today_string():
    "Monday 1st January 2026"
    today = datetime.now()
    return today.strftime(f"%A {ordinal(today.day)} %B %Y")



# ---------- Printing ----------
output = (" " + get_today_string() + " ").center(width, "=") + "\n"
output += (location_string).center(width) + "\n\n"

output += " WEATHER ".center(width, "=") + "\n"
output += weather
output += "\n\n"

output += " ENERGY CONSUMPTION ".center(width, "=") + "\n"
output += dual_tariff_energy_data
output += "\n\n"

output += " WORD OF THE DAY ".center(width, "=") + "\n"
output += wotd
output += "\n\n"

output += " NEWS ".center(width, "=") + "\n"
output += news_headlines
output += "\n\n"

output += " SPORTS ".center(width, "=") + "\n"
output += sport_headlines
output += "\n\n"

output += " WIKIPEDIA ".center(width, "=") + "\n"
output += wikipedia_text
output += "\n\n"

output += " TODAY'S BURNS POEM ".center(width, "=") + "\n"
output += poem
output += "\n\n"

output_lines = output.splitlines()
print(len(output_lines), "lines\n")

for line in output_lines:
    print(line[:width])
    sleep(0.02)
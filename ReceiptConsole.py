# Gather data from various sources across the internet to be printed onto a receipt for some breakfast reading

# TODO:
# Add https://api.edinburghfestivalcity.com/ results?
# Carbon intensity API?
# Worldometer? https://worldometer.readthedocs.io/en/latest/
# Sort news

from DataSources.ReverseGeocode import reverse_geocode_label
from DataSources.Weather import get_day_forecast
from DataSources.Energy import get_energy_consumption
from DataSources.Word import get_word_of_the_day
from DataSources.News import get_headlines, HEADLINES_UNAVAILABLE
from DataSources.Wikipedia import get_wikipedia_info
from DataSources.Burns import get_burns_poem
from time import sleep
import config
from helpers import get_today_string, safe_call

RECEIPT_WIDTH = 42
MARGIN = 2
width = RECEIPT_WIDTH - 2 * MARGIN


# ---------- Data Gathering ----------
print("Location")
location_string = safe_call(
    reverse_geocode_label,
    config.LAT_LONG,
    default="Unrecognised location"
    )
    
print("Weather")
weather = safe_call(
    get_day_forecast,
    config.LAT_LONG,
    default = ("Not available","")
    )

print("Energy")
dual_tariff_energy_data = safe_call(
    get_energy_consumption,
    config.ENERGY_API_KEY,
    config.ENERGY_PRODUCT,
    config.POSTCODE,
    config.ENERGY_MPAN,
    config.ENERGY_MSN,
    default = ("Not available","")
    )

print("Word")
wotd = safe_call(
    get_word_of_the_day,
    default = [("Not available","")]
    )

print("National news")
_, news_headlines = safe_call(
    get_headlines,
    config.NEWS_NATIONAL,
    default=HEADLINES_UNAVAILABLE
    )

print("Local news")
_, news_headlines = safe_call(
    get_headlines,
    config.NEWS_LOCAL,
    default=HEADLINES_UNAVAILABLE
    )

print("Sports")
_, sport_headlines = safe_call(
    get_headlines,
    config.NEWS_SPORT,
    default=HEADLINES_UNAVAILABLE
    )

print("Wikipedia")
wikipedia_text = safe_call(
    get_wikipedia_info,
    default = [("Not available","")]
    )

print("Poem")
poem = safe_call(
    get_burns_poem,
    default = [("Not available","")]
    )


# ---------- Helper functions ----------
def strip_block_formatting(block: tuple[str, str]) -> str:
    return block[0]

def strip_blocks_formatting(blocks: list[tuple[str, str]]) -> str:
    return "\n".join([strip_block_formatting(block) for block in blocks])

# ---------- Printing ----------
output = (" " + get_today_string() + " ").center(width, "=") + "\n"
output += (location_string).center(width) + "\n\n"

output += " WEATHER ".center(width, "=") + "\n"
output += strip_block_formatting(weather)
output += "\n\n"

output += " ENERGY CONSUMPTION ".center(width, "=") + "\n"
output += strip_block_formatting(dual_tariff_energy_data)
output += "\n\n"

output += " WORD OF THE DAY ".center(width, "=") + "\n"
output += strip_blocks_formatting(wotd)
output += "\n\n"

output += " NEWS ".center(width, "=") + "\n"
output += strip_blocks_formatting(news_headlines)
output += "\n\n"

output += " SPORTS ".center(width, "=") + "\n"
output += strip_blocks_formatting(sport_headlines)
output += "\n\n"

output += " WIKIPEDIA ".center(width, "=") + "\n"
output += strip_blocks_formatting(wikipedia_text)
output += "\n\n"

output += " TODAY'S BURNS POEM ".center(width, "=") + "\n"
output += strip_blocks_formatting(poem)
output += "\n\n"

output_lines = output.splitlines()
for line in output_lines:
    print(line[:width])
    sleep(0.02)

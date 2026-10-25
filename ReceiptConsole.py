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
from DataSources.News import get_headlines
from DataSources.Wikipedia import get_wikipedia_info
from DataSources.Burns import get_burns_poem
from time import sleep
from config import load_config
from helpers import get_today_string, safe_call
from blocks import Block, TextBlock, ImageBlock
from typing import assert_never

RECEIPT_WIDTH = 42
MARGIN = 2
WIDTH = RECEIPT_WIDTH - 2 * MARGIN


def strip_blocks_formatting(blocks: list[Block]) -> str:
    
    stripped_blocks:list[str] = []
    for block in blocks:
        match block:
            case TextBlock():
                stripped_blocks.append(block.text)
            case ImageBlock():
                stripped_blocks.append("<image>")
            case _:
                assert_never(block)

    return "\n".join(stripped_blocks)


def main() -> None:

    cfg = load_config()

    today_blocks = [TextBlock(get_today_string())]

    print("Location")
    location_blocks = safe_call(reverse_geocode_label, cfg.lat_long)

    print("Weather")
    weather_blocks = safe_call(get_day_forecast, cfg.lat_long)

    print("Energy")
    energy_blocks = safe_call(
        get_energy_consumption,
        cfg.energy_api_key, cfg.energy_product, cfg.postcode,
        cfg.energy_mpan, cfg.energy_msn
        )

    print("Word")
    wotd_blocks = safe_call(get_word_of_the_day)

    print("National news")
    national_news_blocks = safe_call(get_headlines, cfg.news_national)

    print("Local news")
    local_news_blocks = safe_call(get_headlines, cfg.news_local)

    print("Sport")
    sport_blocks = safe_call(get_headlines, cfg.news_sport)

    print("Wikipedia")
    wikipedia_blocks = safe_call(get_wikipedia_info)

    print("Poem")
    poem_blocks = safe_call(get_burns_poem)


    # ---------- Printing ----------
    output = (" " + get_today_string() + " ").center(WIDTH, "=") + "\n"
    output += (strip_blocks_formatting(location_blocks)).center(WIDTH) + "\n\n"

    output += " WEATHER ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(weather_blocks)
    output += "\n\n"

    output += " ENERGY CONSUMPTION ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(energy_blocks)
    output += "\n\n"

    output += " WORD OF THE DAY ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(wotd_blocks)
    output += "\n\n"

    output += " NATIONAL NEWS ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(national_news_blocks)
    output += "\n\n"

    output += " LOCAL NEWS ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(local_news_blocks)
    output += "\n\n"

    output += " SPORT ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(sport_blocks)
    output += "\n\n"

    output += " WIKIPEDIA ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(wikipedia_blocks)
    output += "\n\n"

    output += " TODAY'S BURNS POEM ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(poem_blocks)
    output += "\n\n"

    output_lines = output.splitlines()
    for line in output_lines:
        print(line[:WIDTH])
        sleep(0.02)

if __name__ == "__main__":
    main()

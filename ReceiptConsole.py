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
from DataSources.News import get_headlines, Headlines, HEADLINES_UNAVAILABLE
from DataSources.Wikipedia import get_wikipedia_info
from DataSources.Burns import get_burns_poem
from time import sleep
from config import load_config
from helpers import get_today_string, safe_call
from blocks import Block

RECEIPT_WIDTH = 42
MARGIN = 2
WIDTH = RECEIPT_WIDTH - 2 * MARGIN


def strip_blocks_formatting(blocks: list[Block]) -> str:
    return "\n".join([block.text for block in blocks])


def main() -> None:

    cfg = load_config()

    print("Location")
    location_string = safe_call(
        reverse_geocode_label,
        cfg.lat_long,
        default="Unrecognised location"
        )

    print("Weather")
    weather = safe_call(
        get_day_forecast,
        cfg.lat_long,
        default = Block("Not available")
        )

    print("Energy")
    dual_tariff_energy_data = safe_call(
        get_energy_consumption,
        cfg.energy_api_key,
        cfg.energy_product,
        cfg.postcode,
        cfg.energy_mpan,
        cfg.energy_msn,
        default = Block("Not available")
        )

    print("Word")
    wotd = safe_call(
        get_word_of_the_day,
        default = [Block("Not available")]
        )

    print("National news")
    national_news_headlines = safe_call(
        get_headlines,
        cfg.news_national,
        default=HEADLINES_UNAVAILABLE
        )

    print("Local news")
    local_news_headlines = safe_call(
        get_headlines,
        cfg.news_local,
        default=HEADLINES_UNAVAILABLE
        )

    print("Sport")
    sport_headlines = safe_call(
        get_headlines,
        cfg.news_sport,
        default=HEADLINES_UNAVAILABLE
        )

    print("Wikipedia")
    wikipedia_text = safe_call(
        get_wikipedia_info,
        default = [Block("Not available")]
        )

    print("Poem")
    poem = safe_call(
        get_burns_poem,
        default = [Block("Not available")]
        )


    # ---------- Printing ----------
    output = (" " + get_today_string() + " ").center(WIDTH, "=") + "\n"
    output += (location_string).center(WIDTH) + "\n\n"

    output += " WEATHER ".center(WIDTH, "=") + "\n"
    output += weather.text
    output += "\n\n"

    output += " ENERGY CONSUMPTION ".center(WIDTH, "=") + "\n"
    output += dual_tariff_energy_data.text
    output += "\n\n"

    output += " WORD OF THE DAY ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(wotd)
    output += "\n\n"

    output += " NATIONAL NEWS ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(national_news_headlines.blocks)
    output += "\n\n"

    output += " LOCAL NEWS ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(local_news_headlines.blocks)
    output += "\n\n"

    output += " SPORT ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(sport_headlines.blocks)
    output += "\n\n"

    output += " WIKIPEDIA ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(wikipedia_text)
    output += "\n\n"

    output += " TODAY'S BURNS POEM ".center(WIDTH, "=") + "\n"
    output += strip_blocks_formatting(poem)
    output += "\n\n"

    output_lines = output.splitlines()
    for line in output_lines:
        print(line[:WIDTH])
        sleep(0.02)

if __name__ == "__main__":
    main()

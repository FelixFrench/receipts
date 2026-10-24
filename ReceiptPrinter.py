# Gather data from various sources across the internet to be printed onto a receipt for some breakfast reading

# TODO:
# Add https://api.edinburghfestivalcity.com/ results?
# Carbon intensity API?
# Worldometer? https://worldometer.readthedocs.io/en/latest/
# Use RSS feeds for news, and other things too?
# Get lat,long from postcode
# Choose local news feed from postcode

from DataSources.ReverseGeocode import reverse_geocode_label
from DataSources.Weather import get_day_forecast
from DataSources.Energy import get_energy_consumption
from DataSources.Word import get_word_of_the_day
from DataSources.News import get_headlines, Headlines, HEADLINES_UNAVAILABLE
from DataSources.Wikipedia import get_wikipedia_info
from DataSources.Burns import get_burns_poem
import textwrap
from escpos.escpos import Escpos
from escpos.printer import Network
from config import load_config
from helpers import get_today_string, safe_call
from blocks import Block, Style
from typing import assert_never

PRINTER_IP = "192.168.1.165"
PRINTER_TYPE = "TM-T88IV"
FONT = "a"
MARGIN = 2


def print_line(printer: Escpos, text: str, style: Style = Style.BODY, margin: int = MARGIN) -> None:

    textlines = text.split("\n")

    match style:
        case Style.HEADING:
            printer.set(bold=True, align="center")

        case Style.SUBHEADING:
            printer.set(bold=False, align="center")

        case Style.RIGHT_ALIGN:
            printer.set(bold=False, align="right")
            textlines = [line + (" " * margin) for line in textlines]

        case Style.BODY:
            printer.set(bold=False, align="left")
            textlines = [(" " * margin) + line for line in textlines]

        case _:
            assert_never(style)

    for line in textlines:
        printer.text(line)
        printer.ln()


def print_block(printer: Escpos, block: Block, margin: int = MARGIN) -> None:
    lines = block.text.split("\n")
    columns = printer.profile.get_columns(font=FONT)
    for line in lines:
        wrapped_lines = textwrap.wrap(line, columns - 2 * margin)
        for wrapped_line in wrapped_lines:
            print_line(printer, wrapped_line, block.style, margin)


def print_blocks(printer: Escpos, blocks: list[Block], margin: int = MARGIN) -> None:
    for block in blocks:
        print_block(printer, block, margin)


def print_headlines(printer: Escpos, heading: str, headlines: Headlines) -> None:
    """print a heading, a thumbnail if there is one, then the headline blocks"""
    print_line(printer, heading, Style.HEADING)
    printer.set(align="center")
    if headlines.image:
        printer.image(headlines.image)
    print_blocks(printer, headlines.blocks)
    printer.ln(2)


def main() -> None:

    cfg = load_config()

    # Try to connect and set the font - will raise if printer offline, avoiding API calls
    printer = Network(PRINTER_IP, profile=PRINTER_TYPE)
    printer.set(font=FONT)

    location_string = safe_call(
        reverse_geocode_label,
        cfg.lat_long,
        default="Unrecognised location"
        )

    weather_block = safe_call(
        get_day_forecast,
        cfg.lat_long,
        default=Block("Not available")
        )

    energy_block = safe_call(
        get_energy_consumption,
        cfg.energy_api_key, cfg.energy_product, cfg.postcode,
        cfg.energy_mpan, cfg.energy_msn,
        default=Block("Not available")
        )

    wotd_blocks = safe_call(
        get_word_of_the_day,
        default=[Block("Not available")]
        )

    national_news_headlines = safe_call(
        get_headlines, cfg.news_national,
        default=HEADLINES_UNAVAILABLE
        )

    local_news_headlines = safe_call(
        get_headlines, cfg.news_local,
        default=HEADLINES_UNAVAILABLE
        )

    sport_headlines = safe_call(
        get_headlines, cfg.news_sport,
        default=HEADLINES_UNAVAILABLE
        )

    wikipedia_blocks = safe_call(
        get_wikipedia_info,
        default=[Block("Not available")]
        )

    poem = safe_call(
        get_burns_poem,
        default = [Block("Not available")]
        )

    # Date
    print_line(printer, get_today_string(), Style.HEADING)

    # Location
    print_line(printer, location_string, Style.SUBHEADING)
    printer.ln(2)

    # Weather
    print_line(printer, "WEATHER", Style.HEADING)
    print_block(printer, weather_block)
    printer.ln(2)

    # Energy
    print_line(printer, "ENERGY CONSUMPTION", Style.HEADING)
    print_block(printer, energy_block)
    printer.ln(2)

    # Word
    print_line(printer, "WORD OF THE DAY", Style.HEADING)
    print_blocks(printer, wotd_blocks)
    printer.ln(2)

    # Print news and sport
    print_headlines(printer, "NATIONAL NEWS", national_news_headlines)
    print_headlines(printer, "LOCAL NEWS", local_news_headlines)
    print_headlines(printer, "SPORT", sport_headlines)

    # Wikipedia
    print_line(printer, "WIKIPEDIA", Style.HEADING)
    print_blocks(printer, wikipedia_blocks)
    printer.ln(2)

    # Poem
    print_line(printer, "TODAY'S BURNS POEM", Style.HEADING)
    print_blocks(printer, poem)
    printer.ln(2)

    # Finalise
    printer.cut()


if __name__ == "__main__":
    main()

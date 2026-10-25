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
from DataSources.News import get_headlines
from DataSources.Wikipedia import get_wikipedia_info
from DataSources.Burns import get_burns_poem
import textwrap
from escpos.escpos import Escpos
from escpos.printer import Network
from config import load_config
from helpers import get_today_string, safe_call
from blocks import Block, TextBlock, ImageBlock, Style
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
    match block:
            case TextBlock():
                lines = block.text.split("\n")
                columns = printer.profile.get_columns(font=FONT)
                for line in lines:
                    wrapped_lines = textwrap.wrap(line, columns - 2 * margin)
                    for wrapped_line in wrapped_lines:
                        print_line(printer, wrapped_line, block.style, margin)

            case ImageBlock():
                printer.set(align="center")
                printer.image(block.image)

            case _:
                assert_never(block)


def print_blocks(printer: Escpos, blocks: list[Block], margin: int = MARGIN) -> None:
    for block in blocks:
        print_block(printer, block, margin)


def main() -> None:

    cfg = load_config()

    # Try to connect and set the font - will raise if printer offline, avoiding API calls
    printer = Network(PRINTER_IP, profile=PRINTER_TYPE)
    printer.set(font=FONT)

    today_blocks: list[Block] = [TextBlock(get_today_string())]

    location_blocks = safe_call(reverse_geocode_label, cfg.lat_long)

    weather_blocks = safe_call(get_day_forecast,cfg.lat_long)

    energy_blocks = safe_call(
        get_energy_consumption,
        cfg.energy_api_key, cfg.energy_product, cfg.postcode,
        cfg.energy_mpan, cfg.energy_msn
        )

    wotd_blocks = safe_call(get_word_of_the_day)

    national_news_blocks = safe_call(get_headlines, cfg.news_national)

    local_news_blocks = safe_call(get_headlines, cfg.news_local)

    sport_blocks = safe_call(get_headlines, cfg.news_sport)

    wikipedia_blocks = safe_call(get_wikipedia_info)

    poem = safe_call(get_burns_poem)

    # Date
    print_blocks(printer, today_blocks)

    # Location
    print_blocks(printer, location_blocks)
    printer.ln(2)

    # Weather
    print_line(printer, "WEATHER", Style.HEADING)
    print_blocks(printer, weather_blocks)
    printer.ln(2)

    # Energy
    print_line(printer, "ENERGY CONSUMPTION", Style.HEADING)
    print_blocks(printer, energy_blocks)
    printer.ln(2)

    # Word
    print_line(printer, "WORD OF THE DAY", Style.HEADING)
    print_blocks(printer, wotd_blocks)
    printer.ln(2)

    # Print news and sport
    print_line(printer, "NATIONAL NEWS", Style.HEADING)
    print_blocks(printer, national_news_blocks)
    printer.ln(2)
    print_line(printer, "LOCAL NEWS", Style.HEADING)
    print_blocks(printer, local_news_blocks)
    printer.ln(2)
    print_line(printer, "SPORT", Style.HEADING)
    print_blocks(printer, sport_blocks)
    printer.ln(2)

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

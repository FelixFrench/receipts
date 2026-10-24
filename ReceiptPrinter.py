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
from escpos.printer import Network
import config
from helpers import get_today_string, safe_call
from blocks import Block, Style
from typing import assert_never

PRINTER_IP = "192.168.1.165"
PRINTER_TYPE = "TM-T88IV"
MARGIN = 2


# ---------- Data Gathering ----------
location_string = safe_call(
    reverse_geocode_label,
    config.LAT_LONG,
    default="Unrecognised location"
    )

weather_block = safe_call(
    get_day_forecast,
    config.LAT_LONG,
    default=Block("Not available")
    )

energy_block = safe_call(
    get_energy_consumption,
    config.ENERGY_API_KEY, config.ENERGY_PRODUCT, config.POSTCODE,
    config.ENERGY_MPAN, config.ENERGY_MSN,
    default=Block("Not available")
    )

wotd_blocks = safe_call(
    get_word_of_the_day,
    default=[Block("Not available")]
    )

national_news_headlines = safe_call(
    get_headlines, config.NEWS_NATIONAL,
    default=HEADLINES_UNAVAILABLE
    )

local_news_headlines = safe_call(
    get_headlines, config.NEWS_LOCAL,
    default=HEADLINES_UNAVAILABLE
    )

sport_headlines = safe_call(
    get_headlines, config.NEWS_SPORT,
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


printer = Network(PRINTER_IP, profile=PRINTER_TYPE)
printer.set(font="a")
columns = printer.profile.get_columns(font="a")
print(columns, "columns")

def print_line(text: str, style: Style = Style.BODY, margin: int = 2) -> None:
    
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

def print_block(block: Block, margin: int = 2) -> None:
    lines = block.text.split("\n")
    for line in lines:
        wrapped_lines = textwrap.wrap(line, columns - 2 * margin)
        for wrapped_line in wrapped_lines:
            print_line(wrapped_line, block.style, margin)

def print_blocks(blocks: list[Block], margin: int = 2) -> None:
    for block in blocks:
        print_block(block, margin)

    
# Date
print_line(get_today_string(), Style.HEADING)

# Location
print_line(location_string, Style.SUBHEADING)
printer.ln(2)
    
# Weather
print_line("WEATHER", Style.HEADING)
print_block(weather_block)
printer.ln(2)

# Energy
print_line("ENERGY CONSUMPTION", Style.HEADING)
print_block(energy_block)
printer.ln(2)

# Word
print_line("WORD OF THE DAY", Style.HEADING)
print_blocks(wotd_blocks)
printer.ln(2)

# News & sport headlines helper function
def print_headlines(heading: str, headlines: Headlines) -> None:

    print_line(heading, Style.HEADING)
    printer.set(align="center")
    if headlines.image:
        printer.image(headlines.image)
    print_blocks(headlines.blocks)
    printer.ln(2)

# Print news and sport
print_headlines("NATIONAL NEWS", national_news_headlines)
print_headlines("LOCAL NEWS", local_news_headlines)
print_headlines("SPORT", sport_headlines)

# Wikipedia
print_line("WIKIPEDIA", Style.HEADING)
print_blocks(wikipedia_blocks)
printer.ln(2)

# Poem
print_line("TODAY'S BURNS POEM", Style.HEADING)
print_blocks(poem)
printer.ln(2)

# Finalise
printer.cut()

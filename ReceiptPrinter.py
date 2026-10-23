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
from DataSources.News import get_headlines, HEADLINES_UNAVAILABLE
from DataSources.Wikipedia import get_wikipedia_info
from DataSources.Burns import get_burns_poem
import textwrap
from escpos.printer import Network
import config
from helpers import get_today_string, safe_call
from PIL import ImageFile

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
    default=("Not available", "body")
    )

energy_block = safe_call(
    get_energy_consumption,
    config.ENERGY_API_KEY, config.ENERGY_PRODUCT, config.POSTCODE,
    config.ENERGY_MPAN, config.ENERGY_MSN,
    default=("Not available", "body")
    )

wotd_blocks = safe_call(
    get_word_of_the_day,
    default=[("Not available", "body")]
    )

national_news_thumb, national_news_blocks = safe_call(
    get_headlines, config.NEWS_NATIONAL,
    default=HEADLINES_UNAVAILABLE
    )

local_news_thumb, local_news_blocks = safe_call(
    get_headlines, config.NEWS_LOCAL,
    default=HEADLINES_UNAVAILABLE
    )

sport_thumb, sport_blocks = safe_call(
    get_headlines, config.NEWS_SPORT,
    default=HEADLINES_UNAVAILABLE
    )

wikipedia_blocks = safe_call(
    get_wikipedia_info,
    default=[("Not available", "body")]
    )

poem = safe_call(
    get_burns_poem,
    default = [("Not available","body")]
    )


printer = Network(PRINTER_IP, profile=PRINTER_TYPE)
printer.set(font="a")
columns = printer.profile.get_columns(font="a")
print(columns, "columns")

def print_line(text: str, style: str | None = None, margin: int = 2) -> None:

    match style:
        case "heading":
            printer.set(bold=True, align="center")
        case "subheading":
            printer.set(bold=False, align="center")
        case "rightAlign":
            printer.set(bold=False, align="right")
        case _: # default to body
            style = "body"
            printer.set(bold=False, align="left")

    textlines = text.split("\n")

    if style=="rightAlign":
        textlines = [line + (" "*margin) for line in textlines]
    elif style == "body":
        textlines = [(" "*margin) + line for line in textlines]
        
    
    for line in textlines:
        printer.text(line)
        printer.ln()

def print_block(block:tuple[str,str], margin: int = 2) -> None:
    lines = block[0].split("\n")
    for line in lines:
        wrapped_lines = textwrap.wrap(line, columns - 2 * margin)
        for wrapped_line in wrapped_lines:
            print_line(wrapped_line, block[1], margin)

def print_blocks(blocks: list[tuple[str,str]], margin: int = 2) -> None:
    for block in blocks:
        print_block(block, margin)

    
# Date
print_line(get_today_string(), "heading")

# Location
print_line(location_string, "subheading")
printer.ln(2)
    
# Weather
print_line("WEATHER", "heading")
print_block(weather_block)
printer.ln(2)

# Energy
print_line("ENERGY CONSUMPTION", "heading")
print_block(energy_block)
printer.ln(2)

# Word
print_line("WORD OF THE DAY", "heading")
print_blocks(wotd_blocks)
printer.ln(2)

# News & sport headlines helper function
def print_headlines(heading:str, image: ImageFile.ImageFile | None, blocks:list[tuple[str,str]]) -> None:

    print_line(heading, "heading")
    printer.set(align="center")
    if image:
        printer.image(image)
    print_blocks(blocks)
    printer.ln(2)

# Print news and sport
print_headlines("NATIONAL NEWS", national_news_thumb, national_news_blocks)
print_headlines("LOCAL NEWS", local_news_thumb, local_news_blocks)
print_headlines("SPORT", sport_thumb, sport_blocks)

# Wikipedia
print_line("WIKIPEDIA", "heading")
print_blocks(wikipedia_blocks)
printer.ln(2)

# Poem
print_line("TODAY'S BURNS POEM", "heading")
print_blocks(poem)
printer.ln(2)

# Finalise
printer.cut()

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
import os, textwrap
from dotenv import load_dotenv
from datetime import datetime
from escpos.printer import Network

PRINTER_IP = "192.168.1.165"
PRINTER_TYPE = "TM-T88IV"
MARGIN = 2

load_dotenv()
LAT_LONG = tuple(map(float, os.getenv("LAT_LONG").split(",")))
ENERGY_API_KEY = os.getenv("ENERGY_API_KEY")
ENERGY_PRODUCT = os.getenv("ENERGY_PRODUCT")
POSTCODE = os.getenv("POSTCODE")
ENERGY_MPAN = os.getenv("ENERGY_MPAN")
ENERGY_MSN = os.getenv("ENERGY_MSN")
NEWSAPI_ORG_KEY = os.getenv("NEWSAPI_ORG_KEY")


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def get_today_string():
    # "Monday 1st January 2026"
    today = datetime.now()
    return today.strftime(f"%A {ordinal(today.day)} %B %Y")

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
    except Exception as e:
        print(e)
        return default

# ---------- Data Gathering ----------
location_string = safe_call(reverse_geocode_label, LAT_LONG, default="Unrecognised location")
weather_block = safe_call(get_day_forecast, LAT_LONG, default=("Not available", "body"))
energy_block = safe_call(get_energy_consumption,
    ENERGY_API_KEY, ENERGY_PRODUCT, POSTCODE,
    ENERGY_MPAN, ENERGY_MSN, default=("Not available", "body")
)
wotd_blocks = safe_call(get_word_of_the_day, default=[("Not available", "body")])
national_news_thumb, national_news_blocks = safe_call(get_headlines, os.getenv("NEWS_NATIONAL"), default=[("Not available", "body")])
local_news_thumb, local_news_blocks = safe_call(get_headlines, os.getenv("NEWS_LOCAL"), default=[("Not available", "body")])
sport_thumb, sport_blocks = safe_call(get_headlines, os.getenv("NEWS_SPORT"), default=[("Not available", "body")])
wikipedia_blocks = safe_call(get_wikipedia_info, default=[("Not available", "body")])
poem = safe_call(get_burns_poem)


printer = Network(PRINTER_IP, profile=PRINTER_TYPE)
printer.set(font="a")
columns = printer.profile.get_columns(font="a")
print(columns, "columns")

def print_line(text: str, style: str = None, margin: int = 2):

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

def print_block(block:tuple[str,str], margin: int = 2):
    lines = block[0].split("\n")
    for line in lines:
        wrapped_lines = textwrap.wrap(line, columns - 2 * margin)
        for wrapped_line in wrapped_lines:
            print_line(wrapped_line, block[1], margin)

def print_blocks(blocks: list[tuple[str,str]], margin: int = 2):
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
def print_headlines(heading:str, image, blocks:list[tuple[str,str]]):

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

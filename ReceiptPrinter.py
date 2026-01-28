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
from DataSources import Secrets
from datetime import datetime
from time import sleep
from escpos.printer import Network
import textwrap

PRINTER_IP = "10.178.77.174"
PRINTER_TYPE = "TM-T88IV"
MARGIN = 2




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
location_string = safe_call(reverse_geocode_label, Secrets.lat_long, default="Unrecognised location")
weather_block = safe_call(get_day_forecast, Secrets.lat_long, default=("Not available", "body"))
energy_block = safe_call(get_energy_consumption,
    Secrets.energy_api_key, Secrets.energy_product, Secrets.postcode,
    Secrets.energy_mpan, Secrets.energy_msn, default=("Not available", "body")
)
wotd_blocks = safe_call(get_word_of_the_day, default=[("Not available", "body")])
news_headlines = safe_call(get_headlines,
    Secrets.newsapi_org_key, "bbc-news", default=[("Not available", "body")]
)
sport_headlines = safe_call(get_headlines,
    Secrets.newsapi_org_key, "bbc-sport", default=[("Not available", "body")]
)
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

# News
print_line("NEWS", "heading")
print_blocks(news_headlines)
printer.ln(2)

# Sport
print_line("SPORT", "heading")
print_blocks(sport_headlines)
printer.ln(2)

# Wikipedia
print_line("WIKIPEDIA", "heading")
print_blocks(wikipedia_blocks)
printer.ln(2)

# Poem
print_line("TODAY'S BURNS POEM", "heading")
print_block((poem, "body"))
printer.ln(2)

# Finalise
printer.cut()

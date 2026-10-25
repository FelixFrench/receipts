from config import Config
from blocks import Block, Section, TextBlock, Style
from collections.abc import Callable
from typing import Any

from datetime import datetime
from DataSources.ReverseGeocode import reverse_geocode_label
from DataSources.Weather import get_day_forecast
from DataSources.Energy import get_energy_consumption
from DataSources.Word import get_word_of_the_day
from DataSources.News import get_headlines
from DataSources.Wikipedia import get_wikipedia_info
from DataSources.Burns import get_burns_poem

def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def get_today_string() -> str:
    # Returns date string like "Monday 1st January 2026"
    today = datetime.now()
    return today.strftime(f"%A {ordinal(today.day)} %B %Y")

def safe_call(func: Callable[..., list[Block]], *args: Any, default: list[Block] = [TextBlock("Not available")], **kwargs: Any) -> list[Block]:
    """
    Call a function and return a default value if it raises an exception.

    Args:
        func: The function to invoke.
        *args: Positional arguments passed to the function.
        **kwargs: Keyword arguments passed to the function.

    Returns:
        list[Block]: The function's return value if successful,
                     otherwise default.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(e)
        return default

def gather_sections(cfg: Config, verbose: bool = False) -> list[Section]:

    sections: list[Section] = []
    
    # Header (Date and location)
    if verbose: print("Date")
    header_section: Section = [TextBlock(get_today_string(), Style.HEADING)]
    
    if verbose: print("Location")
    header_section.extend(safe_call(
        reverse_geocode_label, cfg.lat_long,
        default=[TextBlock("Not available", Style.SUBHEADING)]
        ))
    sections.append(header_section)

    # Other data sources
    if verbose: print("Weather")
    sections.append([TextBlock("WEATHER", Style.HEADING), *safe_call(get_day_forecast, cfg.lat_long)])
    
    if verbose: print("Energy")
    sections.append([TextBlock("ENERGY CONSUMPTION", Style.HEADING), *safe_call(
        get_energy_consumption, cfg.energy_api_key, cfg.energy_product,
        cfg.postcode, cfg.energy_mpan, cfg.energy_msn
        )]) 
    
    if verbose: print("Word")
    sections.append([TextBlock("WORD OF THE DAY", Style.HEADING), *safe_call(get_word_of_the_day)])
    
    if verbose: print("National news")
    sections.append([TextBlock("NATIONAL NEWS", Style.HEADING), *safe_call(get_headlines, cfg.news_national)])
    
    if verbose: print("Local news")
    sections.append([TextBlock("LOCAL NEWS", Style.HEADING), *safe_call(get_headlines, cfg.news_local)])
    
    if verbose: print("Sport")
    sections.append([TextBlock("SPORT", Style.HEADING), *safe_call(get_headlines, cfg.news_sport)])
    
    if verbose: print("Wikipedia")
    sections.append([TextBlock("WIKIPEDIA", Style.HEADING), *safe_call(get_wikipedia_info)])
    
    if verbose: print("Poem")
    sections.append([TextBlock("TODAY'S BURNS POEM", Style.HEADING), *safe_call(get_burns_poem)])

    return sections

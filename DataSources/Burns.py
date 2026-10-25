# Provides a function to get a Robert Burns poem which changes each day

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from blocks import Block, ImageBlock, TextBlock, Style
from dataclasses import dataclass
from typing import assert_never

# Base site URL
BASE_URL = "https://robertburns.org"

# JSON endpoint containing the list of works
JSON_URL = f"{BASE_URL}/static/json/works_app/works_list.json"

@dataclass(frozen=True)
class PoemID:
    title: str
    slug: str


def choose_poem()-> PoemID:
    """
    Selects a poem from robertburns.org
    The chosen poem changes once per day
    
    Returns a tuple of (title, slug), where slug can be used in a url
     to get the full text
    """
    response = requests.get(JSON_URL, timeout=10)
    response.raise_for_status()

    works = response.json()
    titles = [PoemID(work["title"], work["slug"]) for work in works]

    # Rotate through one poem per day
    today = datetime.now(timezone.utc).date()
    epoch = datetime(2026, 5, 20, tzinfo=timezone.utc).date()
    days_since_epoch = (today - epoch).days
    index = days_since_epoch % len(titles)

    return titles[index]


def scrape_poem(slug: str) -> str:
    """
    Given a poem slug, fetch the poem HTML page and extract
    plain text with blank lines separating stanzas.

    param slug: The poem identifier from choose_poem()
    Returns a multiline string
    """

    # Build the poem URL from the slug
    url = f"{BASE_URL}/works/{slug}.html"
    response = requests.get(url)
    response.raise_for_status()

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the main poem container
    work_lines = soup.find("section", class_="work-lines")

    # If the expected structure is missing, return empty text
    if not work_lines:
        return ""

    poem_stanzas = []

    # Iterate over each stanza
    for stanza in work_lines.find_all("div", class_="stanza"):
        stanza_lines = []

        # Iterate over each line in the stanza
        for line in stanza.find_all("div", class_="work-line"):
            text_span = line.find("span", class_="work-line-text")

            # Extract the actual line text
            if text_span:
                stanza_lines.append(text_span.get_text(strip=True))

        # Join lines within a stanza with single newlines
        poem_stanzas.append("\n".join(stanza_lines))

    # Join stanzas with blank lines
    return "\n".join(poem_stanzas)


def get_burns_poem() -> list[Block]:
    """
    Gets today's burns poem by scraping a website
    
    param width: The maximum line length in chars
    Returns a list of blocks
    """
    
    blocks: list[Block] = []

    poem_id = choose_poem()
    blocks.append(TextBlock(poem_id.title, Style.SUBHEADING))
    
    poem_text = scrape_poem(poem_id.slug)
    blocks.append(TextBlock(poem_text, Style.POETRY))

    return blocks


if __name__ == "__main__":

    poem_blocks = get_burns_poem()
    
    print("\n\n")
    for block in poem_blocks:
        match block:
            case ImageBlock():
                print("<image>")
            case TextBlock():
                print(block.text)
            case _:
                assert_never(block)
    print("\n\n")

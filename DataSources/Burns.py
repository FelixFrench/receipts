# Provides a function to get a Robert Burns poem which changes each day

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import textwrap

# Base site URL
BASE_URL = "https://robertburns.org"

# JSON endpoint containing the list of works
JSON_URL = f"{BASE_URL}/static/json/works_app/works_list.json"


def choose_poem()-> tuple[str, str]:
    """
    Selects a poem from robertburns.org
    The chosen poem changes once per day
    
    Returns a tuple of (title, slug), where slug can be used in a url
     to get the full text
    """
    response = requests.get(JSON_URL)
    response.raise_for_status()

    works = response.json()
    titles = [(work["title"], work["slug"]) for work in works]

    # Rotate through one poem per day
    today = datetime.now(timezone.utc).date()
    epoch = datetime(2026, 1, 23, tzinfo=timezone.utc).date()
    days_since_epoch = (today - epoch).days
    index = days_since_epoch % len(titles)

    return titles[index]


def scrape_poem(slug) -> str:
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


def get_burns_poem(width = 34):
    """
    Gets today's burns poem by scraping a website
    
    param width: The maximum line length in chars
    Returns a multiline string
    """
    
    (title, slug) = choose_poem()
    blocks = [(title, "subheading")]
    poem_text = scrape_poem(slug)

    wrapped_lines = []

    for line in poem_text.splitlines():
        # Preserve blank lines (stanza breaks)
        if not line.strip():
            wrapped_lines.append("")
            continue

        wrapped = textwrap.wrap(
            line,
            width=width,
            subsequent_indent="  ",
            break_long_words=False,
            break_on_hyphens=False,
        )

        wrapped_lines.extend(wrapped)

    blocks.extend([(line, "body") for line in wrapped_lines])
    return blocks#title.center(width) + "\n\n" + "\n".join(wrapped_lines)


if __name__ == "__main__":

    poem = get_burns_poem()
    
    print("\n\n")
    for block in poem:
        print(block[0])
    print("\n\n")
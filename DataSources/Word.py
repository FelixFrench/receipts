# Provides a function to get the word of the day with definition

import requests
from xml.etree import ElementTree

def get_word_of_the_day() -> list[tuple[str,str]]:

    rss_url = "https://wordsmith.org/awad/rss1.xml"
    response = requests.get(rss_url, timeout=10)

    response.raise_for_status()

    rss_feed = response.text

    root = ElementTree.fromstring(rss_feed)

    title_text = root.findtext("channel/item/title")
    if title_text is None:
        raise Exception("No title found in the item")

    description_text = root.findtext("channel/item/description")
    if description_text is None:
        raise Exception("No description found in the item")

    return [(title_text, "body"), (description_text, "body")]

if __name__ == "__main__":
    wotd = get_word_of_the_day()

    print("\n\n")
    for block in wotd:
        print(block[0])
    print("\n\n")

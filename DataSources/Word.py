# Provides a function to get the word of the day with definition

import requests
from xml.etree import ElementTree
import textwrap

def get_word_of_the_day(width):

    rss_url = "https://wordsmith.org/awad/rss1.xml"
    response = requests.get(rss_url)

    if response.status_code != 200:
        print("Failed to get RSS feed. Status code:", response.status_code)
        return ""

    rss_feed = response.text

    # parse the RSS feed using xml.etree.ElementTree
    root = ElementTree.fromstring(rss_feed)
    channel = root.find("channel")
    if channel is None:
        print("No channel found in the RSS feed")
        return ""

    item = channel.find("item")
    if item is None:
        print("No item found in the first entry")
        return ""

    title = item.find("title")
    if title is None:
        print("No title found in the item")
        return ""
        
    description = item.find("description")
    if item is None:
        print("No desc found in the item")
        return f"{title.text}"

    return f"{title.text}:\n{textwrap.fill(description.text, width=width)}"

if __name__ == "__main__":
    wotd = get_word_of_the_day(34)

    print("\n\n")
    print(wotd)
    print("\n\n")
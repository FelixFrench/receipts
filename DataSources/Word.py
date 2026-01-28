# Provides a function to get the word of the day with definition

import requests
from xml.etree import ElementTree

def get_word_of_the_day() -> list[tuple[str,str]]:

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

    return [(title.text, "body"), (description.text, "body")]

if __name__ == "__main__":
    wotd = get_word_of_the_day()

    print("\n\n")
    print(wotd)
    print("\n\n")
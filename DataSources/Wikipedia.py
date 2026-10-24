# Provides a function to get today's featured article and the top 5 most read articles

import requests
from datetime import datetime
from blocks import Block, Style

def get_wikipedia_info() -> list[Block]:
    today = datetime.now()

    url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/featured/{today.year}/{today.month:02d}/{today.day:02d}"

    headers = {
        "user-agent": "bot to access wikipedia featured articles once per day"
    }
    (r := requests.get(url, headers=headers)).raise_for_status()
    data =  r.json()

    # Today's featured article
    tfa = data.get("tfa")
    tfa_title = tfa["titles"]["normalized"]
    tfa_extract = tfa["extract"]

    # Most read articles
    mostread = data.get("mostread")["articles"][:5]

    blocks = [Block("Today's featured article", Style.SUBHEADING)]
    blocks.append(Block(tfa_title))
    blocks.append(Block(tfa_extract))
    blocks.append(Block("-", Style.SUBHEADING))
    blocks.append(Block("Most read articles", Style.SUBHEADING))
    for mr in mostread:
        blocks.append(Block(mr["titles"]["normalized"]))
        blocks.append(Block(mr["description"]))
        blocks.append(Block("(" + str(mr["views"]) + " views)", Style.RIGHT_ALIGN))

    return blocks

if __name__ == "__main__":
    wikipedia_info = get_wikipedia_info()

    print("\n\n")
    for block in wikipedia_info:
        print(block.text)
    print("\n\n")
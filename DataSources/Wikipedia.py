# Provides a function to get today's featured article and the top 5 most read articles

import requests
from datetime import datetime
from blocks import Block, ImageBlock, TextBlock, Style
from typing import assert_never

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

    blocks: list[Block] = []
    blocks.append(TextBlock("Today's featured article", Style.SUBHEADING))
    blocks.append(TextBlock(tfa_title))
    blocks.append(TextBlock(tfa_extract))
    blocks.append(TextBlock("-", Style.SUBHEADING))
    blocks.append(TextBlock("Most read articles", Style.SUBHEADING))
    for mr in mostread:
        blocks.append(TextBlock(mr["titles"]["normalized"]))
        blocks.append(TextBlock(mr["description"]))
        blocks.append(TextBlock("(" + str(mr["views"]) + " views)", Style.RIGHT_ALIGN))

    return blocks

if __name__ == "__main__":
    wikipedia_blocks = get_wikipedia_info()

    print("\n\n")
    for block in wikipedia_blocks:
        match block:
            case ImageBlock():
                print("<image>")
            case TextBlock():
                print(block.text)
            case _:
                assert_never(block)
    print("\n\n")

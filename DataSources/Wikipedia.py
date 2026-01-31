# Provides a function to get today's featured article and the top 5 most read articles

import requests
from datetime import datetime

def get_wikipedia_info() -> str:
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

    blocks = [("Today's featured article", "subheading")]
    blocks.append((tfa_title, "body"))
    blocks.append((tfa_extract, "body"))
    blocks.append(("-", "subheading"))
    blocks.append(("Most read articles", "subheading"))
    for mr in mostread:
        blocks.append((mr["titles"]["normalized"], "body"))
        blocks.append((mr["description"], "body"))
        blocks.append(("(" + str(mr["views"]) + " views)", "rightAlign"))

    return blocks

if __name__ == "__main__":
    wikipedia_info = get_wikipedia_info()

    print("\n\n")
    for block in wikipedia_info:
        print(block[0])
    print("\n\n")
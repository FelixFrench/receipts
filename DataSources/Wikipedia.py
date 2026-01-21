# Provides a function to get today's featured article and the top 5 most read articles

import requests
from datetime import datetime
import textwrap

def get_wikipedia_info(width: int) -> str:
    today = datetime.now()

    url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/featured/{today.year}/{today.month:02d}/{today.day:02d}"

    headers = {
        "user-agent": "bot to access wikipedia featured articles once per day pls"
    }
    (r := requests.get(url, headers=headers)).raise_for_status()
    data =  r.json()

    # Today's featured article
    tfa = data.get("tfa")
    tfa_title = textwrap.fill(tfa["titles"]["normalized"], width=width)
    tfa_extract = textwrap.fill(tfa["extract"], width=width)

    # Most read articles
    mostread = data.get("mostread")["articles"][:5]
    mostread_titles = [textwrap.fill(mr["titles"]["normalized"], width=width) for mr in mostread]
    mostread_descriptions = [textwrap.fill(mr["description"], width=width) for mr in mostread]
    mostread_views = [("(" + str(mr["views"]) + " views)").rjust(width) for mr in mostread]
    titles_views = zip(mostread_titles, mostread_descriptions, mostread_views)
    joined_titles_views = ["\n".join(tv) for tv in titles_views]

    data_string = "Today's featured article".center(width) + "\n"
    data_string += f"{tfa_title}\n{tfa_extract}\n\n"
    data_string += "Most read articles".center(width) + "\n"
    data_string += "\n".join(joined_titles_views)

    return data_string

if __name__ == "__main__":
    wikipedia_info = get_wikipedia_info(34)

    print("\n\n")
    print(wikipedia_info)
    print("\n\n")
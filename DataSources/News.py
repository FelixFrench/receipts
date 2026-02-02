# Provides a function to get news headlines from a specified source
# N.B.: newsapi.org has a 24h delay on its free plan

import requests, json
from datetime import datetime

def get_headlines(api_key: str, source: int, count: int=5) -> str:
    """
    Gets recent headlines for a given source from newsapi.org
    Results are given as a list of blocks, where each block is (text, format)
    The list of blocks alternates between article titles and sources, where
     titles have format 'body' and sources have format 'rightAlign'
    
    Parameters:
        api_key: API key to use for newsapi.org
        source: News source to get headlines from. e.g. 'bbc-news'
        count: Max number of headlines to return
    """

    url = "https://newsapi.org/v2/top-headlines"
    params = {"sources": source, "pageSize": 100, "sortBy": "publishedAt"}
    headers = {'Authorization': api_key}
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    # Extract article titles and sources
    articles = data.get("articles", [])[:count]
    print(json.dumps(articles, indent=2))
    titles = [a.get("title","") for a in articles]
    sources = [a.get("source",{}).get("name","") for a in articles]

    # Extract published at time for each article in format "hh:mm DD/MM"
    datetimes = [datetime.fromisoformat(a.get("publishedAt","").replace("Z", "+00:00")) for a in articles]
    datetime_strings = [dt.strftime("%H:%M %d/%m") for dt in datetimes]

    # For each article, create a headline block and a '- source, time' block
    title_source_times = zip(titles, sources, datetime_strings)
    blocks = []
    for (title, source, time) in title_source_times:
        blocks.append((title, "body"))
        blocks.append(("- " + source + ", " + time, "rightAlign"))

    return blocks

if __name__ == "__main__":

    import os
    from dotenv import load_dotenv
    load_dotenv("../.env")
    NEWSAPI_ORG_KEY = os.getenv("NEWSAPI_ORG_KEY")

    news_headlines = get_headlines(NEWSAPI_ORG_KEY, "bbc-news")
    #sport_headlines = get_headlines(NEWSAPI_ORG_KEY, "bbc-sport")

    print("\n\n")
    print("NEWS")
    for block in news_headlines:
        print(block[0])
    print("\n\n")
    # print("SPORT")
    # for block in sport_headlines:
    #     print(block[0])
    # print("\n\n")
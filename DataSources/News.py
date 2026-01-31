# Provides a function to get news headlines from a specified source

import requests

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
    params = {
        "sources": source,
        "apiKey": api_key
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    # Extract article titles
    articles = data.get("articles", [])[:count]
    titles = [a.get("title","") for a in articles]
    sources = [a.get("source",{}).get("name","") for a in articles]

    title_sources = zip(titles, sources)
    blocks = []
    for (title, source) in title_sources:
        blocks.append((title, "body"))
        blocks.append(("- " + source, "rightAlign"))

    return blocks

if __name__ == "__main__":

    import os
    from dotenv import load_dotenv
    load_dotenv("../.env")
    NEWSAPI_ORG_KEY = os.getenv("NEWSAPI_ORG_KEY")

    width = 34
    news_headlines = get_headlines(NEWSAPI_ORG_KEY, "bbc-news", width)
    sport_headlines = get_headlines(NEWSAPI_ORG_KEY, "bbc-sport", width)

    print("\n\n")
    print(" NEWS ".center(width, "="))
    for block in news_headlines:
        print(block[0])
    print("\n\n")
    print(" SPORTS ".center(width, "="))
    for block in sport_headlines:
        print(block[0])
    print("\n\n")
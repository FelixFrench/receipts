# Provides a function to get news headlines from a specified source

import requests

def get_headlines(api_key: str, source: int, count: int=5) -> str:
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

    import Secrets
    width = 34
    news_headlines = get_headlines(Secrets.newsapi_org_key, "bbc-news", width)
    sport_headlines = get_headlines(Secrets.newsapi_org_key, "bbc-sport", width)

    print("\n\n")
    print(" NEWS ".center(width, "="))
    print(news_headlines)
    print("\n\n")
    print(" SPORTS ".center(width, "="))
    print(sport_headlines)
    print("\n\n")
import feedparser, requests
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from io import BytesIO
from PIL import Image, ImageFile
from blocks import Block, Style
from dataclasses import dataclass

@dataclass(frozen=True)
class Headlines:
    blocks: list[Block]
    image: ImageFile.ImageFile | None = None

HEADLINES_UNAVAILABLE = Headlines([Block("Not available")])

@dataclass(frozen=True)
class Article:
    title: str
    pub_date: str
    thumb_url: str | None

def get_headline_data(rss_url:str, limit:int=5, max_age:int=24) -> list[Article]:
    """
    Fetch up to `limit` articles from the given RSS feed
    published in the last so many hours.

    Args:
        limit (int): Maximum number of articles to return.
        max_age (int): Maximum time since publishing in hours
        rss_url (str): RSS feed URL.

    Returns:
        List of tuples: (title, formatted_pubDate, media_thumbnail_url)
        where formatted_pubDate is a "HH:MM DD/MM" string.
    """
    feed = feedparser.parse(rss_url)

    if feed.bozo:
        raise RuntimeError(f"Failed to parse RSS feed: {rss_url}")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age)

    results: list[Article] = []

    for entry in feed.entries:
        if len(results) >= limit:
            break

        title = entry.get("title")
        if not isinstance(title, str):
            continue

        if not hasattr(entry, "published"):
            continue

        try:
            pub_date = parsedate_to_datetime(entry.published)
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
        except Exception:
            continue

        if pub_date < cutoff:
            continue

        # Format date as hh:mm DD/MM
        formatted_date = pub_date.strftime("%H:%M %d/%m")

        # Extract thumbnail url if present
        thumbnail_url = None
        if "media_thumbnail" in entry and entry.media_thumbnail:
            thumbnail_url = entry.media_thumbnail[0].get("url")

        results.append(Article(title, formatted_date, thumbnail_url))

    return results

def format_news(articles: list[Article]) -> Headlines:
    """
    Format output from get_headline_data ready for printing.

    Args:
        articles: List of Article

    Returns:
        Headlines
    """
    
    blocks = []
    image = None

    for a in articles:
        blocks.append(Block(a.title))
        blocks.append(Block(a.pub_date, Style.RIGHT_ALIGN))

    # Try to get an image for the first article
    try:
        first_thumbnail = articles[0].thumb_url if articles else None
        if first_thumbnail:
            response = requests.get(first_thumbnail)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
    except Exception:
        pass

    return Headlines(blocks, image)


def get_headlines(rss_url: str, limit: int = 5, max_age: int = 24) -> Headlines:
    articles = get_headline_data(rss_url, limit, max_age)
    return format_news(articles)


if __name__ == "__main__":

    from config import load_config

    cfg = load_config()
    

    # Load in RSS feed urls
    feeds = [
        cfg.news_national,
        cfg.news_local,
        cfg.news_sport,
    ]

    for feed_url in feeds:
        print(f"\nFeed: {feed_url}\n")
        articles = get_headline_data(feed_url)

        for a in articles:
            print(f"Title: {a.title}")
            print(f"Published: {a.pub_date}")
            print(f"Thumbnail: {a.thumb_url}")
            print("-" * 40)

        headlines = format_news(articles)

        print("\n\n")
        for block in headlines.blocks:
            print(block.text)
        print("\n\n")

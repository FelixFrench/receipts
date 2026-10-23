import feedparser, requests
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from io import BytesIO
from PIL import Image, ImageFile

type Headlines = tuple[ImageFile.ImageFile | None, list[tuple[str, str]]]
HEADLINES_UNAVAILABLE: Headlines = (None, [("Not available", "body")])


def get_headline_data(rss_url:str, limit:int=5, max_age:int=24) -> list[tuple[str,str,str|None]]:
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

    results: list[tuple[str, str, str | None]] = []

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

        results.append((title, formatted_date, thumbnail_url))

    return results

def format_news(articles: list[tuple[str, str, str|None]]) -> Headlines:
    """
    Format output from get_recent_bbc_headlines ready for printing.

    Args:
        articles: List of tuples:
                  (title, formatted_pubDate, media_thumbnail_url)

    Returns:
        (first_thumbnail_url, formatted_list)

        formatted_list: [
            (headline 1, 'body'),
            (date 1, 'rightAlign'),
            (headline 2, 'body'),
            ...
        ]
    """
    formatted: list[tuple[str, str]] = []

    for title, pub_date, _ in articles:
        formatted.append((title, 'body'))
        formatted.append((pub_date, 'rightAlign'))

    # Try to get an image for the first article
    try:
        first_thumbnail = articles[0][2] if articles else None
        if first_thumbnail:
            response = requests.get(first_thumbnail)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
        else:
            image = None

    except Exception:
        image = None

    return (image, formatted)


def get_headlines(rss_url: str, limit: int = 5, max_age: int = 24) -> Headlines:
    articles = get_headline_data(rss_url, limit, max_age)
    return format_news(articles)


if __name__ == "__main__":

    from config import NEWS_NATIONAL, NEWS_LOCAL, NEWS_SPORT
    

    # Load in RSS feed urls
    feeds = [
        NEWS_NATIONAL,
        NEWS_LOCAL,
        NEWS_SPORT,
    ]

    for feed_url in feeds:
        print(f"\nFeed: {feed_url}\n")
        articles = get_headline_data(feed_url)

        for title, pub_date, thumbnail in articles:
            print(f"Title: {title}")
            print(f"Published: {pub_date}")
            print(f"Thumbnail: {thumbnail}")
            print("-" * 40)

        _, news_formatted = format_news(articles)

        print("\n\n")
        for block in news_formatted:
            print(block[0])
        print("\n\n")

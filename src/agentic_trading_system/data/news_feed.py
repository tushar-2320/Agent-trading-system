import feedparser  # type: ignore

rss_feed_urls = [
    "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/business.xml",
    "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/economy.xml",
    "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/market.xml",
]

articles = []


def parse_cnbc_rss(url):
    _articles = []
    feed = feedparser.parse(url)
    for item in feed.entries:
        # use xml format in prompt.
        data = {
            "source": "CNBC-TV18",
            "title": item.get("title", "").strip(),
            "url": item.get("link", "").strip(),
            "description": item.get("summary", "").strip(),
            "published": item.get("published", "").strip(),
            "author": item.get("author", "").strip(),
        }
        _articles.append(data)
    return _articles


for url in rss_feed_urls:
    articles.extend(parse_cnbc_rss(url))

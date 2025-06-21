import feedparser
from config import FEED_URLS

seen_links = set()

def check_new_posts():
    new_entries = []

    for url in FEED_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.link not in seen_links:
                seen_links.add(entry.link)
                new_entries.append((entry.title, entry.link))

    return new_entries

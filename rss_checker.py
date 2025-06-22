import feedparser
import time
from config import FEED_URLS

# Store seen links in memory
seen_links = set()

def check_new_posts():
    """
    Check each RSS feed for new entries.
    Only return posts not seen before.
    """
    new_entries = []

    for url in FEED_URLS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"⚠️ Error parsing feed: {url} — {feed.bozo_exception}")
                continue

            for entry in feed.entries:
                link = entry.get("link")
                title = entry.get("title", "Untitled")

                if link and link not in seen_links:
                    seen_links.add(link)
                    new_entries.append((title, link))

        except Exception as e:
            print(f"❌ Failed to parse feed {url}: {e}")

    return new_entries

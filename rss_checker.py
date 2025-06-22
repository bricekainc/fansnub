import feedparser
from config import FEED_URLS

# --- In-memory storage ---
_cached_entries = []
_cached_creators = []
_cached_posts = []
seen_links = set()


def parse_all_feeds():
    """Parse all feeds and cache creators/posts."""
    global _cached_entries, _cached_creators, _cached_posts

    all_entries = []
    for url in FEED_URLS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"⚠️ Error parsing feed: {url} — {feed.bozo_exception}")
                continue
            all_entries.extend(feed.entries)
        except Exception as e:
            print(f"❌ Failed to parse feed {url}: {e}")

    _cached_entries = all_entries
    _cached_creators = []
    _cached_posts = []

    # Extract creators
    creators_dict = {}
    for entry in all_entries:
        author = entry.get("author", "").strip()
        link = entry.get("link", "").strip()
        if author:
            creators_dict[author] = {
                "name": author,
                "username": author.lower().replace(" ", "_"),
                "link": link,
            }
    _cached_creators = list(creators_dict.values())

    # Extract posts
    for entry in all_entries:
        _cached_posts.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "tags": entry.get("tags", []),
        })


def get_all_creators(limit=10, offset=0):
    return _cached_creators[offset:offset + limit]


def get_all_posts(limit=10, offset=0):
    return _cached_posts[offset:offset + limit]


def search_creators(keyword, limit=10, offset=0):
    keyword = keyword.lower()
    results = [
        c for c in _cached_creators
        if keyword in c.get("name", "").lower()
    ]
    return results[offset:offset + limit]


def search_posts(keyword, limit=10, offset=0):
    keyword = keyword.lower()
    results = [
        p for p in _cached_posts
        if keyword in p.get("title", "").lower()
    ]
    return results[offset:offset + limit]


def search_posts_by_tag(tag, limit=10, offset=0):
    tag = tag.lower()
    results = [
        p for p in _cached_posts
        if any(tag in t.get("term", "").lower() for t in p.get("tags", []))
    ]
    return results[offset:offset + limit]


def check_new_posts():
    """Return newly seen posts since last check."""
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

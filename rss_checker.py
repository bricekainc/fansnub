import feedparser
from config import FEED_URLS

# --- Cache ---
_cached_entries = []
_seen_links = set()


def refresh_feed_cache():
    """Re-parse all feeds and cache them."""
    global _cached_entries
    entries = []
    for url in FEED_URLS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"⚠️ Error parsing feed: {url} — {feed.bozo_exception}")
                continue
            entries.extend(feed.entries)
        except Exception as e:
            print(f"❌ Failed to parse feed {url}: {e}")
    _cached_entries = entries


def get_all_creators(limit=10, offset=0):
    """Extract unique creators from cached entries."""
    creators = {}
    for entry in _cached_entries:
        author = entry.get("author", "").strip()
        if not author:
            continue
        if author not in creators:
            link = entry.get("author_detail", {}).get("href") or entry.get("link", "")
            creators[author] = {
                "name": author,
                "username": author.lower().replace(" ", "_"),
                "link": link,
            }
    creators_list = list(creators.values())
    return creators_list[offset:offset + limit]


def get_all_posts(limit=10, offset=0):
    """Return blog posts from cached entries."""
    posts = []
    for entry in _cached_entries:
        posts.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "tags": entry.get("tags", []),
        })
    return posts[offset:offset + limit]


def search_creators(keyword, limit=10, offset=0):
    """Search cached creators by keyword."""
    keyword = keyword.lower()
    creators = get_all_creators(limit=1000)
    filtered = [c for c in creators if keyword in c["name"].lower()]
    return filtered[offset:offset + limit]


def search_posts(keyword, limit=10, offset=0):
    """Search cached posts by keyword in title."""
    keyword = keyword.lower()
    posts = get_all_posts(limit=1000)
    filtered = [p for p in posts if keyword in p["title"].lower()]
    return filtered[offset:offset + limit]


def search_posts_by_tag(tag, limit=10, offset=0):
    """Search cached posts by tag."""
    tag = tag.lower()
    posts = get_all_posts(limit=1000)
    filtered = [
        p for p in posts
        if any(tag in (t.get("term", "") or "").lower() for t in p.get("tags", []))
    ]
    return filtered[offset:offset + limit]


def check_new_posts():
    """Find new posts by comparing links to the seen set."""
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

                if link and link not in _seen_links:
                    _seen_links.add(link)
                    new_entries.append((title, link))

        except Exception as e:
            print(f"❌ Failed to parse feed {url}: {e}")

    return new_entries

import feedparser
import os
from config import FEED_URLS

# Memory storage for seen links (used during polling)
seen_links = set()


def parse_all_feeds():
    """Parse and return all entries from all feeds"""
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
    return all_entries


def get_all_creators(limit=10, offset=0):
    """Return a simplified list of unique creators from feeds"""
    entries = parse_all_feeds()
    creators = {}

    for entry in entries:
        author = entry.get("author", "").strip()
        link = entry.get("link", "").strip()
        if author:
            creators[author] = {
                "name": author,
                "username": author.lower().replace(" ", "_"),
                "link": link,
            }

    creators_list = list(creators.values())
    return creators_list[offset:offset + limit]


def get_all_posts(limit=10, offset=0):
    """Return all blog posts (entries)"""
    entries = parse_all_feeds()
    posts = []

    for entry in entries:
        posts.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "tags": entry.get("tags", []),
        })

    return posts[offset:offset + limit]


def search_creators(keyword, limit=10, offset=0):
    """Search creators by name"""
    keyword = keyword.lower()
    creators = get_all_creators(limit=1000)
    filtered = [c for c in creators if keyword in c["name"].lower()]
    return filtered[offset:offset + limit]


def search_posts(keyword, limit=10, offset=0):
    """Search posts by title"""
    keyword = keyword.lower()
    posts = get_all_posts(limit=1000)
    filtered = [p for p in posts if keyword in p["title"].lower()]
    return filtered[offset:offset + limit]


def search_posts_by_tag(tag, limit=10, offset=0):
    """Search posts by tag (RSS must have <category> tags)"""
    tag = tag.lower()
    posts = get_all_posts(limit=1000)
    filtered = [
        p for p in posts
        if any(tag in t["term"].lower() for t in p.get("tags", []))
    ]
    return filtered[offset:offset + limit]


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

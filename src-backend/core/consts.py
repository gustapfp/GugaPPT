from pathlib import Path

FILE_PATH = Path(__file__).resolve().parent.parent.parent / "concluded_presentations"


DOMAIN_BLACKLIST = [
    "reddit.com",
    "quora.com",
    "twitter.com",
    "facebook.com",
    "instagram.com",
]

DOMAIN_WHITELIST = [
    "wikipedia.org",
    "reuters.com",
    "bloomberg.com",
    "nature.com",
    "sciencedirect.com",
    "techcrunch.com",
]

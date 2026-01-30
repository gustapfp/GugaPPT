from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


class SourceValidator:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def normalize_url(self, url: str) -> str:
        """Removes query parameters (UTM, etc.) and fragments."""
        parsed = urlparse(url)
        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
        return clean_url

    def get_metadata(self, html_soup) -> dict:
        """Extracts author, date, and reference indicators."""
        meta = {"author": None, "date": None, "has_references": False}

        author_tag = html_soup.find("meta", {"name": "author"}) or html_soup.find(
            "meta", property="article:author"
        )
        if author_tag:
            meta["author"] = author_tag.get("content")

        date_tag = (
            html_soup.find("meta", {"name": "date"})
            or html_soup.find("meta", property="article:published_time")
            or html_soup.find("time")
        )
        if date_tag:
            meta["date"] = date_tag.get("content") or date_tag.get_text()

        headers = html_soup.find_all(["h1", "h2", "h3", "h4"])
        ref_keywords = ["references", "bibliography", "works cited", "sources"]
        for h in headers:
            if any(k in h.get_text().lower() for k in ref_keywords):
                meta["has_references"] = True
                break

        return meta

    def validate_url(self, url: str) -> dict:
        """Performs the full health check and scoring."""
        clean_url = self.normalize_url(url)
        result = {"url": clean_url, "status": "dead", "score": 0, "tier": "C", "details": {}}

        try:
            response = requests.get(clean_url, headers=self.headers, timeout=5)
            if response.status_code != 200:
                return result

            result["status"] = "live"
            soup = BeautifulSoup(response.content, "html.parser")

            meta = self.get_metadata(soup)
            result["details"] = meta

            score = 20

            domain = urlparse(clean_url).netloc  # Domain trust bonus
            if domain.endswith((".edu", ".gov")):
                score += 20

            if meta["author"]:
                score += 20
            if meta["date"]:
                score += 20
            if meta["has_references"]:
                score += 20

            result["score"] = min(score, 100)

            if score >= 80:
                result["tier"] = "S"  # Gold standard
            elif score >= 50:
                result["tier"] = "A"  # Reliable
            else:
                result["tier"] = "B"  # Shouldn't be used caution

        except Exception as e:
            result["error"] = str(e)

        return result

    def rank_sources(self, raw_results: list[dict]) -> list[dict]:
        """Ranks the sources based on the validation score.

        Args:
            raw_results (list[dict]): The raw results from the web search.

        Returns:
            list[dict]: The ranked results.
        """
        ranked_results = []
        for item in raw_results:
            url = item.get("url", "")
            validation = self.validate_url(url)

            ranked_item = {**item, "validation": validation}
            ranked_results.append(ranked_item)

        return sorted(ranked_results, key=lambda x: x["validation"]["score"], reverse=True)


source_validator = SourceValidator()

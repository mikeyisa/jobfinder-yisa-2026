"""Lever public postings API: no auth, ToS-friendly.
GET https://api.lever.co/v0/postings/{token}?mode=json"""
import re
import html
from datetime import datetime
import httpx

API = "https://api.lever.co/v0/postings/{token}?mode=json"


def _strip_html(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fetch(token: str) -> list[dict]:
    r = httpx.get(API.format(token=token), timeout=20)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        return []
    out = []
    for j in data:
        cats = j.get("categories") or {}
        out.append({
            "source": "lever",
            "company": token,
            "title": j.get("text", ""),
            "location": cats.get("location", ""),
            "url": j.get("hostedUrl", ""),
            "description": _strip_html(j.get("descriptionPlain") or j.get("description", ""))[:8000],
            "posted_at": datetime.utcfromtimestamp(j["createdAt"] / 1000) if j.get("createdAt") else None,
        })
    return out

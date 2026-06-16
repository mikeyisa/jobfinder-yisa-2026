"""Greenhouse public job-board API: no auth, no scraping, ToS-friendly.
GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"""
import re
import html
from datetime import datetime
import httpx

API = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"


def _parse(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _strip_html(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fetch(token: str) -> list[dict]:
    r = httpx.get(API.format(token=token), timeout=20)
    r.raise_for_status()
    out = []
    for j in r.json().get("jobs", []):
        out.append({
            "source": "greenhouse",
            "company": token,
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url", ""),
            "description": _strip_html(j.get("content", ""))[:8000],
            "posted_at": _parse(j.get("updated_at") or j.get("first_published")),
        })
    return out

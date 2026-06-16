"""GitHub-hosted new-grad job board (SimplifyJobs/New-Grad-Positions). Public,
community-maintained listings.json — thousands of entry-level SWE roles with
structured company/title/location/sponsorship. Perfect for the junior lane.
ToS-friendly (public raw file, no scraping)."""
import httpx

SWE = ("software", "engineer", "developer", "swe", "backend", "front end",
       "frontend", "full stack", "full-stack", "data", "ml ", "machine learning",
       "cloud", "devops", "sre", "platform", "security")


def fetch(url: str, cap: int = 400) -> list[dict]:
    r = httpx.get(url, timeout=30, headers={"User-Agent": "jobfinder-yisa"})
    r.raise_for_status()
    rows = [j for j in r.json()
            if j.get("active") and j.get("is_visible", True)
            and any(k in (j.get("title", "").lower()) for k in SWE)
            and (j.get("url") or j.get("company_url"))]
    rows.sort(key=lambda j: j.get("date_updated") or j.get("date_posted") or 0, reverse=True)
    out = []
    for j in rows[:cap]:
        locs = j.get("locations") or []
        loc = "; ".join(locs) if isinstance(locs, list) else str(locs)
        spons = j.get("sponsorship", "")
        out.append({
            "source": "github-newgrad",
            "company": (j.get("company_name") or "unknown").strip(),
            "title": j.get("title", ""),
            "location": loc,
            "url": j.get("url") or j.get("company_url"),
            "description": (f"New-grad / entry-level software role: {j.get('title','')} "
                            f"at {j.get('company_name','')}. Locations: {loc}. "
                            f"Sponsorship: {spons}."),
        })
    return out

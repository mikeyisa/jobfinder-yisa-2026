"""Posting recency — fresh roles (<24h) get real responses because the recruiter
is actively reviewing. Drives a ranking boost + the age chip + the ≤24h filter."""
from datetime import datetime, timezone


def age_hours(dt: datetime | None):
    if not dt:
        return None
    if dt.tzinfo:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return max(0.0, (datetime.utcnow() - dt).total_seconds() / 3600)


def score(dt: datetime | None) -> int:
    h = age_hours(dt)
    if h is None:
        return 30
    if h <= 24:
        return 100
    if h <= 72:
        return 80
    if h <= 24 * 7:
        return 60
    if h <= 24 * 30:
        return 40
    return 20


def label(dt: datetime | None) -> str:
    h = age_hours(dt)
    if h is None:
        return "—"
    if h < 1:
        return "just now"
    if h < 24:
        return f"{int(h)}h ago"
    d = int(h / 24)
    if d < 30:
        return f"{d}d ago"
    return f"{int(d / 30)}mo ago"

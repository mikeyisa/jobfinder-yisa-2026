"""Scorer agent: resume-vs-JD fit. Structured output so the UI/DB get clean
fields. Falls back to a keyword heuristic when no API key is configured."""
import llm

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "fit_score": {"type": "integer"},                       # 0-100
        "recommend": {"type": "boolean"},
        "clearance_signal": {"type": "string",
                             "enum": ["none", "eligible_ok", "active_required"]},
        "seniority_match": {"type": "string",
                            "enum": ["good", "too_junior", "too_senior"]},
        "reasons": {"type": "array", "items": {"type": "string"}},
        "gaps": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
    "required": ["fit_score", "recommend", "clearance_signal",
                 "seniority_match", "reasons", "gaps", "summary"],
}

INSTRUCTION = (
    "Score how well THIS candidate fits the job description below. The candidate "
    "wants BOTH defense/cleared roles AND regular junior/mid SWE roles — judge a "
    "good non-defense junior/mid software role just as favorably as a defense one. "
    "Do not penalize a role for being non-defense.\n"
    "- fit_score 0-100. Give 70+ to solid junior/mid SWE roles that match the "
    "candidate's .NET / Python / AWS / full-stack background at an appropriate level. "
    "Reserve 85+ for excellent fits.\n"
    "- clearance_signal: 'active_required' if the role needs an ACTIVE clearance the "
    "candidate lacks; 'eligible_ok' if clearance-eligible/sponsorable is accepted; "
    "'none' if clearance is irrelevant (most commercial roles). Clearance is a BONUS, "
    "never required for a high score.\n"
    "- seniority_match: 'too_senior' if it needs 5+ yrs / senior / staff / principal; "
    "'too_junior' only if clearly below the candidate; else 'good' (entry, new-grad, "
    "associate, mid, 'I', 'II' all count as good).\n"
    "- recommend = true if seniority_match='good', clearance_signal != "
    "'active_required', and fit_score >= 58.\n"
    "- reasons: 2-4 concrete fit points. gaps: missing/weak areas. summary: one line."
)


def score(job: dict) -> dict:
    if not llm.have_key():
        return _heuristic(job)
    jd = f"COMPANY: {job['company']}\nTITLE: {job['title']}\nLOCATION: {job['location']}\n\nJOB DESCRIPTION:\n{job['description']}"
    return llm.structured(INSTRUCTION, jd, SCHEMA, max_tokens=1200)


def _heuristic(job: dict) -> dict:
    """No-key fallback so the pipeline runs end-to-end before a key is added."""
    t = (job["title"] + " " + job["description"]).lower()
    senior = job.get("too_senior")
    base = min(95, int(job.get("prefilter_score", 0) * 10) + 35)
    needs_active = "active clearance" in t or "ts/sci" in t or "must have a secret" in t
    return {
        "fit_score": 40 if senior else base,
        "recommend": (not senior) and (not needs_active) and base >= 60,
        "clearance_signal": "active_required" if needs_active else (
            "eligible_ok" if "clearance" in t else "none"),
        "seniority_match": "too_senior" if senior else "good",
        "reasons": ["Heuristic match on niche keywords (add ANTHROPIC_API_KEY for real Claude scoring)."],
        "gaps": ["Real fit analysis requires Claude — set your API key."],
        "summary": "Heuristic pre-score; configure ANTHROPIC_API_KEY for full scoring.",
    }

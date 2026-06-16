"""Email-organizer agent (roadmap item, draft-only). Paste a recruiter/job email
and it classifies, labels, prioritizes, and DRAFTS a reply — never sends. Real
Gmail API hookup (OAuth, auto-label) is the next step; this is the brain it will
use. Falls back to a keyword heuristic with no API key."""
import llm
from config import CANDIDATE_NAME

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "category": {"type": "string", "enum": [
            "interview_invite", "recruiter_outreach", "offer", "rejection",
            "follow_up_needed", "other"]},
        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
        "label": {"type": "string"},
        "action": {"type": "string"},
        "needs_reply": {"type": "boolean"},
        "draft_reply": {"type": "string"},
    },
    "required": ["category", "priority", "label", "action", "needs_reply", "draft_reply"],
}

INSTRUCTION = (
    "You triage the candidate's job-search inbox. For the email below:\n"
    "- category/priority/label (a short Gmail label like 'Interviews', 'Recruiters').\n"
    "- action: one line on what to do next.\n"
    "- needs_reply + draft_reply: if a reply is warranted, write it (concise, "
    f"professional, signed '{CANDIDATE_NAME}'). For interview invites, propose "
    "availability windows as placeholders. Never send — this is a draft."
)


def organize(email_text: str) -> dict:
    if not llm.have_key():
        return _heuristic(email_text)
    return llm.structured(INSTRUCTION, f"EMAIL:\n{email_text}", SCHEMA, max_tokens=1200)


def _heuristic(text: str) -> dict:
    t = text.lower()
    if any(k in t for k in ["interview", "schedule a call", "availability", "meet"]):
        cat, pri, lbl = "interview_invite", "high", "Interviews"
    elif "unfortunately" in t or "not moving forward" in t or "other candidates" in t:
        cat, pri, lbl = "rejection", "low", "Rejections"
    elif "offer" in t:
        cat, pri, lbl = "offer", "high", "Offers"
    elif any(k in t for k in ["recruiter", "opportunity", "role", "reaching out"]):
        cat, pri, lbl = "recruiter_outreach", "medium", "Recruiters"
    else:
        cat, pri, lbl = "other", "low", "Job Search"
    return {
        "category": cat, "priority": pri, "label": lbl,
        "action": "Set ANTHROPIC_API_KEY for full triage + auto-drafted replies.",
        "needs_reply": cat in ("interview_invite", "recruiter_outreach", "offer"),
        "draft_reply": "(Claude-drafted reply appears here once your API key is set.)",
    }

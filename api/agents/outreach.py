"""Outreach agent: drafts a cold EMAIL the candidate can send from a dedicated
application inbox. Channel is always email — NEVER LinkedIn (per candidate's
explicit constraint and to avoid account risk)."""
import llm
from config import APPLICATION_EMAIL, CANDIDATE_NAME

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "contact_target": {"type": "string"},   # role to find an email for
        "subject": {"type": "string"},
        "message": {"type": "string"},
    },
    "required": ["contact_target", "subject", "message"],
}

INSTRUCTION = (
    "Draft a concise, high-signal cold OUTREACH EMAIL for this candidate to send "
    "for the job below. Do NOT mention or use LinkedIn.\n"
    "- contact_target: the best role to find a direct email for (e.g. 'Engineering "
    "Manager for the team', 'University/early-career recruiter').\n"
    "- subject: a specific, non-generic subject line.\n"
    "- message: 120-160 words, warm but professional, signed off as "
    f"'{CANDIDATE_NAME}'. Lead with the single strongest fit point, name a "
    "concrete achievement from the resume, and end with a soft ask for a chat. "
    "Plain text, no placeholders left unfilled."
)


def draft(job: dict, style_notes: str = "") -> dict:
    if not llm.have_key():
        return {
            "contact_target": "Engineering Manager / early-career recruiter",
            "subject": f"Re: {job['title']} — quick intro",
            "message": "Set ANTHROPIC_API_KEY to auto-generate a tailored outreach email.",
            "channel": "email",
            "send_from": APPLICATION_EMAIL,
        }
    instruction = INSTRUCTION
    if style_notes.strip():
        instruction += ("\n\nLEARNED PREFERENCES from past tweaks — honor these:\n"
                        + style_notes)
    jd = f"TITLE: {job['title']} @ {job['company']}\n\nJOB DESCRIPTION:\n{job['description']}"
    out = llm.structured(instruction, jd, SCHEMA, max_tokens=900)
    out["channel"] = "email"
    out["send_from"] = APPLICATION_EMAIL
    return out

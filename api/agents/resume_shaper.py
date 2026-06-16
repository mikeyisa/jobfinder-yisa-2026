"""Resume-shaper agent: rewrites the candidate's resume FOR this specific job —
ATS-aligned summary, reordered/selected bullets, keyword list. Truth-preserving:
it may reframe and reorder real experience, never invent it."""
import llm

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "headline": {"type": "string"},
        "summary": {"type": "string"},
        "bullets": {"type": "array", "items": {"type": "string"}},
        "keywords": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["headline", "summary", "bullets", "keywords"],
}

INSTRUCTION = (
    "Tailor the candidate's resume to maximize ATS + recruiter fit for the job "
    "below. STRICT RULE: use only real experience from the resume — reframe, "
    "reorder, and re-emphasize, but never fabricate.\n"
    "- headline: a targeting headline matching the role.\n"
    "- summary: 2-3 sentence pitch tuned to this job.\n"
    "- bullets: 6-9 strongest, reworded to mirror the JD's language and surface "
    "matching keywords/metrics.\n"
    "- keywords: exact ATS terms from the JD the candidate legitimately has."
)


def shape(job: dict, style_notes: str = "") -> dict:
    if not llm.have_key():
        return {
            "headline": f"Targeting: {job['title']} @ {job['company']}",
            "summary": "Set ANTHROPIC_API_KEY to auto-generate a tailored resume.",
            "bullets": ["(Claude-tailored bullets appear here once a key is set.)"],
            "keywords": [],
        }
    instruction = INSTRUCTION
    if style_notes.strip():
        instruction += ("\n\nLEARNED STYLE PREFERENCES from the candidate's past "
                        "tweaks — honor all of these:\n" + style_notes)
    jd = f"TITLE: {job['title']} @ {job['company']}\n\nJOB DESCRIPTION:\n{job['description']}"
    return llm.structured(instruction, jd, SCHEMA, max_tokens=2000)

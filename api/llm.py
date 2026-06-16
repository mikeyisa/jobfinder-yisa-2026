"""Thin Claude wrapper — the teaching core. Every specialist agent calls
`structured()` with its own JSON schema. The resume is sent as a cached system
block on every call, so repeated scoring is cheap (prompt caching = ~0.1x on the
resume tokens). If no API key is set, callers fall back to heuristics so the
whole pipeline still runs for a demo."""
import json
from typing import Any

import anthropic

from config import ANTHROPIC_API_KEY, MODEL, CANDIDATE_CONTEXT
from resume_parser import resume_text

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


def have_key() -> bool:
    return _client is not None


def _resume_system_block() -> dict:
    """Stable, cacheable system block: persona + candidate context + full resume.
    Kept byte-stable across calls so the prompt cache actually hits."""
    text = (
        "You are an elite technical recruiter and career strategist who screens "
        "candidates the way a real ATS + hiring manager would. You are blunt and "
        "evidence-based.\n\n"
        f"CANDIDATE CONTEXT: {CANDIDATE_CONTEXT}\n\n"
        f"CANDIDATE RESUME (verbatim):\n{resume_text()}"
    )
    return {"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}


def structured(instruction: str, user: str, schema: dict[str, Any],
               max_tokens: int = 1500) -> dict:
    """One structured Claude call. `instruction` = the per-agent task (volatile,
    goes after the cached resume). Returns the parsed JSON object."""
    resp = _client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=[_resume_system_block(), {"type": "text", "text": instruction}],
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    text = next((b.text for b in resp.content if b.type == "text"), "{}")
    return json.loads(text)

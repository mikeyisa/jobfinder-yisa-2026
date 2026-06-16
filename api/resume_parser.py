"""Parse the .docx resume into plain text once and cache it. The plain text is
what the Claude agents read (and what we prompt-cache on every call)."""
import glob
from functools import lru_cache

from config import RESUME_DIR


def _read_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(parts)


@lru_cache(maxsize=1)
def resume_text() -> str:
    """Return the resume as plain text. Prefers a cached .txt, falls back to the
    first .docx in data/resume/."""
    txt = RESUME_DIR / "resume.txt"
    if txt.exists():
        return txt.read_text(encoding="utf-8")
    docx_matches = sorted(glob.glob(str(RESUME_DIR / "*.docx")))
    if docx_matches:
        text = _read_docx(docx_matches[0])
        txt.write_text(text, encoding="utf-8")  # cache for next time / Docker
        return text
    return ""  # no resume yet — agents degrade gracefully

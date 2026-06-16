"""Central config. Everything is env-overridable so the same code runs locally
(SQLite, no key needed for a demo) and on Docker/AWS (Postgres + real Claude)."""
import os
from pathlib import Path
from dotenv import load_dotenv

# --- paths -------------------------------------------------------------------
API_DIR = Path(__file__).resolve().parent
ROOT_DIR = API_DIR.parent

# Load .env from the project root first (works regardless of launch dir), then
# any .env in the current working directory as a fallback.
load_dotenv(ROOT_DIR / ".env")
load_dotenv()
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT_DIR / "data"))
RESUME_DIR = DATA_DIR / "resume"
WEB_DIR = ROOT_DIR / "web"
for d in (DATA_DIR, RESUME_DIR):
    d.mkdir(parents=True, exist_ok=True)

# --- database ----------------------------------------------------------------
# Local default = SQLite (zero setup). Docker compose overrides with Postgres.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'jobfinder.db'}")

# --- Claude ------------------------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
# Per Anthropic guidance the default is the most capable Opus. Cost lever:
# set MODEL=claude-sonnet-4-6 (≈70% cheaper) for high-volume runs.
MODEL = os.getenv("MODEL", "claude-opus-4-8")

# --- candidate profile (Michael) --------------------------------------------
APPLICATION_EMAIL = os.getenv("APPLICATION_EMAIL", "michael.apply.2026@gmail.com")
CANDIDATE_NAME = os.getenv("CANDIDATE_NAME", "Michael Yisa")
# Your real situation, fed to the scorer so it targets correctly.
CANDIDATE_CONTEXT = os.getenv(
    "CANDIDATE_CONTEXT",
    "U.S. citizen (naturalized), clearance-ELIGIBLE (no active clearance, no "
    "disqualifiers). Early-career: ~6 months full-time SWE + internships, Dec 2025 "
    "CS grad. OPEN TO TWO LANES, both valid: (1) cleared/defense/govtech roles that "
    "sponsor or accept 'clearance eligible' — a bonus tier, and (2) regular "
    "junior/mid software engineer roles at any good company. Score strong junior/mid "
    "SWE roles highly even when they have nothing to do with defense. Clearance is a "
    "PLUS, never a requirement. Do NOT recommend roles needing an ACTIVE clearance or "
    "5+ years / senior+ experience. Location preference (closer is better): Austin, "
    "then Houston/Dallas/Texas, Atlanta, New York, New Jersey, Oregon, Arizona, "
    "Colorado, US-remote; deprioritize international.",
)

# --- pipeline knobs ----------------------------------------------------------
# Only the top-N pre-filtered jobs get sent to Claude (controls cost + latency).
SCORE_TOP_N = int(os.getenv("SCORE_TOP_N", "20"))
# Keywords the cheap heuristic pre-filter rewards (broad SWE + the clearance niche).
NICHE_KEYWORDS = [
    "software engineer", "developer", "backend", "front end", "frontend",
    "full stack", "full-stack", ".net", "c#", "python", "java", "javascript",
    "typescript", "react", "node", "aws", "cloud", "api", "data", "ml", "ai",
    "platform", "new grad", "early career", "associate", "graduate", "entry",
    "engineer i", "engineer ii", "clearance", "secret", "defense", "govtech",
]
SENIOR_FLAGS = [
    "senior", "sr.", "sr ", "staff", "principal", "lead", "manager", "director",
    " vp", "head of", "fellow", " iii", " iv", "architect", "10+", "8+ years",
    "7+ years",
]

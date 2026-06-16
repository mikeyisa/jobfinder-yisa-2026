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
    "U.S. citizen (naturalized), no security clearance yet but fully clearance-"
    "ELIGIBLE (no disqualifiers). Target roles that sponsor clearance or accept "
    "'clearance eligible'. Early-career: ~6 months full-time SWE + internships, "
    "Dec 2025 CS grad. Do NOT recommend roles requiring an ACTIVE clearance or "
    "5+ years experience.",
)

# --- pipeline knobs ----------------------------------------------------------
# Only the top-N pre-filtered jobs get sent to Claude (controls cost + latency).
SCORE_TOP_N = int(os.getenv("SCORE_TOP_N", "15"))
# Keywords that define the niche, used by the cheap heuristic pre-filter.
NICHE_KEYWORDS = [
    "software engineer", "backend", "full stack", "full-stack", ".net", "c#",
    "python", "aws", "cloud", "api", "data", "ml", "ai", "platform",
    "clearance", "secret", "ts/sci", "defense", "govtech",
]
SENIOR_FLAGS = [
    "senior", "staff", "principal", "lead", "manager", "director", " vp",
    "head of", " iii", " iv", "architect", "10+", "8+ years", "7+ years",
]

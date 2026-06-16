"""ToS-friendly, public, no-auth job sources only. NEVER LinkedIn or Indeed —
automating those risks the candidate's own accounts."""
from . import greenhouse, lever

# (source_module, company_token) — verified live during build.
SEED_BOARDS = [
    (greenhouse, "anthropic"),      # AI / cloud
    (greenhouse, "databricks"),     # data / cloud / AI
    (greenhouse, "scaleai"),        # AI, incl. defense arm
    (greenhouse, "vannevarlabs"),   # national-security / defense AI (clearance niche)
    (greenhouse, "primerai"),       # defense / govtech NLP (clearance niche)
    (lever, "palantir"),            # defense / govtech (clearance niche)
]


def fetch_all() -> list[dict]:
    jobs: list[dict] = []
    for module, token in SEED_BOARDS:
        try:
            jobs.extend(module.fetch(token))
        except Exception as e:  # one bad board shouldn't kill the run
            print(f"[sources] {module.__name__}/{token} failed: {e}")
    return jobs

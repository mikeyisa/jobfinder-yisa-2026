"""ToS-friendly, public, no-auth job sources only. NEVER LinkedIn or Indeed —
automating those risks the candidate's own accounts."""
from . import greenhouse, lever

# (source_module, company_token) — all verified live. Two lanes:
# mainstream/junior-friendly (often Texas/in-geo + remote) AND the defense niche.
SEED_BOARDS = [
    # --- mainstream SWE, lots of junior/mid + in-geo/remote roles ---
    (greenhouse, "samsara"),        # IoT/cloud — big, many US roles
    (greenhouse, "gusto"),          # fintech/HR — junior-friendly
    (greenhouse, "robinhood"),      # fintech
    (greenhouse, "affirm"),         # fintech — mostly remote US
    (greenhouse, "coinbase"),       # remote US heavy
    (greenhouse, "dropbox"),        # remote US heavy
    (greenhouse, "twilio"),         # cloud/comms
    (greenhouse, "gitlab"),         # all-remote
    (greenhouse, "datadog"),        # cloud/observability
    (greenhouse, "airtable"),
    (greenhouse, "databricks"),     # data / cloud / AI
    # --- the clearance / defense / govtech niche (bonus lane) ---
    (greenhouse, "scaleai"),        # AI, incl. defense arm
    (greenhouse, "vannevarlabs"),   # national-security / defense AI
    (greenhouse, "primerai"),       # defense / govtech NLP
    (lever, "palantir"),            # defense / govtech
]


def fetch_all() -> list[dict]:
    jobs: list[dict] = []
    for module, token in SEED_BOARDS:
        try:
            jobs.extend(module.fetch(token))
        except Exception as e:  # one bad board shouldn't kill the run
            print(f"[sources] {module.__name__}/{token} failed: {e}")
    return jobs

# JobFinder — Yisa 2026

Your first real agentic AI project: it discovers **niche, high-fit** roles
(cleared-track AI/cloud SWE in defense & govtech), scores each against your
resume with Claude, reshapes your resume per job, and drafts a cold outreach
**email** — outputs to a dedicated application inbox. **No LinkedIn/Indeed
automation** — only ToS-friendly public job APIs, so nothing risks your accounts.

## Architecture (the agentic brain)
```
api/
  sources/        greenhouse.py, lever.py   # public, no-auth job APIs
  agents/         scorer · resume_shaper · outreach   # one Claude agent each
  llm.py          Claude wrapper (prompt-caches your resume on every call)
  pipeline.py     ingest -> heuristic pre-filter -> Claude score
  main.py         FastAPI: JSON API + serves the UI
web/index.html    unique single-page dashboard
```
Each agent has its own JSON schema (structured output) and system prompt —
edit `agents/*.py` and watch behavior change. That's how you learn orchestration.

## Run it (local, fastest)
```bash
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# optional but recommended — real Claude scoring:
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn main:app --reload --port 8000
```
Open http://localhost:8000 → click **Run pipeline**. Without a key it runs in
heuristic mode so you can see the flow; add the key for real scoring/tailoring.

## Run it (Docker — Postgres + API, closest to AWS)
```bash
cp .env.example .env   # paste your ANTHROPIC_API_KEY
docker compose up --build
```
Open http://localhost:8000.

## Cost control
- Only the top `SCORE_TOP_N` (default 15) pre-filtered jobs hit Claude.
- Your resume is prompt-cached, so repeated scoring is ~0.1x on those tokens.
- Set `MODEL=claude-sonnet-4-6` to cut cost ~70% on high-volume runs.

## Your job-hunt setup
1. Create a dedicated inbox (e.g. `michael.apply.2026@gmail.com`); set
   `APPLICATION_EMAIL`. Outreach drafts are addressed from it.
2. Keep your resume `.docx` in `data/resume/` (already copied).

## Roadmap
Gmail organizer agent · ClearanceJobs + company-page watchers · cheap AWS
(small EC2/Lightsail, Dockerized) · multi-user so Udoh can use it (add `user_id`
+ scope queries — the schema is already history-first).

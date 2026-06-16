"""FastAPI app: JSON API + serves the single-page UI. One container does both,
which keeps the prototype simple and cheap to run on a tiny AWS box."""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

import config
import geo
import llm
import pipeline
from db import init_db, get_db
from models import Job, Score, TailoredResume, Outreach, StyleNote
from resume_parser import resume_text
from agents import resume_shaper, outreach as outreach_agent, email_organizer

app = FastAPI(title="JobFinder — Yisa 2026")


@app.on_event("startup")
def _startup():
    init_db()


# ---- status / profile -------------------------------------------------------
@app.get("/api/status")
def status():
    return {
        "candidate": config.CANDIDATE_NAME,
        "model": config.MODEL,
        "claude_key": llm.have_key(),
        "application_email": config.APPLICATION_EMAIL,
        "resume_loaded": bool(resume_text().strip()),
    }


# ---- pipeline ---------------------------------------------------------------
@app.post("/api/ingest")
def api_ingest(db: Session = Depends(get_db)):
    return {"ingested": pipeline.ingest(db)}


@app.post("/api/score")
def api_score(db: Session = Depends(get_db)):
    return {"scored": pipeline.score_top(db)}


@app.post("/api/run")
def api_run(db: Session = Depends(get_db)):
    """Ingest + score in one call — what the UI's 'Run' button hits."""
    return pipeline.run(db)


# ---- jobs -------------------------------------------------------------------
def _job_dict(job: Job) -> dict:
    s = job.score
    loc_score, proximity = geo.proximity(job.location or "")
    return {
        "id": job.id, "source": job.source, "company": job.company,
        "title": job.title, "location": job.location, "url": job.url,
        "location_score": loc_score, "proximity": proximity,
        "prefilter_score": job.prefilter_score, "too_senior": job.too_senior,
        "score": None if not s else {
            "fit_score": s.fit_score, "recommend": s.recommend,
            "clearance_signal": s.clearance_signal,
            "seniority_match": s.seniority_match,
            "reasons": s.reasons, "gaps": s.gaps, "summary": s.summary,
        },
        "has_tailored": bool(job.tailored),
        "has_outreach": bool(job.outreach),
    }


@app.get("/api/jobs")
def api_jobs(scored_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(Job)
    if scored_only:
        q = q.join(Score)
    jobs = q.all()

    def rank(j):
        fit = j.score.fit_score if j.score else -1
        loc = geo.proximity(j.location or "")[0]
        rec = j.score.recommend if j.score else False
        blended = fit * 0.62 + loc * 0.38          # fit-led, but proximity matters
        return (not rec, -blended)                  # recommended first, then blended
    jobs.sort(key=rank)
    return [_job_dict(j) for j in jobs]


@app.get("/api/jobs/{job_id}")
def api_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "job not found")
    d = _job_dict(job)
    d["description"] = job.description
    if job.tailored:
        t = job.tailored[-1]
        d["tailored"] = {"headline": t.headline, "summary": t.summary,
                         "bullets": t.bullets, "keywords": t.keywords}
    if job.outreach:
        o = job.outreach[-1]
        d["outreach"] = {"contact_target": o.contact_target, "channel": o.channel,
                         "subject": o.subject, "message": o.message}
    return d


class FeedbackIn(BaseModel):
    feedback: str = ""   # a tweak the shaper should learn, e.g. "shorter bullets"


def _notes(db: Session, scope: str) -> str:
    rows = db.query(StyleNote).filter_by(scope=scope).order_by(StyleNote.created_at).all()
    return "\n".join(f"- {r.note}" for r in rows)


@app.get("/api/notes")
def api_notes(scope: str = "resume", db: Session = Depends(get_db)):
    rows = db.query(StyleNote).filter_by(scope=scope).order_by(StyleNote.created_at).all()
    return [{"id": r.note and r.id, "note": r.note} for r in rows]


@app.post("/api/jobs/{job_id}/tailor")
def api_tailor(job_id: int, body: FeedbackIn = FeedbackIn(), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "job not found")
    if body.feedback.strip():   # learn from this tweak for all future tailoring
        db.add(StyleNote(scope="resume", note=body.feedback.strip())); db.commit()
    r = resume_shaper.shape({"company": job.company, "title": job.title,
                             "description": job.description},
                            style_notes=_notes(db, "resume"))
    db.add(TailoredResume(job_id=job.id, headline=r["headline"], summary=r["summary"],
                          bullets=r["bullets"], keywords=r["keywords"], model=config.MODEL))
    db.commit()
    return r


@app.post("/api/jobs/{job_id}/outreach")
def api_outreach(job_id: int, body: FeedbackIn = FeedbackIn(), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "job not found")
    if body.feedback.strip():
        db.add(StyleNote(scope="outreach", note=body.feedback.strip())); db.commit()
    r = outreach_agent.draft({"company": job.company, "title": job.title,
                              "description": job.description},
                             style_notes=_notes(db, "outreach"))
    db.add(Outreach(job_id=job.id, contact_target=r["contact_target"],
                    channel="email", subject=r["subject"], message=r["message"],
                    model=config.MODEL))
    db.commit()
    return r


# ---- email organizer (roadmap: draft-only, paste an email) ------------------
class EmailIn(BaseModel):
    text: str


@app.post("/api/email/organize")
def api_email(body: EmailIn):
    if not body.text.strip():
        raise HTTPException(400, "empty email")
    return email_organizer.organize(body.text)


# ---- UI (served last so /api/* wins) ---------------------------------------
@app.get("/")
def index():
    return FileResponse(config.WEB_DIR / "index.html")


if (config.WEB_DIR).exists():
    app.mount("/static", StaticFiles(directory=config.WEB_DIR), name="static")

"""Orchestrates the agentic pipeline: ingest -> heuristic pre-filter -> Claude
score. Tailoring + outreach run on demand (per job) to control cost."""
from sqlalchemy.orm import Session

import config
from models import Job, Score, Run
import sources
from agents import scorer


def _prefilter(job: dict) -> tuple[float, bool]:
    """Cheap keyword score + seniority flag — keeps Claude calls to the top N."""
    text = (job["title"] + " " + job["description"]).lower()
    title = job["title"].lower()
    score = sum(1 for k in config.NICHE_KEYWORDS if k in text)
    # weight title matches heavier
    score += sum(2 for k in config.NICHE_KEYWORDS if k in title)
    too_senior = any(f in title for f in config.SENIOR_FLAGS)
    return float(score), too_senior


def ingest(db: Session) -> int:
    """Fetch all sources, normalize, dedupe, store. Returns new-job count."""
    raw = sources.fetch_all()
    new = 0
    for j in raw:
        if not j.get("url") or not j.get("title"):
            continue
        exists = db.query(Job).filter_by(source=j["source"], company=j["company"],
                                         url=j["url"]).first()
        if exists:
            continue
        pf, senior = _prefilter(j)
        db.add(Job(prefilter_score=pf, too_senior=senior, **j))
        new += 1
    db.commit()
    return new


def score_top(db: Session, top_n: int | None = None) -> int:
    """Score the highest pre-filtered, not-yet-scored jobs with Claude."""
    top_n = top_n or config.SCORE_TOP_N
    pending = (db.query(Job)
               .outerjoin(Score)
               .filter(Score.id.is_(None))
               .order_by(Job.too_senior.asc(), Job.prefilter_score.desc())
               .limit(top_n).all())
    done = 0
    for job in pending:
        result = scorer.score({
            "company": job.company, "title": job.title, "location": job.location,
            "description": job.description, "prefilter_score": job.prefilter_score,
            "too_senior": job.too_senior,
        })
        db.add(Score(
            job_id=job.id,
            fit_score=int(result.get("fit_score", 0)),
            recommend=bool(result.get("recommend", False)),
            clearance_signal=result.get("clearance_signal", "none"),
            seniority_match=result.get("seniority_match", "good"),
            reasons=result.get("reasons", []),
            gaps=result.get("gaps", []),
            summary=result.get("summary", ""),
            model=config.MODEL,
        ))
        done += 1
    db.commit()
    return done


def run(db: Session) -> dict:
    ingested = ingest(db)
    scored = score_top(db)
    r = Run(ingested=ingested, scored=scored,
            note=f"model={config.MODEL} key={'yes' if __import__('llm').have_key() else 'no'}")
    db.add(r)
    db.commit()
    return {"ingested": ingested, "scored": scored, "run_id": r.id}

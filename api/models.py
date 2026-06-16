"""History is first-class: every job, score, tailored resume and outreach draft
is persisted so nothing is lost and Udoh-style multi-user is an easy next step
(add a user_id column + scope queries)."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from db import Base


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    source = Column(String, index=True)          # greenhouse | lever
    company = Column(String, index=True)
    title = Column(String)
    location = Column(String)
    url = Column(String)
    description = Column(Text)                    # plain-text JD
    prefilter_score = Column(Float, default=0.0)  # cheap heuristic
    too_senior = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("source", "company", "url", name="uq_job"),)

    score = relationship("Score", uselist=False, back_populates="job",
                         cascade="all, delete-orphan")
    tailored = relationship("TailoredResume", back_populates="job",
                            cascade="all, delete-orphan")
    outreach = relationship("Outreach", back_populates="job",
                            cascade="all, delete-orphan")


class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), unique=True)
    fit_score = Column(Integer, default=0)        # 0-100
    recommend = Column(Boolean, default=False)
    clearance_signal = Column(String)             # none | eligible_ok | active_required
    seniority_match = Column(String)              # good | too_junior | too_senior
    reasons = Column(JSON)                        # list[str]
    gaps = Column(JSON)                           # list[str]
    summary = Column(Text)
    model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    job = relationship("Job", back_populates="score")


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    headline = Column(String)
    summary = Column(Text)
    bullets = Column(JSON)                         # list[str]
    keywords = Column(JSON)                         # list[str] ATS terms
    model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    job = relationship("Job", back_populates="tailored")


class Outreach(Base):
    __tablename__ = "outreach"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    contact_target = Column(String)                # role to find (e.g. "Eng Manager")
    channel = Column(String)                       # "email" — never LinkedIn
    subject = Column(String)
    message = Column(Text)
    model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    job = relationship("Job", back_populates="outreach")


class StyleNote(Base):
    """The shaper's memory. Every tweak the user gives ('shorter bullets', 'less
    buzzwordy', 'lead with AWS') is stored and fed into future tailoring/outreach
    so the agent keeps learning the candidate's voice."""
    __tablename__ = "style_notes"
    id = Column(Integer, primary_key=True)
    scope = Column(String, index=True)            # resume | outreach
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    ingested = Column(Integer, default=0)
    scored = Column(Integer, default=0)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

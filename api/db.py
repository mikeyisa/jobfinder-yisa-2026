"""SQLAlchemy engine/session. SQLite locally, Postgres in Docker — same models."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    import models  # noqa: F401  (register tables)
    Base.metadata.create_all(bind=engine)
    # best-effort migration for the posted_at column on pre-existing DBs
    from sqlalchemy import text
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN posted_at TIMESTAMP"))
        except Exception:
            pass  # already exists


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

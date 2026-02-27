"""
EnerScopeAI — Database Layer
SQLAlchemy models + session management for storing analysis results.
Supabase PostgreSQL is supported via SUPABASE_URL.
"""

import os
import logging
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine, Column, Integer, Float, String,
    DateTime, Text, Boolean
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# Build the connection URL from separate components to safely handle
# special characters in the password (e.g. @ $ in "Heli0$cope@i")
def _build_db_url() -> str | None:
    # Supabase-first for deployable production backend
    supabase_url = os.getenv("SUPABASE_URL", "")
    if supabase_url:
        return supabase_url

    # Accept a full URL override (raw string, not URL-parsed by us)
    raw_url = os.getenv("DATABASE_URL", "")
    if raw_url:
        return raw_url

    # Build from individual env vars (safest for special-char passwords)
    from sqlalchemy.engine import URL as SAUrl
    return SAUrl.create(
        drivername="postgresql+psycopg",
        username=os.getenv("POSTGRES_USER", "enerscope"),
        password=os.getenv("POSTGRES_PASSWORD", "Ener$cope@i"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "enerscope"),
    )

# ── Engine ────────────────────────────────────────────────────────────────────
engine = None
SessionLocal = None


def init_db():
    """Initialise the database engine and create tables."""
    global engine, SessionLocal
    try:
        db_url = _build_db_url()
        engine = create_engine(
            db_url,
            pool_pre_ping=False,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 3},  # 3-second timeout for quick failure
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database connected and tables created.")
        return True
    except OperationalError as e:
        logger.warning(f"⚠️  Database unavailable — running in stateless mode. ({e})")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Database connection failed — running in stateless mode. ({e})")
        return False


def get_db():
    """FastAPI dependency — yields a DB session, or None if DB is unavailable."""
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Models ────────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class AnalysisResult(Base):
    """Stores each placement analysis run."""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Location
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    # Panel config
    panel_area = Column(Float, default=100.0)
    efficiency = Column(Float, default=0.18)

    # Climate data
    solar_irradiance = Column(Float)
    wind_speed = Column(Float)
    elevation = Column(Float)

    # Scores
    score = Column(Integer)
    grade = Column(String(4))
    solar_score = Column(Float)
    wind_score = Column(Float)
    elevation_score = Column(Float)
    recommendation = Column(Text)

    # ROI
    energy_output_kwh_per_year = Column(Float)
    annual_savings_inr = Column(Float)
    payback_years = Column(Float)
    lifetime_profit_inr = Column(Float)

    # AI summary
    ai_summary = Column(Text)
    ai_provider = Column(String(50))


class SavedLocation(Base):
    """User-saved locations for future reference."""
    __tablename__ = "saved_locations"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    name = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    last_score = Column(Integer)
    notes = Column(Text)
    is_favourite = Column(Boolean, default=False)


# ── CRUD helpers ──────────────────────────────────────────────────────────────
def save_analysis(db: Session, data: dict) -> AnalysisResult | None:
    """Persist an analysis result. Returns None if DB is unavailable."""
    if db is None:
        return None
    try:
        record = AnalysisResult(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save analysis: {e}")
        return None


def get_recent_analyses(db: Session, limit: int = 20) -> list[AnalysisResult]:
    """Fetch the most recent analyses ordered by creation time."""
    if db is None:
        return []
    return (
        db.query(AnalysisResult)
        .order_by(AnalysisResult.created_at.desc())
        .limit(limit)
        .all()
    )

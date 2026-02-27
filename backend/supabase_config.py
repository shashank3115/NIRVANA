"""
EnerScopeAI — Supabase Database Configuration
==============================================
Fully managed PostgreSQL backend with Supabase for production deployment.
Handles connection pooling, migrations, and secure credential management.
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# SUPABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


def get_supabase_url() -> str:
    """
    Get Supabase PostgreSQL connection URL.
    
    Format: postgresql://[user]:[password]@[host]:[port]/[database]
    
    Set via environment variable:
    SUPABASE_URL=postgresql://postgres.abc:password@db.supabase.co:5432/postgres
    """
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise ValueError(
            "SUPABASE_URL environment variable not set. "
            "Get it from: https://app.supabase.com → Project Settings → Database"
        )
    return url


def get_database_url() -> str:
    """
    Get database URL with fallback to Supabase or SQLite.
    
    Priority:
    1. SUPABASE_URL (production)
    2. DATABASE_URL (custom PostgreSQL)
    3. SQLite (development fallback, no persistence)
    """
    # Try Supabase first
    if os.getenv("SUPABASE_URL"):
        return get_supabase_url()
    
    # Try custom PostgreSQL
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    # Development fallback
    logger.warning(
        "No SUPABASE_URL or DATABASE_URL set. "
        "Using SQLite in-memory database (not persistent). "
        "Set SUPABASE_URL for production deployment."
    )
    return "sqlite:///:memory:"


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE ENGINE & SESSION FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

database_url = get_database_url()
is_supabase = "postgresql" in database_url
is_postgres = "postgresql" in database_url or "postgres" in database_url

logger.info(f"Database Type: {'Supabase (PostgreSQL)' if is_supabase else 'PostgreSQL' if is_postgres else 'SQLite'}")
logger.info(f"Database URL: {database_url.split('@')[0]}...{database_url.split('/')[-1] if '/' in database_url else ''}")

# Create engine with connection pooling (optimized for Supabase)
engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=20,                    # Connection pool size
    max_overflow=0,                  # Don't create extra connections beyond pool_size
    pool_pre_ping=True,             # Verify connections before use
    pool_recycle=3600,              # Recycle connections every hour
    echo=False,                      # Set to True for SQL logging
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30 second query timeout
    } if is_postgres else {},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE INITIALIZATION & MIGRATIONS
# ═══════════════════════════════════════════════════════════════════════════════


async def init_db():
    """Initialize database and create tables."""
    try:
        logger.info("Initializing database...")
        
        # Import models to register them with Base
        from models import Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✓ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        return False


async def verify_connection() -> bool:
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection verified")
            return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def get_db() -> Session:
    """
    Get database session for dependency injection in FastAPI.
    
    Usage:
        @app.get("/endpoint")
        async def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Get database session as context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# SUPABASE-SPECIFIC UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


def create_supabase_tables():
    """
    Create essential tables for EnerScopeAI in Supabase.
    Intentionally minimal - let application handle relationships.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    location_lat FLOAT NOT NULL,
                    location_lng FLOAT NOT NULL,
                    analysis_type VARCHAR(50),  -- 'solar', 'wind', 'hydro', 'multi'
                    results JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            conn.commit()
            logger.info("✓ Supabase tables created")
            
    except Exception as e:
        logger.warning(f"Could not create Supabase tables: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# SUPABASE CLIENT (Optional: for direct access beyond SQLAlchemy)
# ═══════════════════════════════════════════════════════════════════════════════


def get_supabase_client():
    """
    Get Supabase Python client for direct database operations.
    Requires: pip install supabase
    
    Usage:
        from supabase_config import get_supabase_client
        supabase = get_supabase_client()
        data = supabase.table('analyses').select('*').execute()
    """
    try:
        import supabase
        url = os.getenv("SUPABASE_URL_PUBLIC")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            logger.warning("Supabase client credentials not configured")
            return None
        
        client = supabase.create_client(url, key)
        return client
        
    except ImportError:
        logger.info("Supabase client not installed. Install with: pip install supabase")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════


async def health_check() -> dict:
    """
    Perform database health check.
    
    Returns:
        dict with 'status' (healthy/degraded), 'message', 'response_time_ms'
    """
    import time
    
    try:
        start = time.time()
        is_connected = await verify_connection()
        elapsed = (time.time() - start) * 1000
        
        return {
            "status": "healthy" if is_connected else "degraded",
            "type": "supabase" if is_supabase else "postgres" if is_postgres else "sqlite",
            "response_time_ms": round(elapsed, 2),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }

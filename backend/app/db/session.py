"""Database engine, session factory and the FastAPI session dependency."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Iterator[Session]:
    """Yield a database session and guarantee it is closed.

    Used as a FastAPI dependency: ``db: Session = Depends(get_db)``.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

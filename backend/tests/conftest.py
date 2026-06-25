"""Pytest fixtures: an isolated in-memory SQLite app, no Postgres required."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.interview.llm import get_llm
from app.main import app  # importing the app also registers all ORM models
from tests.fakes import FakeLLM


@pytest.fixture
def db_session() -> Iterator[Session]:
    """A fresh in-memory database per test, torn down afterwards."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """A TestClient whose get_db dependency points at the test session."""

    def _override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_llm] = lambda: FakeLLM()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

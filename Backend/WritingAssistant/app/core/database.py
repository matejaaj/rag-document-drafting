import os
from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import create_engine, event, orm
from sqlalchemy.orm import Session

from app.model import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./writing_assistant.db")


def _enable_foreign_keys(dbapi_connection, connection_record) -> None:
    """SQLite enforces foreign keys only when enabled per connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Database:
    def __init__(self, db_url: str = DATABASE_URL) -> None:
        self._engine = create_engine(db_url, echo=False)
        event.listen(self._engine, "connect", _enable_foreign_keys)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            )
        )

    def create_tables(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Generator[Session, Any, None]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

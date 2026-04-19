import os
from pathlib import Path

from sqlmodel import Session, create_engine

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE_PATH = BASE_DIR / "data" / "database.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def _ensure_sqlite_directory(database_url: str) -> None:
    sqlite_prefix = "sqlite:///"
    if not database_url.startswith(sqlite_prefix):
        return

    raw_path = database_url.removeprefix(sqlite_prefix)
    if raw_path in {":memory:", ""}:
        return

    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = (BASE_DIR / db_path).resolve()

    db_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_directory(DATABASE_URL)
engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session

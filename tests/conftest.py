from pathlib import Path

import pytest

from databank import Database, QueryCollection

MEMBERS = [{"member": "John"}, {"member": "Paul"}, {"member": "George"}, {"member": "Ringo"}]
CREATE_TABLE = "CREATE TABLE beatles (id INTEGER PRIMARY KEY, member TEXT NOT NULL);"
INSERT = "INSERT INTO beatles (member) VALUES (:member);"


@pytest.fixture
def database(tmp_path: Path):
    # file-based database, so that every session gets its own connection from the pool
    db = Database(f"sqlite:///{tmp_path / 'test.db'}")
    db.execute(CREATE_TABLE)
    db.execute_many(INSERT, params=MEMBERS)
    yield db
    db.close()


@pytest.fixture
def queries() -> QueryCollection:
    return QueryCollection.from_file(Path(__file__).parent / "queries.sql")

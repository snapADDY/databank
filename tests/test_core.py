from pathlib import Path
from threading import Thread

import pytest

from databank import Database, QueryCollection


@pytest.fixture
def database():
    db = Database("sqlite://")

    db.execute("CREATE TABLE beatles (id INTEGER PRIMARY KEY, member TEXT NOT NULL);")

    params = [{"member": "John"}, {"member": "Paul"}, {"member": "George"}, {"member": "Ringo"}]
    db.execute_many("INSERT INTO beatles (member) VALUES (:member);", params=params)
    yield db


@pytest.fixture
def queries() -> QueryCollection:
    filepath = Path(__file__).parent / "queries.sql"
    return QueryCollection.from_file(filepath)


def test_execute(database: Database):
    params = {"member": "Klaus"}
    database.execute("INSERT INTO beatles (member) VALUES (:member);", params=params)
    assert len(database.fetch_all("SELECT * FROM beatles;")) == 5


def test_execute_many(database: Database):
    params = [{"member": "Klaus"}, {"member": "Yoko"}]
    database.execute_many("INSERT INTO beatles (member) VALUES (:member);", params=params)
    assert len(database.fetch_all("SELECT * FROM beatles;")) == 6


def test_fetch_one(database: Database):
    assert database.fetch_one("SELECT * FROM beatles ORDER BY id;")["member"] == "John"


def test_fetch_many(database: Database):
    assert len(database.fetch_many("SELECT * FROM beatles;", n=2)) == 2


def test_fetch_all(database: Database):
    assert len(database.fetch_all("SELECT * FROM beatles;")) == 4


def test_fetch_all_from_query_collection(database: Database, queries: QueryCollection):
    assert len(database.fetch_all(queries["select_all_data"])) == 4

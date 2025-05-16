from pathlib import Path

import pytest
import pytest_asyncio

from databank import AsyncDatabase, Database, QueryCollection


@pytest.fixture
def database():
    db = Database("sqlite://")

    db.execute("CREATE TABLE beatles (id INTEGER PRIMARY KEY, member TEXT NOT NULL);")

    params = [{"member": "John"}, {"member": "Paul"}, {"member": "George"}, {"member": "Ringo"}]
    db.execute_many("INSERT INTO beatles (member) VALUES (:member);", params=params)
    yield db


@pytest_asyncio.fixture
async def async_database():
    db = AsyncDatabase("sqlite+aiosqlite://")

    await db.aexecute("CREATE TABLE beatles (id INTEGER PRIMARY KEY, member TEXT NOT NULL);")

    params = [{"member": "John"}, {"member": "Paul"}, {"member": "George"}, {"member": "Ringo"}]
    await db.aexecute_many("INSERT INTO beatles (member) VALUES (:member);", params=params)
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


@pytest.mark.asyncio
async def test_aexecute(async_database: AsyncDatabase):
    params = {"member": "Klaus"}
    await async_database.aexecute("INSERT INTO beatles (member) VALUES (:member);", params=params)
    result = await async_database.afetch_all("SELECT * FROM beatles;")
    assert len(result) == 5


@pytest.mark.asyncio
async def test_aexecute_many(async_database: AsyncDatabase):
    params = [{"member": "Klaus"}, {"member": "Yoko"}]
    await async_database.aexecute_many(
        "INSERT INTO beatles (member) VALUES (:member);", params=params
    )
    result = await async_database.afetch_all("SELECT * FROM beatles;")
    assert len(result) == 6


@pytest.mark.asyncio
async def test_afetch_one(async_database: AsyncDatabase):
    result = await async_database.afetch_one("SELECT * FROM beatles ORDER BY id;")
    assert result["member"] == "John"


@pytest.mark.asyncio
async def test_afetch_many(async_database: AsyncDatabase):
    results = await async_database.afetch_many("SELECT * FROM beatles;", n=2)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_afetch_all(async_database: AsyncDatabase):
    results = await async_database.afetch_all("SELECT * FROM beatles;")
    assert len(results) == 4


@pytest.mark.asyncio
async def test_afetch_all_from_query_collection(
    async_database: AsyncDatabase,
    queries: QueryCollection,
):
    assert len(await async_database.afetch_all(queries["select_all_data"])) == 4

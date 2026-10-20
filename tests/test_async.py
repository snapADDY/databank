import asyncio
from pathlib import Path

import pytest
import pytest_asyncio

pytest.importorskip("greenlet", reason="requires the asyncio extra")
pytest.importorskip("aiosqlite")

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from databank import AsyncDatabase, QueryCollection
from tests.conftest import CREATE_TABLE, INSERT, MEMBERS


@pytest_asyncio.fixture
async def async_database(tmp_path: Path):
    db = AsyncDatabase(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    await db.aexecute(CREATE_TABLE)
    await db.aexecute_many(INSERT, params=MEMBERS)
    yield db
    await db.aclose()


async def acount(database: AsyncDatabase) -> int:
    return (await database.afetch_one("SELECT COUNT(*) AS n FROM beatles;"))["n"]


@pytest.mark.asyncio
async def test_aexecute(async_database: AsyncDatabase):
    await async_database.aexecute(INSERT, params={"member": "Klaus"})
    assert await acount(async_database) == 5


@pytest.mark.asyncio
async def test_aexecute_many(async_database: AsyncDatabase):
    await async_database.aexecute_many(INSERT, params=[{"member": "Klaus"}, {"member": "Yoko"}])
    assert await acount(async_database) == 6


@pytest.mark.asyncio
async def test_aexecute_rolls_back_on_error(async_database: AsyncDatabase):
    with pytest.raises(IntegrityError):
        await async_database.aexecute_many(INSERT, params=[{"member": "Klaus"}, {"member": None}])
    assert await acount(async_database) == 4


@pytest.mark.asyncio
async def test_afetch_one(async_database: AsyncDatabase):
    result = await async_database.afetch_one("SELECT * FROM beatles ORDER BY id;")
    assert result == {"id": 1, "member": "John"}


@pytest.mark.asyncio
async def test_afetch_one_without_result(async_database: AsyncDatabase):
    assert await async_database.afetch_one("SELECT * FROM beatles WHERE id = -1;") == {}


@pytest.mark.asyncio
async def test_afetch_many(async_database: AsyncDatabase):
    results = await async_database.afetch_many("SELECT * FROM beatles ORDER BY id;", n=2)
    assert [r["member"] for r in results] == ["John", "Paul"]


@pytest.mark.asyncio
async def test_afetch_all(async_database: AsyncDatabase):
    results = await async_database.afetch_all("SELECT * FROM beatles;")
    assert len(results) == 4


@pytest.mark.asyncio
async def test_afetch_all_without_result(async_database: AsyncDatabase):
    assert await async_database.afetch_all("SELECT * FROM beatles WHERE id = -1;") == []


@pytest.mark.asyncio
async def test_afetch_all_from_query_collection(
    async_database: AsyncDatabase,
    queries: QueryCollection,
):
    assert len(await async_database.afetch_all(queries["select_all_data"])) == 4
    result = await async_database.afetch_all(queries["select_record_by_id"], params={"id": 2})
    assert result == [{"id": 2, "member": "Paul"}]


@pytest.mark.asyncio
async def test_acreate_session_rolls_back_on_error(async_database: AsyncDatabase):
    with pytest.raises(RuntimeError):
        async with async_database.acreate_session() as session:
            await session.execute(text(INSERT), params={"member": "Klaus"})
            raise RuntimeError
    assert await acount(async_database) == 4


@pytest.mark.asyncio
async def test_nested_sessions_commit_once(async_database: AsyncDatabase):
    async with async_database.acreate_session():
        await async_database.aexecute(INSERT, params={"member": "Klaus"})
        assert await acount(async_database) == 5
    assert await acount(async_database) == 5


@pytest.mark.asyncio
async def test_other_tasks_get_own_session(async_database: AsyncDatabase):
    async def get_session():
        async with async_database.acreate_session() as session:
            return session

    async with async_database.acreate_session() as outer:
        inner = await asyncio.create_task(get_session())
    assert inner is not outer


@pytest.mark.asyncio
async def test_concurrent_usage(async_database: AsyncDatabase):
    query = "SELECT * FROM beatles;"
    async with async_database.acreate_session():
        # concurrent tasks must not share the (non-concurrency-safe) session
        results = await asyncio.gather(*(async_database.afetch_all(query) for _ in range(10)))
    assert all(len(result) == 4 for result in results)


@pytest.mark.asyncio
async def test_independent_databases(tmp_path: Path, async_database: AsyncDatabase):
    other = AsyncDatabase(f"sqlite+aiosqlite:///{tmp_path / 'other.db'}")
    try:
        async with async_database.acreate_session() as first, other.acreate_session() as second:
            assert first is not second
    finally:
        await other.aclose()

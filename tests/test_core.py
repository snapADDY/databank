import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from databank import Database, QueryCollection
from tests.conftest import INSERT


def count(database: Database) -> int:
    return database.fetch_one("SELECT COUNT(*) AS n FROM beatles;")["n"]


def test_execute(database: Database):
    database.execute(INSERT, params={"member": "Klaus"})
    assert count(database) == 5


def test_execute_many(database: Database):
    database.execute_many(INSERT, params=[{"member": "Klaus"}, {"member": "Yoko"}])
    assert count(database) == 6


def test_execute_rolls_back_on_error(database: Database):
    with pytest.raises(IntegrityError):
        database.execute_many(INSERT, params=[{"member": "Klaus"}, {"member": None}])
    assert count(database) == 4


def test_params_are_keyword_only(database: Database):
    with pytest.raises(TypeError):
        database.execute(INSERT, {"member": "Klaus"})  # type: ignore[misc]


def test_fetch_one(database: Database):
    assert database.fetch_one("SELECT * FROM beatles ORDER BY id;") == {"id": 1, "member": "John"}


def test_fetch_one_with_params(database: Database):
    result = database.fetch_one("SELECT member FROM beatles WHERE id = :id;", params={"id": 4})
    assert result == {"member": "Ringo"}


def test_fetch_one_without_result(database: Database):
    assert database.fetch_one("SELECT * FROM beatles WHERE id = -1;") == {}


def test_fetch_many(database: Database):
    results = database.fetch_many("SELECT * FROM beatles ORDER BY id;", n=2)
    assert [r["member"] for r in results] == ["John", "Paul"]


def test_fetch_many_default_n(database: Database):
    assert len(database.fetch_many("SELECT * FROM beatles;")) == 1


def test_fetch_many_more_than_available(database: Database):
    assert len(database.fetch_many("SELECT * FROM beatles;", n=10)) == 4


def test_fetch_all(database: Database):
    results = database.fetch_all("SELECT * FROM beatles ORDER BY id;")
    assert [r["member"] for r in results] == ["John", "Paul", "George", "Ringo"]


def test_fetch_all_without_result(database: Database):
    assert database.fetch_all("SELECT * FROM beatles WHERE id = -1;") == []


def test_fetch_all_from_query_collection(database: Database, queries: QueryCollection):
    assert len(database.fetch_all(queries["select_all_data"])) == 4
    result = database.fetch_all(queries["select_record_by_id"], params={"id": 2})
    assert result == [{"id": 2, "member": "Paul"}]


def test_create_session_commits(database: Database):
    with database.create_session() as session:
        session.execute(text(INSERT), params={"member": "Klaus"})
    assert count(database) == 5


def test_create_session_rolls_back_on_error(database: Database):
    with pytest.raises(RuntimeError), database.create_session() as session:
        session.execute(text(INSERT), params={"member": "Klaus"})
        raise RuntimeError
    assert count(database) == 4


def test_session_is_reset_after_error(database: Database):
    with pytest.raises(RuntimeError), database.create_session() as first:
        raise RuntimeError

    with database.create_session() as second:
        assert second is not first


def test_sessions_are_thread_local(database: Database):
    barrier = threading.Barrier(2)

    def get_session():
        with database.create_session() as session:
            # make sure both sessions are open at the same time
            barrier.wait(timeout=5)
            return session

    with ThreadPoolExecutor(max_workers=2) as executor:
        first, second = executor.map(lambda _: get_session(), range(2))

    assert first is not second


def test_multithreaded_usage(database: Database):
    def work(i: int) -> int:
        database.execute(INSERT, params={"member": f"Member {i}"})
        return len(database.fetch_all("SELECT * FROM beatles;"))

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(work, range(20)))

    assert count(database) == 24


def test_close(database: Database):
    database.close()
    # the engine reconnects on demand after being disposed
    assert count(database) == 4


def test_import_without_greenlet():
    # the sync API must work without the `asyncio` extra (i.e. without greenlet)
    code = (
        "import sys; sys.modules['greenlet'] = None\n"
        "from databank import AsyncDatabase, Database\n"
        "assert Database('sqlite://').fetch_one('SELECT 1 AS x') == {'x': 1}\n"
        "try:\n"
        "    AsyncDatabase('sqlite+aiosqlite://')\n"
        "except ImportError:\n"
        "    pass\n"
        "else:\n"
        "    raise AssertionError('expected ImportError')\n"
    )
    subprocess.run([sys.executable, "-c", code], check=True)  # noqa: S603

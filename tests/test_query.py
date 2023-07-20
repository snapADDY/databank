from pathlib import Path

import pytest

from databank.query import QueryCollection, is_valid_query_header


@pytest.fixture
def queries() -> QueryCollection:
    filepath = Path(__file__).parent / "queries.sql"
    return QueryCollection.from_file(filepath)


def test_query_collection(queries: QueryCollection):
    assert len(queries) == 2
    assert queries["insert_data"] == "INSERT INTO beatles (id, member) VALUES (:id, :member);"
    assert queries["select_all_data"] == "SELECT * FROM beatles;"

    with pytest.raises(KeyError):
        queries["invalid"]


def test_is_valid_query_header():
    assert is_valid_query_header("/* @name foo */")
    assert not is_valid_query_header("/* name: foo bar */")
    assert not is_valid_query_header("/** @name foo **/")
    assert not is_valid_query_header("/* @name foo bar */")
    assert not is_valid_query_header("-- @name: foo")

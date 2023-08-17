from pathlib import Path

import pytest

from databank.query import QueryCollection, is_valid_query_header


@pytest.fixture
def queries() -> QueryCollection:
    filepath = Path(__file__).parent / "queries.sql"
    return QueryCollection.from_file(filepath)


def test_query_collection(queries: QueryCollection):
    assert len(queries) == 3
    assert queries["insert_data"] == "INSERT INTO beatles (id, member) VALUES (:id, :member);"
    assert queries["select_all_data"] == "SELECT * FROM beatles;"
    assert queries["select_record_by_id"] == "SELECT * FROM beatles WHERE id = :id;"

    with pytest.raises(KeyError):
        queries["invalid"]


def test_is_valid_query_header():
    assert is_valid_query_header("/* @name foo */")
    assert not is_valid_query_header("/* name: foo bar */")
    assert not is_valid_query_header("/** @name foo **/")
    assert not is_valid_query_header("/* @name foo bar */")
    assert not is_valid_query_header("-- @name: foo")


def test_query_collection_mapping(queries: QueryCollection):
    assert hasattr(queries, "items")
    assert hasattr(queries, "keys")
    assert hasattr(queries, "values")

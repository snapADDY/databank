from pathlib import Path

import pytest

from databank.query import (
    InvalidQueryError,
    InvalidQueryHeaderError,
    QueryCollection,
    is_valid_query_header,
    parse_header,
)


def test_query_collection(queries: QueryCollection):
    assert len(queries) == 3
    assert queries["insert_data"] == "INSERT INTO beatles (id, member) VALUES (:id, :member);"
    assert queries["select_all_data"] == "SELECT * FROM beatles;"
    assert queries["select_record_by_id"] == "SELECT *\nFROM beatles\n\nWHERE id = :id;"

    with pytest.raises(KeyError, match="'invalid' is not a valid query name"):
        queries["invalid"]


def test_query_collection_mapping(queries: QueryCollection):
    assert list(queries) == ["insert_data", "select_all_data", "select_record_by_id"]
    assert "select_all_data" in queries
    assert "invalid" not in queries
    assert queries.get("invalid") is None
    assert dict(queries.items())["select_all_data"] == "SELECT * FROM beatles;"
    assert "3 queries" in repr(queries)


def test_query_collection_copies_input():
    source = {"foo": "SELECT 1;"}
    queries = QueryCollection(source)
    source["bar"] = "SELECT 2;"
    assert list(queries) == ["foo"]


def test_is_valid_query_header():
    assert is_valid_query_header("/* @name foo */")
    assert is_valid_query_header("/*\t@name\tfoo\t*/")
    assert is_valid_query_header("/* @name foo */  ")
    assert is_valid_query_header("/*@name foo*/")
    assert not is_valid_query_header("/* name: foo bar */")
    assert not is_valid_query_header("/** @name foo **/")
    assert not is_valid_query_header("/* @name foo bar */")
    assert not is_valid_query_header("/* @name */")
    assert not is_valid_query_header("-- @name: foo")


def test_parse_header():
    assert parse_header("/* @name foo */") == {"name": "foo"}
    assert parse_header("/*\t@name  foo_bar */ ") == {"name": "foo_bar"}
    with pytest.raises(InvalidQueryHeaderError):
        parse_header("/* @name foo bar */")


def test_from_string_blank_lines_in_query():
    queries = QueryCollection.from_string(
        "/* @name foo */\nSELECT *\n\nFROM foo;\n\n\n/* @name bar */\nSELECT 1;\n"
    )
    assert queries["foo"] == "SELECT *\n\nFROM foo;"
    assert queries["bar"] == "SELECT 1;"


def test_from_string_without_blank_line_between_queries():
    queries = QueryCollection.from_string("/* @name foo */\nSELECT 1;\n/* @name bar */\nSELECT 2;")
    assert dict(queries) == {"foo": "SELECT 1;", "bar": "SELECT 2;"}


def test_from_string_comments_before_first_query():
    sql = "-- comment\n/*\n multi-line\n comment\n*/\n\n/* @name foo */\nSELECT 1;"
    assert dict(QueryCollection.from_string(sql)) == {"foo": "SELECT 1;"}


def test_from_string_comments_in_query_are_kept():
    sql = "/* @name foo */\n-- explain this\nSELECT 1; /* inline */"
    assert QueryCollection.from_string(sql)["foo"] == "-- explain this\nSELECT 1; /* inline */"


def test_from_string_empty():
    assert len(QueryCollection.from_string("")) == 0
    assert len(QueryCollection.from_string("-- only a comment\n")) == 0


def test_from_string_query_without_header():
    with pytest.raises(InvalidQueryHeaderError):
        QueryCollection.from_string("SELECT 1;\n\n/* @name foo */\nSELECT 2;")


def test_from_string_invalid_header_between_queries():
    with pytest.raises(InvalidQueryHeaderError, match="foo bar"):
        QueryCollection.from_string("/* @name foo */\nSELECT 1;\n\n/* @name foo bar */\nSELECT 2;")


def test_from_string_empty_query():
    with pytest.raises(InvalidQueryError, match="'foo' is empty"):
        QueryCollection.from_string("/* @name foo */\n\n/* @name bar */\nSELECT 1;")


def test_from_string_duplicate_name():
    with pytest.raises(InvalidQueryError, match="'foo' is not unique"):
        QueryCollection.from_string("/* @name foo */\nSELECT 1;\n/* @name foo */\nSELECT 2;")


def test_from_file_accepts_str_and_uppercase_suffix(tmp_path: Path):
    filepath = tmp_path / "QUERIES.SQL"
    filepath.write_text("/* @name foo */\nSELECT 1;\n", encoding="utf-8")
    assert QueryCollection.from_file(str(filepath))["foo"] == "SELECT 1;"


def test_from_file_crlf_line_endings(tmp_path: Path):
    filepath = tmp_path / "queries.sql"
    filepath.write_bytes(b"/* @name foo */\r\nSELECT 1;\r\n\r\n/* @name bar */\r\nSELECT 2;\r\n")
    assert dict(QueryCollection.from_file(filepath)) == {"foo": "SELECT 1;", "bar": "SELECT 2;"}


def test_from_file_requires_sql_suffix(tmp_path: Path):
    filepath = tmp_path / "queries.txt"
    filepath.write_text("/* @name foo */\nSELECT 1;\n", encoding="utf-8")
    with pytest.raises(ValueError, match="is no SQL file"):
        QueryCollection.from_file(filepath)

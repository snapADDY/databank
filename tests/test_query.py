from pathlib import Path

import pytest

from databank import QueryCollection


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

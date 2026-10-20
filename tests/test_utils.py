import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.dialects import postgresql

from databank.utils import compile_sql, serialize_param, serialize_params

UUID_ = UUID("12345678-1234-5678-1234-567812345678")


@pytest.mark.parametrize(
    "value",
    [
        "1",
        1,
        1.0,
        True,
        b"bytes",
        (0, 1, 2),
        datetime(1970, 1, 1),
        date(1970, 1, 1),
        time(12, 30),
        timedelta(days=1),
        Decimal("1.5"),
        UUID_,
        None,
    ],
)
def test_serialize_param_passthrough(value):
    assert serialize_param(value) is value


def test_serialize_param_json():
    assert serialize_param({"a": 0}) == json.dumps({"a": 0})
    assert serialize_param([0]) == json.dumps([0])


def test_serialize_param_nested_json():
    value = {"date": date(1970, 1, 1), "id": UUID_, "amount": Decimal("1.5"), "list": [None]}
    assert json.loads(serialize_param(value)) == {
        "date": "1970-01-01",
        "id": str(UUID_),
        "amount": "1.5",
        "list": [None],
    }


@pytest.mark.parametrize("value", [object(), {1, 2}, {"a": object()}, [{1, 2}]])
def test_serialize_param_unsupported(value):
    with pytest.raises(ValueError, match="is not serializable"):
        serialize_param(value)


def test_serialize_param_psycopg_json():
    json_types = pytest.importorskip("psycopg.types.json")
    value = json_types.Jsonb({"a": 0})
    assert serialize_param(value) is value


def test_serialize_params():
    assert serialize_params({"member": "Ringo", "songs": ["Octopus's Garden"], "x": None}) == {
        "member": "Ringo",
        "songs": '["Octopus\'s Garden"]',
        "x": None,
    }


def test_compile_sql():
    expected = "SELECT * FROM foo WHERE bar = 1;"
    assert compile_sql("SELECT * FROM foo WHERE bar = :bar;", params={"bar": 1}) == expected


def test_compile_sql_without_params():
    assert compile_sql("SELECT 1;") == "SELECT 1;"


def test_compile_sql_ignores_unused_params():
    actual = compile_sql("SELECT * FROM foo WHERE bar = :bar;", params={"bar": 1, "baz": 2})
    assert actual == "SELECT * FROM foo WHERE bar = 1;"


def test_compile_sql_escapes_strings():
    actual = compile_sql("SELECT * FROM foo WHERE bar = :bar;", params={"bar": "x' OR '1'='1"})
    assert actual == "SELECT * FROM foo WHERE bar = 'x'' OR ''1''=''1';"


def test_compile_sql_with_dialect():
    actual = compile_sql(
        "SELECT * FROM foo WHERE bar = :bar;",
        params={"bar": datetime(1970, 1, 1)},
        dialect=postgresql.dialect(),
    )
    assert actual == "SELECT * FROM foo WHERE bar = '1970-01-01 00:00:00';"

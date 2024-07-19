import json
from datetime import date, datetime

from databank.utils import compile_sql, serialize_param


def test_serialize_param():
    assert serialize_param("1") == "1"
    assert serialize_param(1) == 1
    assert serialize_param(1.0) == 1.0
    assert serialize_param(True) is True
    assert serialize_param({"a": 0}) == json.dumps({"a": 0})
    assert serialize_param([0]) == json.dumps([0])
    assert serialize_param(datetime(1970, 1, 1)) == datetime(1970, 1, 1)
    assert serialize_param((0, 1, 2)) == (0, 1, 2)
    assert serialize_param(date(1970, 1, 1)) == date(1970, 1, 1)


def test_compile_sql():
    expected = "SELECT * FROM foo WHERE bar = 1;"
    actual = compile_sql("SELECT * FROM foo WHERE bar = :bar;", params={"bar": 1})
    assert actual == expected

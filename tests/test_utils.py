import json
from datetime import datetime

from databank.utils import serialize_param, serialize_params


def test_serialize_params():
    assert serialize_params(
        {
            "a": 0,
            "b": "1",
            "c": 1.0,
            "d": True,
            "e": datetime.now(),
            "f": [0, 1, 2],
            "e": {"a": 0, "b": 1},
        }
    ) == {"a": 0, "b": "1", "c": 1.0, "d": True, "e": '{"a": 0, "b": 1}', "f": "[0, 1, 2]"}


def test_serialize_param():
    assert serialize_param("1") == "1"
    assert serialize_param(1) == 1
    assert serialize_param(1.0) == 1.0
    assert serialize_param(True) == True
    assert serialize_param({"a": 0}) == json.dumps({"a": 0})
    assert serialize_param([0]) == json.dumps([0])
    assert serialize_param(datetime(1970, 1, 1)) == "1970-01-01T00:00:00"

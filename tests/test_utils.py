import json
from datetime import datetime

from databank.utils import serialize_param


def test_serialize_param():
    assert serialize_param("1") == "1"
    assert serialize_param(1) == 1
    assert serialize_param(1.0) == 1.0
    assert serialize_param(True) == True
    assert serialize_param({"a": 0}) == json.dumps({"a": 0})
    assert serialize_param([0]) == json.dumps([0])
    assert serialize_param(datetime(1970, 1, 1)) == datetime(1970, 1, 1)
    assert serialize_param((0, 1, 2)) == (0, 1, 2)

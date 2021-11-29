import json
from datetime import datetime
from typing import Any, Union


def serialize_values(values: dict[str, Any]) -> dict[str, Union[str, int, float, bool]]:
    """Serialize the values of the given dictionary.

    Parameters
    ----------
    values : dict[str, Any]
        tba.

    Returns
    -------
    dict[str, Union[str, int, float, bool]]
        tba.
    """
    return {key: serialize_item(item) for key, item in values.items()}


def serialize_item(item: Any) -> Union[str, int, float, bool]:
    """Serialize the given item.

    Parameters
    ----------
    item : Any
        Item to serialize.

    Returns
    -------
    Union[str, int, float, bool]
        Valid item.
    """
    if isinstance(item, (str, int, float, bool)):
        return item
    elif isinstance(item, (dict, list)):
        return json.dumps(item)
    elif isinstance(item, datetime):
        return datetime.isoformat()
    else:
        raise ValueError(f"{type(item)} is no supported type")

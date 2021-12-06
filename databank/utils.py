import json
from datetime import datetime
from typing import Any, Union

# supported types for a row value
Value = Union[str, int, float, bool, tuple, datetime]

def serialize_params(params: dict[str, Any]) -> dict[str, Value]:
    """Serialize the given parameters to supported data types.

    Note
    ----
    Dictionaries and lists are serialized as JSON.

    Parameters
    ----------
    params : dict[str, Any]
        Parameters to serialize.

    Returns
    -------
    dict[str, Value]
        Parameters serialized as string, integer, float or boolean.
    """
    return {key: serialize_param(value) for key, value in params.items()}


def serialize_param(param: Any) -> Value:
    """Serialize the given parameter to a supported data type.

    Note
    ----
    Dictionaries and lists are serialized as JSON.

    Parameters
    ----------
    param : Any
        Parameter to serialize.

    Raises
    ------
    ValueError
        If the given parameter is not serializable.

    Returns
    -------
    Value
        Serialized parameter.
    """
    if isinstance(param, (str, int, float, bool, tuple, datetime)):
        return param
    elif isinstance(param, (dict, list)):
        return json.dumps(param)
    elif param is None:
        return None
    else:
        raise ValueError(f"{type(param)} is not serializable")

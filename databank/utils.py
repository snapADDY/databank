import json
from datetime import datetime
from typing import Any, Union


def serialize_params(params: dict[str, Any]) -> dict[str, Union[str, int, float, bool]]:
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
    dict[str, Union[str, int, float, bool]]
        Parameters serialized as string, integer, float or boolean.
    """
    return {key: serialize_param(value) for key, value in params.items()}


def serialize_param(param: Any) -> Union[str, int, float, bool]:
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
    Union[str, int, float, bool]
        Serialized parameter.
    """
    if isinstance(param, (str, int, float, bool)):
        return param
    elif isinstance(param, (dict, list)):
        return json.dumps(param)
    elif isinstance(param, datetime):
        return param.isoformat()
    else:
        raise ValueError(f"{type(param)} is not serializable")

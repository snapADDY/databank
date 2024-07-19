import json
from datetime import date, datetime
from typing import Any, Literal, Mapping, Optional, Union

from sqlalchemy import text
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql.elements import TextClause

SUPPORTED_TYPES = (str, int, float, bool, tuple, datetime, date)

# supported types for a row value
Value = Union[
    str, int, float, bool, tuple, datetime, date, Literal["Jsonb"], Literal["Json"], None
]


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
    if isinstance(param, SUPPORTED_TYPES) or (type(param).__name__ in {"Jsonb", "Json"}):
        return param
    elif isinstance(param, (dict, list)):
        return json.dumps(param)
    elif param is None:
        return None
    else:
        raise ValueError(f"{type(param)} is not serializable")


def compile_sql(query: str, params: Mapping = {}, dialect: Optional[Dialect] = None) -> str:
    """Compile the given query and bind the parameters to get the actual SQL query.

    Parameters
    ----------
    query : str
        SQL query to execute.
    params : Mapping
        Parameters to bind to the query.
    dialect : Optional[Dialect]
        SQL dialect.

    Returns
    -------
    str
        Compile SQL query with actual data.
    """
    # bind params to sql query
    sql: TextClause = text(query).bindparams(**params)

    # compile sql and bind params
    return str(sql.compile(compile_kwargs={"literal_binds": True}, dialect=dialect))

import json
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql.elements import TextClause

try:
    from psycopg.types.json import Json, Jsonb

    SUPPORTED_TYPES = (str, int, float, bool, tuple, datetime, date, Jsonb, Json)
    Value = str | int | float | bool | tuple | datetime | date | Jsonb | Json
except ModuleNotFoundError:
    SUPPORTED_TYPES = (str, int, float, bool, tuple, datetime, date)
    Value = str | int | float | bool | tuple | datetime | date


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
    if isinstance(param, SUPPORTED_TYPES):
        return param

    if isinstance(param, (dict, list)):
        return json.dumps(param)

    if param is None:
        return None

    raise ValueError(f"{type(param)} is not serializable")


def compile_sql(query: str, params: Mapping = {}, dialect: Dialect | None = None) -> str:
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

import json
from collections.abc import Mapping
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql.elements import TextClause

# types the database drivers can handle natively
_NATIVE_TYPES = (
    str,
    int,
    float,
    bool,
    bytes,
    tuple,
    datetime,
    date,
    time,
    timedelta,
    Decimal,
    UUID,
)
_NativeValue = (
    str | int | float | bool | bytes | tuple | datetime | date | time | timedelta | Decimal | UUID
)

try:
    from psycopg.types.json import Json, Jsonb

    SUPPORTED_TYPES = (*_NATIVE_TYPES, Jsonb, Json)
    Value = _NativeValue | Jsonb | Json
except ImportError:
    # psycopg is not installed or can't be loaded (e.g. libpq is missing)
    SUPPORTED_TYPES = _NATIVE_TYPES
    Value = _NativeValue


def _json_default(obj: Any) -> str:
    """Serialize objects the json module can't handle by default."""
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()

    if isinstance(obj, (Decimal, UUID)):
        return str(obj)

    raise TypeError(f"{type(obj)} is not JSON serializable")


def serialize_params(params: Mapping[str, Any]) -> dict[str, Value | None]:
    """Serialize the given parameters to supported data types.

    Note
    ----
    Dictionaries and lists are serialized as JSON.

    Parameters
    ----------
    params : Mapping[str, Any]
        Parameters to serialize.

    Raises
    ------
    ValueError
        If a parameter is not serializable.

    Returns
    -------
    dict[str, Value | None]
        Serialized parameters.
    """
    return {key: serialize_param(value) for key, value in params.items()}


def serialize_param(param: Any) -> Value | None:
    """Serialize the given parameter to a supported data type.

    Note
    ----
    Dictionaries and lists are serialized as JSON. Dates, times, decimals and UUIDs inside of
    them are serialized as strings.

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
    Value | None
        Serialized parameter.
    """
    if param is None or isinstance(param, SUPPORTED_TYPES):
        return param

    if isinstance(param, (dict, list)):
        try:
            return json.dumps(param, default=_json_default)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{type(param)} is not serializable: {error}") from error

    raise ValueError(f"{type(param)} is not serializable")


def compile_sql(query: str, params: Mapping | None = None, dialect: Dialect | None = None) -> str:
    """Compile the given query and bind the parameters to get the actual SQL query.

    Warning
    -------
    The parameters are rendered as literals into the query. Use the result for logging or
    debugging only and never execute it, use parameter binding instead.

    Parameters
    ----------
    query : str
        SQL query to compile.
    params : Mapping | None
        Parameters to bind to the query. Parameters not used in the query are ignored.
    dialect : Dialect | None
        SQL dialect.

    Returns
    -------
    str
        Compiled SQL query with actual data.
    """
    sql: TextClause = text(query)

    # only bind params the query actually uses (like execute does)
    names = sql.compile().params.keys()
    sql = sql.bindparams(**{key: value for key, value in (params or {}).items() if key in names})

    # compile sql and bind params
    return str(sql.compile(compile_kwargs={"literal_binds": True}, dialect=dialect))

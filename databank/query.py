import re
from collections.abc import Iterator, Mapping
from os import PathLike
from pathlib import Path

# pattern a query header must match, e.g. `/* @name select_all */`
_HEADER_PATTERN = re.compile(r"/\*[ \t]*@name[ \t]+(\w+)[ \t]*\*/")

# a header occupying a whole line (surrounding whitespace allowed)
_HEADER_LINE_PATTERN = re.compile(rf"^[ \t]*{_HEADER_PATTERN.pattern}[ \t]*$", re.MULTILINE)

# a line that looks like it is meant to be a query header
_HEADER_LIKE_PATTERN = re.compile(r"^[ \t]*/\*+[ \t]*@name\b.*$", re.MULTILINE)

# sql comments, which are allowed before the first query header
_COMMENT_PATTERN = re.compile(r"--[^\n]*|/\*.*?\*/", re.DOTALL)


class InvalidQueryError(Exception):
    """Exception raised when a query file cannot be parsed."""


class InvalidQueryHeaderError(InvalidQueryError):
    """Exception raised when a query header is invalid."""


class QueryCollection(Mapping):
    """Collection of SQL queries."""

    def __init__(self, queries: Mapping[str, str]):
        """Initialize a collection of SQL queries.

        Parameters
        ----------
        queries : Mapping[str, str]
            Mapping of query names and queries.
        """
        self._queries = dict(queries)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the query names.

        Yields
        ------
        str
            Query name.
        """
        yield from self._queries

    def __len__(self) -> int:
        """Get the number of queries in this collection.

        Returns
        -------
        int
            Number of queries in this collection.
        """
        return len(self._queries)

    def __getitem__(self, key: str) -> str:
        """Get the query with the given name.

        Parameters
        ----------
        key : str
            Name of the query to get.

        Raises
        ------
        KeyError
            If the given key is not a valid query name.

        Returns
        -------
        str
            Query with the given name.
        """
        if key not in self._queries:
            raise KeyError(f"'{key}' is not a valid query name")

        return self._queries[key]

    def __repr__(self) -> str:
        """Get the string representation of this collection.

        Returns
        -------
        str
            String representation of this collection.
        """
        return f"<QueryCollection ({len(self)} queries): {list(self._queries)}>"

    @classmethod
    def from_string(cls, sql: str):
        """Create a QueryCollection from the given SQL string.

        Every query starts with a header line like `/* @name query_name */`, followed by the
        query itself, which ends at the next header or at the end of the string.

        Parameters
        ----------
        sql : str
            SQL string to parse.

        Raises
        ------
        InvalidQueryError
            If there is anything but comments before the first header, a query is empty or a
            query name is not unique.

        Returns
        -------
        QueryCollection
            QueryCollection created from the given string.
        """
        headers = list(_HEADER_LINE_PATTERN.finditer(sql))

        # reject malformed headers instead of silently merging them into the previous query
        for line in _HEADER_LIKE_PATTERN.finditer(sql):
            if not is_valid_query_header(line.group()):
                raise InvalidQueryHeaderError(f"'{line.group().strip()}' is not a valid header")

        # only comments are allowed before the first query
        preamble = sql[: headers[0].start()] if headers else sql
        if _COMMENT_PATTERN.sub("", preamble).strip():
            raise InvalidQueryHeaderError("Expected a query header before first query")

        queries = {}
        ends = [header.start() for header in headers[1:]] + [len(sql)]
        for header, end in zip(headers, ends, strict=False):
            name = header.group(1)
            query = sql[header.end() : end].strip()

            if not query:
                raise InvalidQueryError(f"Query '{name}' is empty")
            if name in queries:
                raise InvalidQueryError(f"Query name '{name}' is not unique")

            queries[name] = query

        return cls(queries)

    @classmethod
    def from_file(cls, filepath: str | PathLike):
        """Create a QueryCollection from the given file.

        Parameters
        ----------
        filepath : str | PathLike
            Path to the file to read.

        Raises
        ------
        ValueError
            If the given file is no SQL file.
        InvalidQueryError
            If the file cannot be parsed, see `QueryCollection.from_string`.

        Returns
        -------
        QueryCollection
            QueryCollection created from the given file.
        """
        filepath = Path(filepath)

        # file must be a sql file
        if filepath.suffix.lower() != ".sql":
            raise ValueError(f"'{filepath}' is no SQL file")

        return cls.from_string(filepath.read_text(encoding="utf-8"))


def is_valid_query_header(header: str) -> bool:
    """Check if the given header is a valid query header.

    Parameters
    ----------
    header : str
        Header to check.

    Returns
    -------
    bool
        True if the header is valid, False otherwise.
    """
    return _HEADER_PATTERN.fullmatch(header.strip()) is not None


def parse_header(header: str) -> dict[str, str]:
    """Parse the given query header.

    Parameters
    ----------
    header : str
        Query header to parse.

    Raises
    ------
    InvalidQueryHeaderError
        If the given header is not a valid query header.

    Returns
    -------
    dict[str, str]
        Dictionary of header name and value.
    """
    match = _HEADER_PATTERN.fullmatch(header.strip())
    if match is None:
        raise InvalidQueryHeaderError(f"'{header}' is not a valid query header")

    return {"name": match.group(1)}

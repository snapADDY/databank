import re
from collections.abc import Mapping
from os import PathLike
from pathlib import Path

# queries are separated by two newlines
QUERY_SEPARATOR = "\n\n"

# pattern a query header must match
_HEADER_PATTERN = re.compile(r"/\*\s@name\s\w+\s\*/")


class InvalidQueryHeader(Exception):
    ...


class QueryCollection(Mapping):
    def __init__(self, queries: dict[str, str]):
        """Collection of SQL queries.

        Parameters
        ----------
        queries : dict[str, str]
            Dictionary of query names and queries.
        """
        self._queries = queries

    def __iter__(self):
        """Iterate over the query names.

        Yields
        ------
        str
            Query name.
        """
        yield from self._queries

    def __len__(self):
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
    def from_file(cls, filepath: PathLike):
        """Create a QueryCollection from the given file.

        Parameters
        ----------
        filepath : PathLike
            Path to the file to read.

        Raises
        ------
        ValueError
            If the given file is no SQL file.

        Returns
        -------
        QueryCollection
            QueryCollection created from the given file.
        """
        # file must be a sql file
        if not Path(filepath).suffix == ".sql":
            raise ValueError(f"'{filepath}' is no SQL file")

        # read file
        with Path(filepath).open("r", encoding="utf-8") as file:
            sql = file.read()

        # parse queries
        queries = {}
        for query in (q.strip() for q in sql.split(QUERY_SEPARATOR) if q.strip()):
            _lines = query.split("\n")

            # parse query header and body
            header = parse_header(_lines[0])
            queries[header["name"]] = "\n".join(_lines[1:]).strip()

        return cls(queries)


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
    return _HEADER_PATTERN.fullmatch(header) is not None


def parse_header(header: str) -> dict[str, str]:
    """Parse the given query header.

    Parameters
    ----------
    header : str
        Query header to parse.

    Raises
    ------
    InvalidQueryHeader
        If the given header is not a valid query header.

    Returns
    -------
    dict[str, str]
        Dictionary of header name and value.
    """
    if not is_valid_query_header(header):
        raise InvalidQueryHeader(f"'{header}' is not a valid query header")

    return {"name": header.removeprefix("/* @name ").removesuffix(" */")}

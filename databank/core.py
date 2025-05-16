from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Iterable, Mapping

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session


class Database:
    def __init__(self, url: str, **kwargs):
        """Connect to the given database.

        Parameters
        ----------
        url : str
            URL of the database to connect to.
        pool_size : int
            The size of the connection pool to use, by default 5.
        max_overflow : int
            The maximum number of connections to allow in the pool, by default 10.
        pool_timeout : int
            The number of seconds to wait before giving up on getting a connection from the pool, by default 30.
        pool_recycle : int
            The number of seconds to recycle a connection, by default 3600.
        """
        self._engine = create_engine(url, **kwargs)
        self._session = scoped_session(sessionmaker(bind=self._engine, expire_on_commit=False))

    @contextmanager
    def create_session(self) -> Generator[Session, None, None]:
        """Create a new session for the current thread."""
        session = self._session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            self._session.remove()

    def execute(self, query: str, *, params: Mapping | None = None):
        """Execute the given SQL query with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping | None
            Parameters to bind to the query.
        """
        with self.create_session() as session:
            session.execute(text(query), params=params)

    def execute_many(self, query: str, *, params: Iterable[Mapping] | None = None):
        """Execute the given SQL query multiple times with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping] | None
            Iterable of params to bind to the query.
        """
        with self.create_session() as session:
            session.execute(text(query), params=params)

    def fetch_one(self, query: str, *, params: Mapping | None = None) -> dict:
        """Fetch the first result of the given SQL query with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping | None
            Parameters to bind to the query.
        """
        with self.create_session() as session:
            result = session.execute(text(query), params=params).fetchone()
            return result._asdict() if result else {}

    def fetch_many(self, query: str, *, params: Mapping | None = None, n: int = 1) -> list[dict]:
        """Fetch the first `n` results of the given SQL query with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping | None
            Parameters to bind to the query.
        n : int
            Number of rows to fetch, by default 1.
        """
        with self.create_session() as session:
            results = session.execute(text(query), params=params).fetchmany(n)
            return [result._asdict() for result in results if result]

    def fetch_all(self, query: str, *, params: Mapping | None = None) -> list[dict]:
        """Fetch all results of the given SQL query with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping | None
            Parameters to bind to the query.
        """
        with self.create_session() as session:
            results = session.execute(text(query), params=params).fetchall()
            return [result._asdict() for result in results if result]


class AsyncDatabase:
    def __init__(self, url: str, **kwargs):
        """Connect to the given database.

        Parameters
        ----------
        url : str
            URL of the database to connect to.
        pool_size : int
            The size of the connection pool to use, by default 5.
        max_overflow : int
            The maximum number of connections to allow in the pool, by default 10.
        pool_timeout : int
            The number of seconds to wait before giving up on getting a connection from the pool, by default 30.
        pool_recycle : int
            The number of seconds to recycle a connection, by default 3600.
        """
        self._engine: AsyncEngine = create_async_engine(url, **kwargs)
        self._session = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    @asynccontextmanager
    async def acreate_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create a new session for the current thread."""
        session = self._session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def aexecute(self, query: str, *, params: Mapping | None = None):
        """Execute the given SQL query with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping | None
            Parameters to bind to the query.
        """
        async with self.acreate_session() as session:
            await session.execute(text(query), params=params)

    async def aexecute_many(self, query: str, *, params: Iterable[Mapping] | None = None):
        """Execute the given SQL query multiple times with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping] | None
            Iterable of params to bind to the query.
        """
        async with self.acreate_session() as session:
            await session.execute(text(query), params=params)

    async def afetch_one(self, query: str, *, params: Mapping | None = None) -> dict:
        """Fetch the first result of the given SQL query with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping | None
            Parameters to bind to the query.
        """
        async with self.acreate_session() as session:
            result = await session.execute(text(query), params=params)
            row = result.fetchone()
            return row._asdict() if row else {}

    async def afetch_many(
        self, query: str, *, params: Mapping | None = None, n: int = 1
    ) -> list[dict]:
        """Fetch the first `n` results of the given SQL query with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping | None
            Parameters to bind to the query.
        n : int
            Number of rows to fetch, by default 1.
        """
        async with self.acreate_session() as session:
            result = await session.execute(text(query), params=params)
            rows = result.fetchmany(n)
            return [row._asdict() for row in rows if row]

    async def afetch_all(self, query: str, *, params: Mapping | None = None) -> list[dict]:
        """Fetch all results of the given SQL query with optional parameters.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping | None
            Parameters to bind to the query.
        """
        async with self.acreate_session() as session:
            result = await session.execute(text(query), params=params)
            rows = result.fetchall()
            return [row._asdict() for row in rows if row]

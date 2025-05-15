from typing import Iterable, Mapping

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, ResultProxy
from sqlalchemy.engine.row import RowProxy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker


class Database:
    def __init__(self, url: str, **kwargs):
        """Connect to the given database.

        Parameters
        ----------
        url : str
            URL of the database to connect to.
        """
        self.engine: Engine = create_engine(url, **kwargs)
        self.session: scoped_session = scoped_session(sessionmaker(bind=self.engine))

    def execute(self, query: str, *, params: Mapping = {}):
        """Execute and commit the given SQL query, optionally bind the params first.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping
            Parameters to bind to the query.
        """
        # create thread-local session
        self.session()

        # bind params to sql query
        sql: TextClause = text(query).bindparams(**params)

        try:
            self.session.execute(sql)
        except Exception:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

    def execute_many(self, query: str, *, params: Iterable[Mapping] = []):
        """Execute and commit multiple SQL queries, optionally bind the iterable of params first.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping]
            Iterable of params to bind to the query.
        """
        # create thread-local session
        self.session()

        # construct executable text clause
        sql: TextClause = text(query)

        try:
            self.session.execute(sql, params=params)
        except Exception:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

    def fetch_one(self, query: str, *, params: Mapping = {}) -> dict:
        """Execute the given SQL query, optionally bind the params, and fetch the first result.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping
            Parameters to bind to the query.
        """
        # create thread-local session
        self.session()

        # bind params to sql query
        sql: TextClause = text(query).bindparams(**params)

        try:
            result: ResultProxy = self.session.execute(sql)
            row: RowProxy = result.fetchone()
        except Exception:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

        return row._asdict() if row else {}

    def fetch_many(self, query: str, *, params: Mapping = {}, n: int = 1) -> list[dict]:
        """Execute the given SQL query, optionally bind params, and fetch the first `n` results.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping
            Parameters to bind to the query.
        n : int
            Number of rows to fetch, by default 1.
        """
        # create thread-local session
        self.session()

        # bind params to sql query
        sql = text(query).bindparams(**params)

        try:
            proxy: ResultProxy = self.session.execute(sql)
            result = proxy.fetchmany(n)
        except Exception:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

        return [row._asdict() for row in result if row]

    def fetch_all(self, query: str, *, params: Mapping = {}) -> list[dict]:
        """Execute the given SQL query, optionally bind the params, and fetch all results.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping
            Parameters to bind to the query.
        """
        # create thread-local session
        self.session()

        # bind params to sql query
        sql = text(query).bindparams(**params)

        try:
            proxy: ResultProxy = self.session.execute(sql)
            result = proxy.fetchall()
        except Exception:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

        return [row._asdict() for row in result if row]

    def execute_fetch_one(self, query: str, *, params: Iterable[Mapping] = []) -> dict:
        """Execute multiple SQL queries, optionally bind params, fetch first result of last query.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping]
            Iterable of params to bind to the query.
        """
        # create thread-local session
        self.session()

        # construct executable text clause
        sql: TextClause = text(query)

        try:
            proxy: ResultProxy = self.session.execute(sql, params=params)
            row: RowProxy = proxy.fetchone()
        except Exception:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

        return row._asdict() if row else {}

    def execute_fetch_many(
        self,
        query: str,
        params: Iterable[Mapping] = [],
        n: int = 1,
    ) -> list[dict]:
        """Execute SQL queries, optionally bind params, fetch first `n` results of last query.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping]
            Iterable of params to bind to the query.
        n : int
            Number of rows to fetch, by default 1.
        """
        # create thread-local session
        self.session()

        # construct executable text clause
        sql: TextClause = text(query)

        try:
            proxy: ResultProxy = self.session.execute(sql, params=params)
            result = proxy.fetchmany(n)
        except Exception:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

        return [row._asdict() for row in result if row]

    def execute_fetch_all(self, query: str, *, params: Iterable[Mapping] = []) -> list[dict]:
        """Execute multiple SQL queries, optionally bind params, fetch all results of last query.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping]
            Iterable of params to bind to the query.
        """
        # create thread-local session
        self.session()

        # construct executable text clause
        sql: TextClause = text(query)

        try:
            proxy: ResultProxy = self.session.execute(sql, params=params)
            result = proxy.fetchall()
        except Exception:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

        return [row._asdict() for row in result if row]


class AsyncDatabase:
    def __init__(self, url: str, **kwargs):
        """Connect to the given database.

        Parameters
        ----------
        url : str
            URL of the database to connect to.
        """
        self.engine: AsyncEngine = create_async_engine(url, **kwargs)
        self.session = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def aexecute(self, query: str, *, params: Mapping = {}):
        """Execute and commit the given SQL query, optionally bind the params first.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping
            Parameters to bind to the query.
        """
        # bind params to sql query
        sql: TextClause = text(query).bindparams(**params)

        async with self.session() as session:
            try:
                await session.execute(sql)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def aexecute_many(self, query: str, *, params: Iterable[Mapping] = []):
        """Execute and commit multiple SQL queries, optionally bind the iterable of params first.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping]
            Iterable of params to bind to the query.
        """
        # construct executable text clause
        sql: TextClause = text(query)

        async with self.session() as session:
            try:
                await session.execute(sql, params=params)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def afetch_one(self, query: str, *, params: Mapping = {}) -> dict:
        """Execute the given SQL query, optionally bind the params, and fetch the first result.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping
            Parameters to bind to the query.
        """
        # bind params to sql query
        sql: TextClause = text(query).bindparams(**params)

        async with self.session() as session:
            try:
                result = await session.execute(sql)
                row = result.fetchone()
                await session.commit()
                return row._asdict() if row else {}
            except Exception:
                await session.rollback()
                raise

    async def afetch_many(self, query: str, *, params: Mapping = {}, n: int = 1) -> list[dict]:
        """Execute the given SQL query, optionally bind params, and fetch the first `n` results.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping
            Parameters to bind to the query.
        n : int
            Number of rows to fetch, by default 1.
        """
        # bind params to sql query
        sql = text(query).bindparams(**params)

        async with self.session() as session:
            try:
                proxy = await session.execute(sql)
                result = proxy.fetchmany(n)
                await session.commit()
                return [row._asdict() for row in result if row]
            except Exception:
                await session.rollback()
                raise

    async def afetch_all(self, query: str, *, params: Mapping = {}) -> list[dict]:
        """Execute the given SQL query, optionally bind the params, and fetch all results.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Mapping
            Parameters to bind to the query.
        """
        # bind params to sql query
        sql = text(query).bindparams(**params)

        async with self.session() as session:
            try:
                proxy = await session.execute(sql)
                result = proxy.fetchall()
                await session.commit()
                return [row._asdict() for row in result if row]
            except Exception:
                await session.rollback()
                raise

    async def execute_fetch_one(self, query: str, *, params: Iterable[Mapping] = []) -> dict:
        """Execute multiple SQL queries, optionally bind params, fetch first result of last query.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping]
            Iterable of params to bind to the query.
        """
        # construct executable text clause
        sql: TextClause = text(query)

        async with self.session() as session:
            try:
                proxy = await session.execute(sql, params=params)
                row = proxy.fetchone()
                await session.commit()
                return row._asdict() if row else {}
            except Exception:
                await session.rollback()
                raise

    async def aexecute_fetch_many(
        self,
        query: str,
        params: Iterable[Mapping] = [],
        n: int = 1,
    ) -> list[dict]:
        """Execute SQL queries, optionally bind params, fetch first `n` results of last query.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping]
            Iterable of params to bind to the query.
        n : int
            Number of rows to fetch, by default 1.
        """
        # construct executable text clause
        sql: TextClause = text(query)

        async with self.session() as session:
            try:
                proxy = await session.execute(sql, params=params)
                result = proxy.fetchmany(n)
                await session.commit()
                return [row._asdict() for row in result if row]
            except Exception:
                await session.rollback()
                raise

    async def aexecute_fetch_all(
        self, query: str, *, params: Iterable[Mapping] = []
    ) -> list[dict]:
        """Execute multiple SQL queries, optionally bind params, fetch all results of last query.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Iterable[Mapping]
            Iterable of params to bind to the query.
        """
        # construct executable text clause
        sql: TextClause = text(query)

        async with self.session() as session:
            try:
                proxy = await session.execute(sql, params=params)
                result = proxy.fetchall()
                await session.commit()
                return [row._asdict() for row in result if row]
            except Exception:
                await session.rollback()
                raise

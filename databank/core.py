from typing import Iterable, Mapping

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, ResultProxy
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.util import ThreadLocalRegistry

from databank.utils import serialize_values


class Database:
    def __init__(self, url: str, pool_size: int = 10):
        """Initialize a database connection pool.

        If you are multi-threading, make sure the pool size is ≥ the number of threads.

        Parameters
        ----------
        url : str
            URL of the database to connect to.
        pool_size : int, optional
            Size of the connection pool, by default 10.
        """
        self.engine: Engine = create_engine(url, pool_size=pool_size)
        self.registry: ThreadLocalRegistry = scoped_session(sessionmaker(bind=self.engine))

    def execute(self, query: str, *, values: Mapping = {}):
        """Execute the given SQL query, optionally bind the values first.

        Parameters
        ----------
        query : str
            SQL query to execute.
        values : Mapping
            Values to bind to the query.
        """
        # create thread-local session
        session: Session = self.registry()

        # bind values to sql query
        sql = text(query).bindparams(**serialize_values(values))

        try:
            session.execute(sql)
        except:
            session.rollback()
            raise
        else:
            session.commit()

    def execute_many(self, query: str, *, values: Iterable[Mapping] = []):
        """Execute the given SQL query many times, optionally bind the iterable of values first.

        Parameters
        ----------
        query : str
            SQL query to execute.
        values : Iterable[Mapping]
            Iterable of values to bind to the query.
        """
        # create thread-local session
        session: Session = self.registry()

        # bind values to sql query
        sql = [text(query).bindparams(**params) for params in values]

        try:
            session.execute(sql)
        except:
            session.rollback()
            raise
        else:
            session.commit()

    def fetch_one(self, query: str, *, values: Mapping = {}) -> dict:
        """Execute the given SQL query, optionally bind the values, and fetch the first result.

        Parameters
        ----------
        query : str
            SQL query to execute.
        values : Mapping
            Values to bind to the query.
        """
        # create thread-local session
        session: Session = self.registry()

        # bind values to sql query
        sql = text(query).bindparams(**values)

        try:
            proxy: ResultProxy = session.execute(sql)
            result = proxy.fetchone()
        except:
            session.rollback()
            raise
        else:
            session.commit()

        return dict(result)

    def fetch_many(self, query: str, *, values: Mapping = {}, n: int = 1) -> dict:
        """Execute the given SQL query, optionally bind values, and fetch the first `n` results.

        Parameters
        ----------
        query : str
            SQL query to execute.
        values : Mapping
            Values to bind to the query.
        """
        # create thread-local session
        session: Session = self.registry()

        # bind values to sql query
        sql = text(query).bindparams(**values)

        try:
            proxy: ResultProxy = session.execute(sql)
            result = proxy.fetchmany(n)
        except:
            session.rollback()
            raise
        else:
            session.commit()

        return [dict(row) for row in result]

    def fetch_all(self, query: str, *, values: Mapping = {}):
        """Execute the given SQL query, optionally bind the values, and fetch all results.

        Parameters
        ----------
        query : str
            SQL query to execute.
        values : Mapping
            Values to bind to the query.
        """
        # create thread-local session
        session: Session = self.registry()

        # bind values to sql query
        sql = text(query).bindparams(**values)

        try:
            proxy: ResultProxy = session.execute(sql)
            result = proxy.fetchall()
        except:
            session.rollback()
            raise
        else:
            session.commit()

        return [dict(row) for row in result]

from typing import Iterable, Mapping

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, ResultProxy
from sqlalchemy.engine.row import RowProxy
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.util import ThreadLocalRegistry


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

    def execute(self, query: str, params: Mapping = {}):
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
        except:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

    def execute_many(self, query: str, params: Iterable[Mapping] = []):
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
        except:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.commit()
            self.session.remove()

    def fetch_one(self, query: str, params: Mapping = {}) -> dict:
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
        except:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.remove()

        return dict(row) if row else {}

    def fetch_many(self, query: str, params: Mapping = {}, n: int = 1) -> dict:
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
        except:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.remove()

        return [dict(row) for row in result if row]

    def fetch_all(self, query: str, params: Mapping = {}):
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
        except:
            self.session.rollback()
            self.session.remove()
            raise
        else:
            self.session.remove()

        return [dict(row) for row in result if row]

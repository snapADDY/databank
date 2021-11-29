# Databank

Databank is an easy-to-use Python library for making raw SQL queries in a multi-threaded environment.

No ORM, no frills. Thread-safe. Only raw SQL queries and parameter binding. Built on top of [SQLAlchemy](https://www.sqlalchemy.org/).

## Installation

You can install the latest stable version from [PyPI](https://pypi.org/project/databank/)

```
$ pip install databank
```

**Adapters are not included.** To work with PostgreSQL for example, you have to install `psycopg2` as well:

```
$ pip install psycopg2
```

## Usage

```python
>>> from databank import Database
>>> db = Database("postgresql://user:password@localhost/db")
>>> db.execute("INSERT INTO table VALUES (:a, :b);", values={"a": 0, "b": 1})
>>> db.fetch_one("SELECT * FROM table;")
{"a": 0, "b": 1}
```

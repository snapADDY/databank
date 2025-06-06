# Databank

[![PyPI](https://img.shields.io/pypi/v/databank.svg)](https://pypi.org/project/databank) ![GitHub Actions](https://github.com/snapADDY/databank/actions/workflows/main.yml/badge.svg)

Databank is an easy-to-use Python library for making raw SQL queries in a multi-threaded environment.

No ORM, no frills. Only raw SQL queries and parameter binding. Thread-safe. Built on top of [SQLAlchemy](https://www.sqlalchemy.org/).

[![IBM System/360 Model 91](https://live.staticflickr.com/7328/9169294489_ba900907f1_b.jpg)](https://www.flickr.com/photos/mratzloff/9169294489/)

(The photo was taken by [Matthew Ratzloff](https://www.flickr.com/photos/mratzloff/) and is licensed under CC BY-NC-ND 2.0.)
## Installation

You can install the latest stable version from [PyPI](https://pypi.org/project/databank/):

```
$ pip install databank
```

**Adapters not included.** Install e.g. `psycopg` for PostgreSQL:

```
$ pip install psycopg
```

## Usage

Connect to the database of your choice:

```python
>>> from databank import Database
>>> db = Database("postgresql+psycopg://user:password@localhost/db", pool_size=2)
```

The keyword arguments are passed directly to SQLAlchemy's `create_engine()` function. Depending on the database you connect to, you have options like the size of connection pools.

> If you are using `databank` in a multi-threaded environment (e.g. in a web application), make sure the pool size is at least the number of worker threads.

Let's create a simple table:

```python
>>> db.execute("CREATE TABLE beatles (id SERIAL PRIMARY KEY, member TEXT NOT NULL);")
```

You can insert multiple rows at once:

```python
>>> params = [
...     {"id": 0, "member": "John"},
...     {"id": 1, "member": "Paul"},
...     {"id": 2, "member": "George"},
...     {"id": 3, "member": "Ringo"}
... ]
>>> db.execute_many("INSERT INTO beatles (id, member) VALUES (:id, :member);", params)
```

Fetch a single row:

```python
>>> db.fetch_one("SELECT * FROM beatles;")
{'id': 0, 'member': 'John'}
```

But you can also fetch `n` rows:

```python
>>> db.fetch_many("SELECT * FROM beatles;", n=2)
[{'id': 0, 'member': 'John'}, {'id': 1, 'member': 'Paul'}]
```

Or all rows:

```python
>>> db.fetch_all("SELECT * FROM beatles;")
[{'id': 0, 'member': 'John'},
 {'id': 1, 'member': 'Paul'},
 {'id': 2, 'member': 'George'},
 {'id': 3, 'member': 'Ringo'}]
```

If you are using PostgreSQL with `jsonb` columns, you can use a helper function to serialize the parameter values:

```python
>>> from databank.utils import serialize_params
>>> serialize_params({"member": "Ringo", "song": ["Don't Pass Me By", "Octopus's Garden"]})
{'member': 'Ringo', 'song': '["Don\'t Pass Me By", "Octopus\'s Garden"]'}
```

### Async

You can also use `AsyncDatabase` which implements basically the same methods as `Database` (but with [an `a` prefix](https://peps.python.org/pep-0492/#why-magic-methods-start-with-a)):

```python
>>> from databank import AsyncDatabase
>>> db = AsyncDatabase("postgresql+psycopg://user:password@localhost/db", pool_size=2)
>>> await db.afetch_one("SELECT * FROM beatles;")
{'id': 0, 'member': 'John'}
```

## Query Collection

You can also organize SQL queries in an SQL file and load them into a `QueryCollection`:

```sql
/* @name insert_data */
INSERT INTO beatles (id, member) VALUES (:id, :member);

/* @name select_all_data */
SELECT * FROM beatles;
```

> This idea is borrowed from [PgTyped](https://pgtyped.dev/docs/sql-file)

A query _must_ have a header comment with the name of the query. If a query name is not unique, the last query with the same name will be used. You can parse that file and load the queries into a `QueryCollection`:

```python
>>> from databank import QueryCollection
>>> queries = QueryCollection.from_file("queries.sql")
```

and access the queries like in a dictionary:

```python
>>> queries["insert_data"]
'INSERT INTO beatles (id, member) VALUES (:id, :member);'
>>> queries["select_all_data"]
'SELECT * FROM beatles;'
```

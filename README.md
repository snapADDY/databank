# Databank

[![PyPI](https://img.shields.io/pypi/v/databank.svg)](https://pypi.org/project/databank) ![GitHub Actions](https://github.com/snapADDY/databank/workflows/main/badge.svg)


Databank is a Python library for making raw SQL queries in a multi-threaded environment.

No ORM, no frills. Only raw SQL queries and parameter binding. Thread-safe. Built on top of [SQLAlchemy](https://www.sqlalchemy.org/).

## Installation

You can install the latest stable version from [PyPI](https://pypi.org/project/databank/)

```
$ pip install databank
```

**Adapters not included.** Install e.g. `psycopg2` for a PostgreSQL database:

```
$ pip install psycopg2
```

## Usage

```python
from databank import Database

# create connection pool
db = Database("postgresql://user:password@localhost/db")

# create a table
db.execute("CREATE TABLE beatles (id SERIAL PRIMARY KEY, member TEXT NOT NULL);")

# insert data
values = [
    {"member": "John"},
    {"member": "Paul"},
    {"member": "George"}
    {"member": "Ringo"}
]
db.execute_many("INSERT INTO beatles (member) VALUES (:member);", values=values)

# select a single row
db.fetch_one("SELECT * FROM beatles;")


# select the two rows
db.fetch_many("SELECT * FROM beatles;", n=2)

# select all rows
db.fetch_all("SELECT * FROM beatles;")
```

If you are using `databank` in a multi-threaded environment (e.g. in a web application), make sure the pool size is at least the number of threads.

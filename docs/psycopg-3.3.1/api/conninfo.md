<a id="psycopg-conninfo"></a>

# `conninfo` – manipulate connection strings

This module contains a few utility functions to manipulate database
connection strings.

<a id="module-psycopg.conninfo"></a>

### psycopg.conninfo.conninfo_to_dict(conninfo: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', \*\*kwargs: [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)) → [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)]

Convert the `conninfo` string into a dictionary of parameters.

* **Parameters:**
  * **conninfo** – A [connection string](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING) as accepted by PostgreSQL.
  * **kwargs** – Parameters overriding the ones specified in `conninfo`.
* **Returns:**
  Dictionary with the parameters parsed from `conninfo` and
  `kwargs`.

Raise [`ProgrammingError`](errors.md#psycopg.ProgrammingError) if `conninfo` is not a a valid connection
string.

```python
>>> conninfo_to_dict("postgres://jeff@example.com/db", user="piro")
{'user': 'piro', 'dbname': 'db', 'host': 'example.com'}
```

### psycopg.conninfo.make_conninfo(conninfo: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', \*\*kwargs: [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)) → [str](https://docs.python.org/3/library/stdtypes.html#str)

Merge a string and keyword params into a single conninfo string.

* **Parameters:**
  * **conninfo** – A [connection string](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING) as accepted by PostgreSQL.
  * **kwargs** – Parameters overriding the ones specified in `conninfo`.
* **Returns:**
  A connection string valid for PostgreSQL, with the `kwargs`
  parameters merged.

Raise [`ProgrammingError`](errors.md#psycopg.ProgrammingError) if the input doesn’t make a valid
conninfo string.

```python
>>> make_conninfo("dbname=db user=jeff", user="piro", port=5432)
'dbname=db user=piro port=5432'
```

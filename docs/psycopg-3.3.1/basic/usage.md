<a id="module-usage"></a>

# Basic module usage

The basic Psycopg usage is common to all the database adapters implementing
the [DB-API](https://www.python.org/dev/peps/pep-0249/) protocol. Other database adapters, such as the builtin
[`sqlite3`](https://docs.python.org/3/library/sqlite3.html#module-sqlite3) or [`psycopg2`](https://www.psycopg.org/docs/module.html#module-psycopg2), have roughly the same pattern of interaction.

<a id="index-0"></a>

<a id="usage"></a>

## Main objects in Psycopg 3

Here is an interactive session showing some of the basic commands:

```python
# Note: the module name is psycopg, not psycopg3
import psycopg

# Connect to an existing database
with psycopg.connect("dbname=test user=postgres") as conn:

    # Open a cursor to perform database operations
    with conn.cursor() as cur:

        # Execute a command: this creates a new table
        cur.execute("""
            CREATE TABLE test (
                id serial PRIMARY KEY,
                num integer,
                data text)
            """)

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no SQL injections!)
        cur.execute(
            "INSERT INTO test (num, data) VALUES (%s, %s)",
            (100, "abc'def"))

        # Query the database and obtain data as Python objects.
        cur.execute("SELECT * FROM test")
        print(cur.fetchone())
        # will print (1, 100, "abc'def")

        # You can use `cur.executemany()` to perform an operation in batch
        cur.executemany(
            "INSERT INTO test (num) values (%s)",
            [(33,), (66,), (99,)])

        # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
        # of several records, or even iterate on the cursor
        cur.execute("SELECT id, num FROM test order by num")
        for record in cur:
            print(record)

        # Make the changes to the database persistent
        conn.commit()
```

In the example you can see some of the main objects and methods and how they
relate to each other:

- The function [`connect()`](../api/connections.md#psycopg.Connection.connect) creates a new database session and
  returns a new [`Connection`](../api/connections.md#psycopg.Connection) instance. [`AsyncConnection.connect()`](../api/connections.md#psycopg.AsyncConnection.connect)
  creates an [`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio) connection instead.
- The [`Connection`](../api/connections.md#psycopg.Connection) class encapsulates a database session. It allows to:
  - create new [`Cursor`](../api/cursors.md#psycopg.Cursor) instances using the [`cursor()`](../api/connections.md#psycopg.Connection.cursor) method to
    execute database commands and queries,
  - terminate transactions using the methods [`commit()`](../api/connections.md#psycopg.Connection.commit) or
    [`rollback()`](../api/connections.md#psycopg.Connection.rollback).
- The class [`Cursor`](../api/cursors.md#psycopg.Cursor) allows interaction with the database:
  - send commands to the database using methods such as [`execute()`](../api/cursors.md#psycopg.Cursor.execute)
    and [`executemany()`](../api/cursors.md#psycopg.Cursor.executemany),
  - retrieve data from the database, iterating on the cursor or using methods
    such as [`fetchone()`](../api/cursors.md#psycopg.Cursor.fetchone), [`fetchmany()`](../api/cursors.md#psycopg.Cursor.fetchmany), [`fetchall()`](../api/cursors.md#psycopg.Cursor.fetchall).
- Using these objects as context managers (i.e. using `with`) will make sure
  to close them and free their resources at the end of the block (notice that
  [this is different from psycopg2](from_pg2.md#diff-with)).

#### SEE ALSO
A few important topics you will have to deal with are:

- [Passing parameters to SQL queries](params.md#query-parameters).
- [Adapting basic Python types](adapt.md#types-adaptation).
- [Transactions management](transactions.md#transactions).

## Shortcuts

The pattern above is familiar to `psycopg2` users. However, Psycopg 3 also
exposes a few simple extensions which make the above pattern leaner:

- the [`Connection`](../api/connections.md#psycopg.Connection) objects exposes an [`execute()`](../api/connections.md#psycopg.Connection.execute) method,
  equivalent to creating a cursor, calling its [`execute()`](../api/cursors.md#psycopg.Cursor.execute) method, and
  returning it.
  ```default
  # In Psycopg 2
  cur = conn.cursor()
  cur.execute(...)

  # In Psycopg 3
  cur = conn.execute(...)
  ```
- The [`Cursor.execute()`](../api/cursors.md#psycopg.Cursor.execute) method returns `self`. This means that you can chain
  a fetch operation, such as [`fetchone()`](../api/cursors.md#psycopg.Cursor.fetchone), to the `execute()` call:
  ```default
  # In Psycopg 2
  cur.execute(...)
  record = cur.fetchone()

  cur.execute(...)
  for record in cur:
      ...

  # In Psycopg 3
  record = cur.execute(...).fetchone()

  for record in cur.execute(...):
      ...
  ```

Using them together, in simple cases, you can go from creating a connection to
using a result in a single expression:

```default
print(psycopg.connect(DSN).execute("SELECT now()").fetchone()[0])
# 2042-07-12 18:15:10.706497+01:00
```

<a id="index-1"></a>

<a id="with-connection"></a>

## Connection context

Psycopg 3 [`Connection`](../api/connections.md#psycopg.Connection) can be used as a context manager:

```python
with psycopg.connect() as conn:
    ... # use the connection

# the connection is now closed
```

When the block is exited, if there is a transaction open, it will be
committed. If an exception is raised within the block the transaction is
rolled back. In both cases the connection is closed. It is roughly the
equivalent of:

```python
conn = psycopg.connect()
try:
    ... # use the connection
except BaseException:
    conn.rollback()
else:
    conn.commit()
finally:
    conn.close()
```

#### NOTE
This behaviour is not what `psycopg2` does: in `psycopg2` [there is
no final close()](https://www.psycopg.org/docs/usage.html#with) and the connection can be used in several
`with` statements to manage different transactions. This behaviour has
been considered non-standard and surprising so it has been replaced by the
more explicit [`transaction()`](../api/connections.md#psycopg.Connection.transaction) block.

Note that, while the above pattern is what most people would use, [`connect()`](../api/module.md#psycopg.connect)
doesn’t enter a block itself, but returns an “un-entered” connection, so that
it is still possible to use a connection regardless of the code scope and the
developer is free to use (and responsible for calling) [`commit()`](../api/connections.md#psycopg.Connection.commit),
[`rollback()`](../api/connections.md#psycopg.Connection.rollback), [`close()`](../api/connections.md#psycopg.Connection.close) as and where needed.

#### WARNING
If a connection is just left to go out of scope, the way it will behave
with or without the use of a `with` block is different:

- if the connection is used without a `with` block, the server will find
  a connection closed INTRANS and roll back the current transaction;
- if the connection is used with a `with` block, there will be an
  explicit COMMIT and the operations will be finalised.

You should use a `with` block when your intention is just to execute a
set of operations and then committing the result, which is the most usual
thing to do with a connection. If your connection life cycle and
transaction pattern is different, and want more control on it, the use
without `with` might be more convenient.

See [Transactions management](transactions.md#transactions) for more information.

[`AsyncConnection`](../api/connections.md#psycopg.AsyncConnection) can be also used as context manager, using `async with`,
but be careful about its quirkiness: see [with async connections](../advanced/async.md#async-with) for details.

## Adapting psycopg to your program

The above [pattern of use](#usage) only shows the default behaviour of
the adapter. Psycopg can be customised in several ways, to allow the smoothest
integration between your Python program and your PostgreSQL database:

- If your program is concurrent and based on [`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio) instead of on
  threads/processes, you can use [async connections and cursors](../advanced/async.md#async).
- If you want to customise the objects that the cursor returns, instead of
  receiving tuples, you can specify your [row factories](../advanced/rows.md#row-factories).
- If you want to customise how Python values and PostgreSQL types are mapped
  into each other, beside the [basic type mapping](adapt.md#types-adaptation),
  you can [configure your types](../advanced/adapt.md#adaptation).

<a id="logging"></a>

## Connection logging

Psycopg uses the stdlib [`logging`](https://docs.python.org/3/library/logging.html#module-logging) module to report the operations happening at
connection time. If you experience slowness or random failures on connection
you can set the `psycopg` logger at `DEBUG` level to read the operations
performed.

A very simple example of logging configuration may be the following:

```python
import logging
import psycopg

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

logging.getLogger("psycopg").setLevel(logging.DEBUG)

psycopg.connect("host=192.0.2.1,localhost connect_timeout=10")
```

In this example Psycopg will first try to connect to a non responsive server,
only stopping after hitting the timeout, and will move on to a working server.
The resulting log might look like:

```text
2045-05-10 11:45:54,364 DEBUG connection attempt: host: '192.0.2.1', port: None, hostaddr: '192.0.2.1'
2045-05-10 11:45:54,365 DEBUG connection started: <psycopg_c.pq.PGconn [STARTED] at 0x79dff6d26160>
2045-05-10 11:45:54,365 DEBUG connection polled: <psycopg_c.pq.PGconn [MADE] at 0x79dff6d26160>
2045-05-10 11:46:04,392 DEBUG connection failed: host: '192.0.2.1', port: None, hostaddr: '192.0.2.1': connection timeout expired
2045-05-10 11:46:04,392 DEBUG connection attempt: host: 'localhost', port: None, hostaddr: '127.0.0.1'
2045-05-10 11:46:04,393 DEBUG connection started: <psycopg_c.pq.PGconn [STARTED] at 0x79dff6d26160>
2045-05-10 11:46:04,394 DEBUG connection polled: <psycopg_c.pq.PGconn [MADE] at 0x79dff6d26160>
2045-05-10 11:46:04,394 DEBUG connection polled: <psycopg_c.pq.PGconn [SSL_STARTUP] at 0x79dff6d26160>
2045-05-10 11:46:04,411 DEBUG connection polled: <psycopg_c.pq.PGconn [SSL_STARTUP] at 0x79dff6d26160>
2045-05-10 11:46:04,413 DEBUG connection polled: <psycopg_c.pq.PGconn [SSL_STARTUP] at 0x79dff6d26160>
2045-05-10 11:46:04,423 DEBUG connection polled: <psycopg_c.pq.PGconn [MADE] at 0x79dff6d26160>
2045-05-10 11:46:04,424 DEBUG connection polled: <psycopg_c.pq.PGconn [AWAITING_RESPONSE] at 0x79dff6d26160>
2045-05-10 11:46:04,426 DEBUG connection polled: <psycopg_c.pq.PGconn [IDLE] (host=localhost database=piro) at 0x79dff6d26160>
2045-05-10 11:46:04,426 DEBUG connection succeeded: host: 'localhost', port: None, hostaddr: '127.0.0.1'
```

Please note that a connection attempt might try to reach different servers:
either explicitly because the connection string specifies [multiple hosts](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-MULTIPLE-HOSTS),
or implicitly, because the DNS resolves the host name to multiple IPs.

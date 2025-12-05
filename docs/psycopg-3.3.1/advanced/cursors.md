<a id="index-0"></a>

<a id="cursor-types"></a>

# Cursor types

Cursors are objects used to send commands to a PostgreSQL connection and to
manage the results returned by it. They are normally created by the
connection’s [`cursor()`](../api/connections.md#psycopg.Connection.cursor) method.

Psycopg can manage different kinds of “cursors”, the objects used to send
queries and retrieve results from the server. They differ from each other in
aspects such as:

- Are the parameters bound on the client or on the server?
  [Server-side binding](../basic/from_pg2.md#server-side-binding) can offer better performance (for instance
  allowing to use prepared statements) and reduced memory footprint, but may
  require stricter query definition and certain queries that work in
  `psycopg2` might need to be adapted.
- Is the query result stored on the client or on the server? Server-side
  cursors allow partial retrieval of large datasets, but they might offer less
  performance in everyday usage.
- Are queries manipulated by Python (to handle placeholders in `%s` and
  `%(name)s` Python-style) or sent as they are to the PostgreSQL server
  (which only supports `$1`, `$2` parameters)?

Psycopg exposes the following classes to implement the different strategies.
All the classes are exposed by the main `psycopg` package. Every class has
also an `Async`-prefixed counterparts, designed to be used in conjunction
with [`AsyncConnection`](../api/connections.md#psycopg.AsyncConnection) in [`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio) programs.

| Class                                                          | Binding     | Storage     | Placeholders     | See also                                                    |
|----------------------------------------------------------------|-------------|-------------|------------------|-------------------------------------------------------------|
| [`Cursor`](../api/cursors.md#psycopg.Cursor)                   | server-side | client-side | `%s`, `%(name)s` | [Client-side cursors](#client-side-cursors)                 |
| [`ClientCursor`](../api/cursors.md#psycopg.ClientCursor)       | client-side | client-side | `%s`, `%(name)s` | [Client-side-binding cursors](#client-side-binding-cursors) |
| [`ServerCursor`](../api/cursors.md#psycopg.ServerCursor)       | server-side | server-side | `%s`, `%(name)s` | [Server-side cursors](#server-side-cursors)                 |
| [`RawCursor`](../api/cursors.md#psycopg.RawCursor)             | server-side | client-side | `$1`             | [Raw query cursors](#raw-query-cursors)                     |
| [`RawServerCursor`](../api/cursors.md#psycopg.RawServerCursor) | server-side | server-side | `$1`             | [Raw query cursors](#raw-query-cursors)                     |

If not specified by a [`cursor_factory`](../api/connections.md#psycopg.Connection.cursor_factory), [`cursor()`](../api/connections.md#psycopg.Connection.cursor)
will usually produce [`Cursor`](../api/cursors.md#psycopg.Cursor) objects.

<a id="index-1"></a>

<a id="client-side-cursors"></a>

## Client-side cursors

Client-side cursors are what Psycopg uses in its normal querying process.
They are implemented by the [`Cursor`](../api/cursors.md#psycopg.Cursor) and [`AsyncCursor`](../api/cursors.md#psycopg.AsyncCursor) classes. In such
querying pattern, after a cursor sends a query to the server (usually calling
[`execute()`](../api/cursors.md#psycopg.Cursor.execute)), the server replies transferring to the client the whole
set of results requested, which is stored in the state of the same cursor and
from where it can be read from Python code (using methods such as
[`fetchone()`](../api/cursors.md#psycopg.Cursor.fetchone) and siblings).

This querying process is very scalable because, after a query result has been
transmitted to the client, the server doesn’t keep any state. Because the
results are already in the client memory, iterating its rows is very quick.

The downside of this querying method is that the entire result has to be
transmitted completely to the client (with a time proportional to its size)
and the client needs enough memory to hold it, so it is only suitable for
reasonably small result sets.

<a id="index-2"></a>

<a id="client-side-binding-cursors"></a>

## Client-side-binding cursors

#### Versionadded
Added in version 3.1.

The previously described [client-side cursors](#client-side-cursors) send
the query and the parameters separately to the server. This is the most
efficient way to process parametrised queries and allows to build several
features and optimizations. However, not all types of queries can be bound
server-side; in particular no Data Definition Language query can. See
[Server-side binding](../basic/from_pg2.md#server-side-binding) for the description of these problems.

The [`ClientCursor`](../api/cursors.md#psycopg.ClientCursor) (and its [`AsyncClientCursor`](../api/cursors.md#psycopg.AsyncClientCursor) async counterpart) merge the
query on the client and send the query and the parameters merged together to
the server. This allows to parametrize any type of PostgreSQL statement, not
only queries (`SELECT`) and Data Manipulation statements (`INSERT`,
`UPDATE`, `DELETE`).

Using `ClientCursor`, Psycopg 3 behaviour will be more similar to [`psycopg2`](https://www.psycopg.org/docs/module.html#module-psycopg2)
(which only implements client-side binding) and could be useful to port
Psycopg 2 programs more easily to Psycopg 3. The objects in the [`sql`](../api/sql.md#module-psycopg.sql) module
allow for greater flexibility (for instance to parametrize a table name too,
not only values); however, for simple cases, a `ClientCursor` could be the
right object.

In order to obtain `ClientCursor` from a connection, you can set its
[`cursor_factory`](../api/connections.md#psycopg.Connection.cursor_factory) (at init time or changing its attribute
afterwards):

```python
from psycopg import connect, ClientCursor

conn = psycopg.connect(DSN, cursor_factory=ClientCursor)
cur = conn.cursor()
# <psycopg.ClientCursor [no result] [IDLE] (database=piro) at 0x7fd977ae2880>
```

If you need to create a one-off client-side-binding cursor out of a normal
connection, you can just use the [`ClientCursor`](../api/cursors.md#psycopg.ClientCursor) class passing the connection
as argument.

```python
conn = psycopg.connect(DSN)
cur = psycopg.ClientCursor(conn)
```

#### WARNING
Client-side cursors don’t support [binary parameters and return
values](../basic/params.md#binary-data) and don’t support [prepared statements](prepare.md#prepared-statements).

<a id="index-3"></a>

<a id="simple-query-protocol"></a>

### Simple query protocol

Using the `ClientCursor` should ensure that psycopg will always use the
[simple query protocol](https://www.postgresql.org/docs/current/protocol-flow.html#PROTOCOL-FLOW-SIMPLE-QUERY) for querying. In most cases, the choice of the
fronted/backend protocol used is transparent on PostgreSQL. However, in some
case using the simple query protocol is mandatory. This is the case querying
the [PgBouncer admin console](https://www.pgbouncer.org/usage.html#admin-console) for instance, which doesn’t support the
extended query protocol.

```python
from psycopg import connect, ClientCursor

conn = psycopg.connect(ADMIN_DSN, cursor_factory=ClientCursor)
cur = conn.cursor()
cur.execute("SHOW STATS")
cur.fetchall()
```

#### Versionchanged
Changed in version 3.1.20: While querying using the `ClientCursor` works well with PgBouncer, the
connection’s COMMIT and ROLLBACK commands are only ensured to be executed
using the simple query protocol starting from Psycopg 3.1.20.

In previous versions you should use an autocommit connection in order to
query the PgBouncer admin console:

```python
from psycopg import connect, ClientCursor

conn = psycopg.connect(ADMIN_DSN, cursor_factory=ClientCursor, autocommit=True)
...
```

<a id="index-4"></a>

<a id="server-side-cursors"></a>

## Server-side cursors

PostgreSQL has its own concept of *cursor* too (sometimes also called
*portal*). When a database cursor is created, the query is not necessarily
completely processed: the server might be able to produce results only as they
are needed. Only the results requested are transmitted to the client: if the
query result is very large but the client only needs the first few records it
is possible to transmit only them.

The downside is that the server needs to keep track of the partially
processed results, so it uses more memory and resources on the server.

Psycopg allows the use of server-side cursors using the classes [`ServerCursor`](../api/cursors.md#psycopg.ServerCursor)
and [`AsyncServerCursor`](../api/cursors.md#psycopg.AsyncServerCursor). They are usually created by passing the `name`
parameter to the [`cursor()`](../api/connections.md#psycopg.Connection.cursor) method (reason for which, in
`psycopg2`, they are usually called *named cursors*). The use of these classes
is similar to their client-side counterparts: their interface is the same, but
behind the scene they send commands to control the state of the cursor on the
server (for instance when fetching new records or when moving using
[`scroll()`](../api/cursors.md#psycopg.Cursor.scroll)).

Using a server-side cursor it is possible to process datasets larger than what
would fit in the client’s memory. However for small queries they are less
efficient because it takes more commands to receive their result, so you
should use them only if you need to process huge results or if only a partial
result is needed.

#### SEE ALSO
Server-side cursors are created and managed by [`ServerCursor`](../api/cursors.md#psycopg.ServerCursor) using SQL
commands such as [DECLARE](https://www.postgresql.org/docs/current/sql-declare.html), [FETCH](https://www.postgresql.org/docs/current/sql-fetch.html), [MOVE](https://www.postgresql.org/docs/current/sql-move.html). The PostgreSQL documentation
gives a good idea of what is possible to do with them.

<a id="cursor-steal"></a>

### “Stealing” an existing cursor

A Psycopg [`ServerCursor`](../api/cursors.md#psycopg.ServerCursor) can be also used to consume a cursor which was
created in other ways than the `DECLARE` that [`ServerCursor.execute()`](../api/cursors.md#psycopg.ServerCursor.execute)
runs behind the scene.

For instance if you have a [PL/pgSQL function returning a cursor](https://www.postgresql.org/docs/current/plpgsql-cursors.html):

```postgres
CREATE FUNCTION reffunc(refcursor) RETURNS refcursor AS $$
BEGIN
    OPEN $1 FOR SELECT col FROM test;
    RETURN $1;
END;
$$ LANGUAGE plpgsql;
```

you can run a one-off command in the same connection to call it (e.g. using
[`Connection.execute()`](../api/connections.md#psycopg.Connection.execute)) in order to create the cursor on the server:

```python
conn.execute("SELECT reffunc('curname')")
```

after which you can create a server-side cursor declared by the same name, and
directly call the fetch methods, skipping the [`execute()`](../api/cursors.md#psycopg.ServerCursor.execute) call:

```python
cur = conn.cursor('curname')
# no cur.execute()
for record in cur:  # or cur.fetchone(), cur.fetchmany()...
    # do something with record
```

<a id="raw-query-cursors"></a>

## Raw query cursors

#### Versionadded
Added in version 3.2.

The [`RawCursor`](../api/cursors.md#psycopg.RawCursor) and [`AsyncRawCursor`](../api/cursors.md#psycopg.AsyncRawCursor) classes allow users to use PostgreSQL
native placeholders (`$1`, `$2`, etc.) in their queries instead of the
standard `%s` placeholder. This can be useful when it’s desirable to pass
the query unmodified to PostgreSQL and rely on PostgreSQL’s placeholder
functionality, such as when dealing with a very complex query containing
`%s` inside strings, dollar-quoted strings or elsewhere.

One important note is that raw query cursors only accept positional arguments
in the form of a list or tuple. This means you cannot use named arguments
(i.e., dictionaries).

`RawCursor` behaves like [`Cursor`](../api/cursors.md#psycopg.Cursor), in returning the complete result from the
server to the client. The [`RawServerCursor`](../api/cursors.md#psycopg.RawServerCursor) and [`AsyncRawServerCursor`](../api/cursors.md#psycopg.AsyncRawServerCursor)
implement [Server-side cursors](#server-side-cursors) with raw PostgreSQL placeholders.

There are two ways to use raw query cursors:

1. Using the cursor factory:

```python
from psycopg import connect, RawCursor

with connect(dsn, cursor_factory=RawCursor) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT $1, $2", [1, "Hello"])
        assert cur.fetchone() == (1, "Hello")
```

1. Instantiating a cursor:

```python
from psycopg import connect, RawCursor

with connect(dsn) as conn:
    with RawCursor(conn) as cur:
        cur.execute("SELECT $1, $2", [1, "Hello"])
        assert cur.fetchone() == (1, "Hello")
```

# `crdb` – CockroachDB support

#### Versionadded
Added in version 3.1.

[CockroachDB](https://www.cockroachlabs.com/) is a distributed database using the same fronted-backend protocol
of PostgreSQL. As such, Psycopg can be used to write Python programs
interacting with CockroachDB.

Opening a connection to a CRDB database using [`psycopg.connect()`](module.md#psycopg.connect) provides a
largely working object. However, using the [`psycopg.crdb.connect()`](#psycopg.crdb.connect) function
instead, Psycopg will create more specialised objects and provide a types
mapping tweaked on the CockroachDB data model.

<a id="crdb-differences"></a>

## Main differences from PostgreSQL

CockroachDB behaviour is [different from PostgreSQL](https://www.cockroachlabs.com/docs/stable/postgresql-compatibility.html): please refer to the
database documentation for details. These are some of the main differences
affecting Psycopg behaviour:

- [`cancel()`](connections.md#psycopg.Connection.cancel) doesn’t work before CockroachDB 22.1. On
  older versions, you can use [CANCEL QUERY](https://www.cockroachlabs.com/docs/stable/cancel-query.html) instead (but from a different
  connection).
- [Server-side cursors](../advanced/cursors.md#server-side-cursors) are well supported only from CockroachDB 22.1.3.
- [`backend_pid`](objects.md#psycopg.ConnectionInfo.backend_pid) is only populated from CockroachDB
  22.1. Note however that you cannot use the PID to terminate the session; use
  [SHOW session_id](https://www.cockroachlabs.com/docs/stable/show-vars.html) to find the id of a session, which you may terminate with
  [CANCEL SESSION](https://www.cockroachlabs.com/docs/stable/cancel-session.html) in lieu of PostgreSQL’s `pg_terminate_backend()`.
- Several data types are missing or slightly different from PostgreSQL (see
  [`adapters`](#psycopg.crdb.adapters) for an overview of the differences).
- The [two-phase commit protocol](../basic/transactions.md#two-phase-commit) is not supported.
- `LISTEN` and `NOTIFY` are not supported. However the [CHANGEFEED](https://www.cockroachlabs.com/docs/stable/changefeed-for.html)
  command, in conjunction with [`stream()`](cursors.md#psycopg.Cursor.stream), can provide push
  notifications.

<a id="crdb-objects"></a>

## CockroachDB-specific objects

### psycopg.crdb.connect(conninfo: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', , autocommit: [bool](https://docs.python.org/3/library/functions.html#bool) = False, prepare_threshold: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = 5, context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None, row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None, cursor_factory: [type](https://docs.python.org/3/library/functions.html#type)[[Cursor](cursors.md#psycopg.Cursor)[Row]] | [None](https://docs.python.org/3/library/constants.html#None) = None, \*\*kwargs: [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

Connect to a database server and return a new `Connection` instance.

This is an alias of the class method `CrdbConnection.connect`.

If you need an asynchronous connection use the `AsyncCrdbConnection.connect()`
method instead.

### *class* psycopg.crdb.CrdbConnection(pgconn: PGconn, row_factory: RowFactory[Row] = <function tuple_row>)

Wrapper for a connection to a CockroachDB database.

[`psycopg.Connection`](connections.md#psycopg.Connection) subclass.

#### *classmethod* is_crdb(conn: [Connection](connections.md#psycopg.Connection)[Any] | [AsyncConnection](connections.md#psycopg.AsyncConnection)[Any] | [PGconn](pq.md#psycopg.pq.PGconn)) → [bool](https://docs.python.org/3/library/functions.html#bool)

Return `True` if the server connected to `conn` is CockroachDB.

* **Parameters:**
  **conn** ([`Connection`](connections.md#psycopg.Connection), [`AsyncConnection`](connections.md#psycopg.AsyncConnection), [`PGconn`](pq.md#psycopg.pq.PGconn)) – the connection to check

### *class* psycopg.crdb.AsyncCrdbConnection(pgconn: PGconn, row_factory: AsyncRowFactory[Row] = <function tuple_row>)

Wrapper for an async connection to a CockroachDB database.

[`psycopg.AsyncConnection`](connections.md#psycopg.AsyncConnection) subclass.

### *class* psycopg.crdb.CrdbConnectionInfo(pgconn: PGconn)

[`ConnectionInfo`](objects.md#psycopg.ConnectionInfo) subclass to get info about a CockroachDB database.

The object is returned by the [`info`](connections.md#psycopg.Connection.info) attribute of
[`CrdbConnection`](#psycopg.crdb.CrdbConnection) and [`AsyncCrdbConnection`](#psycopg.crdb.AsyncCrdbConnection).

The object behaves like `ConnectionInfo`, with the following differences:

#### vendor

The `CockroachDB` string.

#### server_version

Return the CockroachDB server version connected.

Return a number in the PostgreSQL format (e.g. 21.2.10 -> 210210).

### psycopg.crdb.adapters

The default adapters map establishing how Python and CockroachDB types are
converted into each other.

The map is used as a template when new connections are created, using
[`psycopg.crdb.connect()`](#psycopg.crdb.connect) (similarly to the way [`psycopg.adapters`](module.md#psycopg.adapters) is used
as template for new PostgreSQL connections).

This registry contains only the types and adapters supported by
CockroachDB. Several PostgreSQL types and adapters are missing or
different from PostgreSQL, among which:

- Composite types
- `range`, `multirange` types
- The `hstore` type
- Geometric types
- Nested arrays
- Arrays of `jsonb`
- The `cidr` data type
- The `json` type is an alias for `jsonb`
- The `int` type is an alias for `int8`, not `int4`.

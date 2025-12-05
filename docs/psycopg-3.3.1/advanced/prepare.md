<a id="index-0"></a>

<a id="prepared-statements"></a>

# Prepared statements

Psycopg uses an automatic system to manage *prepared statements*. When a
query is prepared, its parsing and planning is stored in the server session,
so that further executions of the same query on the same connection (even with
different parameters) are optimised.

A query is prepared automatically after it is executed more than
[`prepare_threshold`](../api/connections.md#psycopg.Connection.prepare_threshold) times on a connection. `psycopg` will make
sure that no more than [`prepared_max`](../api/connections.md#psycopg.Connection.prepared_max) statements are planned: if
further queries are executed, the least recently used ones are deallocated and
the associated resources freed.

Statement preparation can be controlled in several ways:

- You can decide to prepare a query immediately by passing `prepare=True` to
  [`Connection.execute()`](../api/connections.md#psycopg.Connection.execute) or [`Cursor.execute()`](../api/cursors.md#psycopg.Cursor.execute). The query is prepared, if it
  wasn’t already, and executed as prepared from its first use.
- Conversely, passing `prepare=False` to `execute()` will avoid to prepare
  the query, regardless of the number of times it is executed. The default for
  the parameter is `None`, meaning that the query is prepared if the
  conditions described above are met.
- You can disable the use of prepared statements on a connection by setting
  its [`prepare_threshold`](../api/connections.md#psycopg.Connection.prepare_threshold) attribute to `None`.

#### Versionchanged
Changed in version 3.1: You can set `prepare_threshold` as a [`connect()`](../api/connections.md#psycopg.Connection.connect) keyword
parameter too.

#### SEE ALSO
The [PREPARE](https://www.postgresql.org/docs/current/sql-prepare.html) PostgreSQL documentation contains plenty of details about
prepared statements in PostgreSQL.

Note however that Psycopg doesn’t use SQL statements such as
`PREPARE` and `EXECUTE`, but protocol level commands such as the
ones exposed by `[PQsendPrepare](https://www.postgresql.org/docs/18/libpq-async.html#LIBPQ-PQSENDPREPARE)`, `[PQsendQueryPrepared](https://www.postgresql.org/docs/18/libpq-async.html#LIBPQ-PQSENDQUERYPREPARED)`.

<a id="pgbouncer"></a>

## Using prepared statements with PgBouncer

#### WARNING
Unless a connection pooling middleware explicitly declares otherwise, they
are not compatible with prepared statements, because the same client
connection may change the server session it refers to. If such middleware
is used you should disable prepared statements, by setting the
[`Connection.prepare_threshold`](../api/connections.md#psycopg.Connection.prepare_threshold) attribute to `None`.

Starting from 3.2, Psycopg supports prepared statements when using the
[PgBouncer](https://www.pgbouncer.org/) middleware, using the following caveats:

- PgBouncer version must be version [1.22](https://www.pgbouncer.org/2024/01/pgbouncer-1-22-0) or newer.
- PgBouncer [max_prepared_statements](https://www.pgbouncer.org/config.html#max_prepared_statements) must be greater than 0.
- The libpq version on the client must be from PostgreSQL 17 or newer
  (you can check the [`has_send_close_prepared()`](../api/objects.md#psycopg.Capabilities.has_send_close_prepared) capability to
  verify that the libpq implements the features required by PgBouncer).

#### HINT
If libpq 17 is not available on your client, but PgBouncer is 1.22 or
higher, you can still use Psycopg *as long as you disable deallocation*.

You can do so by setting [`Connection.prepared_max`](../api/connections.md#psycopg.Connection.prepared_max) to `None`.

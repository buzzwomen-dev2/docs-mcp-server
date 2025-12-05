<a id="index-0"></a>

<a id="from-psycopg2"></a>

# Differences from `psycopg2`

Psycopg 3 uses the common DBAPI structure of many other database adapters and
tries to behave as close as possible to `psycopg2`. There are however a few
differences to be aware of.

<a id="install-difference"></a>

## Which package to install?

#### IMPORTANT
- If you were installing `psycopg2-binary` you should now install
  `psycopg[binary]` instead.
- If you were installing `psycopg2`, therefore your client has the
  prerequisites to build the C extension yourself, you can install
  `psycopg[c]` instead.

Please see the [installation](install.md#installation) section for all the details.

Rationale: both the `psycopg2` and the `psycopg2-binary` distribution
packages install the `psycopg2` Python package. This scenario is not well
covered by Python packaging metadata, resulting in complex dependencies
management and problems if both the packages are installed.

In Psycopg 3 there is a clear “interface” package, `psycopg`, and optional
speed-up extensions that can be included in the dependencies of a service (but
don’t need to – and shouldn’t be – included in the dependencies of a
library). See [Handling dependencies](install.md#install-dependencies) for more details.

<a id="server-side-binding"></a>

## Server-side binding

Psycopg 3 sends the query and the parameters to the server separately, instead
of merging them on the client side. Server-side binding works for normal
`SELECT` and data manipulation statements (`INSERT`, `UPDATE`,
`DELETE`), but it doesn’t work with many other statements. For instance,
it doesn’t work with `SET` or with `NOTIFY`:

```default
>>> conn.execute("SET TimeZone TO %s", ["UTC"])
Traceback (most recent call last):
...
psycopg.errors.SyntaxError: syntax error at or near "$1"
LINE 1: SET TimeZone TO $1
                        ^

>>> conn.execute("NOTIFY %s, %s", ["chan", 42])
Traceback (most recent call last):
...
psycopg.errors.SyntaxError: syntax error at or near "$1"
LINE 1: NOTIFY $1, $2
               ^
```

and with any data definition statement:

```default
>>> conn.execute("CREATE TABLE foo (id int DEFAULT %s)", [42])
Traceback (most recent call last):
...
psycopg.errors.UndefinedParameter: there is no parameter $1
LINE 1: CREATE TABLE foo (id int DEFAULT $1)
                                         ^
```

Sometimes, PostgreSQL offers an alternative: for instance the [set_config()](https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADMIN-SET)
function can be used instead of the `SET` statement, the [pg_notify()](https://www.postgresql.org/docs/current/sql-notify.html#id-1.9.3.157.7.5)
function can be used instead of `NOTIFY`:

```default
>>> conn.execute("SELECT set_config('TimeZone', %s, false)", ["UTC"])

>>> conn.execute("SELECT pg_notify(%s, %s)", ["chan", "42"])
```

If this is not possible, you must merge the query and the parameter on the
client side. You can do so using the [`psycopg.sql`](../api/sql.md#module-psycopg.sql) objects:

```default
>>> from psycopg import sql

>>> cur.execute(sql.SQL("CREATE TABLE foo (id int DEFAULT {})").format(42))
```

or creating a [client-side binding cursor](../advanced/cursors.md#client-side-binding-cursors)
such as [`ClientCursor`](../api/cursors.md#psycopg.ClientCursor):

```default
>>> cur = ClientCursor(conn)
>>> cur.execute("CREATE TABLE foo (id int DEFAULT %s)", [42])
```

If you need `ClientCursor` often, you can set the [`Connection.cursor_factory`](../api/connections.md#psycopg.Connection.cursor_factory)
to have them created by default by [`Connection.cursor()`](../api/connections.md#psycopg.Connection.cursor). This way, Psycopg 3
will behave largely the same way of Psycopg 2.

Note that, both server-side and client-side, you can only specify **values**
as parameters (i.e. *the strings that go in single quotes*). If you need to
parametrize different parts of a statement (such as a table name), you must
use the [`psycopg.sql`](../api/sql.md#module-psycopg.sql) module:

```default
>>> from psycopg import sql

# This will quote the user and the password using the right quotes
# e.g.: ALTER USER "foo" SET PASSWORD 'bar'
>>> conn.execute(
...     sql.SQL("ALTER USER {} SET PASSWORD {}")
...     .format(sql.Identifier(username), password))
```

<a id="index-1"></a>

<a id="advanced-query-protocol"></a>

## Extended query Protocol

In order to use [Server-side binding](#server-side-binding), psycopg normally uses the
[extended query protocol](https://www.postgresql.org/docs/current/protocol-flow.html#PROTOCOL-FLOW-EXT-QUERY) to communicate with the backend.

In certain context outside pure PostgreSQL, the extended query protocol is not
supported, for instance to query the [PgBouncer admin console](https://www.pgbouncer.org/usage.html#admin-console). In this case
you should probably use a [`ClientCursor`](../api/cursors.md#psycopg.ClientCursor). See [Simple query protocol](../advanced/cursors.md#simple-query-protocol) for
details.

<a id="multi-statements"></a>

## Multiple statements in the same query

As a consequence of using [server-side bindings](#server-side-binding),
when parameters are used, it is not possible to execute several statements in
the same `execute()` call, separating them by semicolon:

```default
>>> conn.execute(
...     "INSERT INTO foo VALUES (%s); INSERT INTO foo VALUES (%s)",
...     (10, 20))
Traceback (most recent call last):
...
psycopg.errors.SyntaxError: cannot insert multiple commands into a prepared statement
```

One obvious way to work around the problem is to use several `execute()`
calls.

**There is no such limitation if no parameters are used**. As a consequence, you
can compose a multiple query on the client side and run them all in the same
`execute()` call, using the [`psycopg.sql`](../api/sql.md#module-psycopg.sql) objects:

```default
>>> from psycopg import sql
>>> conn.execute(
...     sql.SQL("INSERT INTO foo VALUES ({}); INSERT INTO foo values ({})")
...     .format(10, 20))
```

or a [client-side binding cursor](../advanced/cursors.md#client-side-binding-cursors):

```default
>>> cur = psycopg.ClientCursor(conn)
>>> cur.execute(
...     "INSERT INTO foo VALUES (%s); INSERT INTO foo VALUES (%s)",
...     (10, 20))
```

#### WARNING
You cannot execute multiple statements in the same query:

- when retrieving a [binary result](params.md#binary-data) (such as using
  `.execute(..., binary=True)`;
- when using the [pipeline mode](../advanced/pipeline.md#pipeline-mode).

#### WARNING
If a statement must be executed outside a transaction (such as
`CREATE DATABASE`), it cannot be executed in batch with other
statements, even if the connection is in autocommit mode:

```default
>>> conn.autocommit = True
>>> conn.execute("CREATE DATABASE foo; SELECT 1")
Traceback (most recent call last):
...
psycopg.errors.ActiveSqlTransaction: CREATE DATABASE cannot run inside a transaction block
```

This happens because PostgreSQL itself will wrap multiple statements in a
transaction. Note that you will experience a different behaviour in
**psql** (**psql** will split the queries on semicolons and
send them to the server separately).

This is not new in Psycopg 3: the same limitation is present in
`psycopg2` too.

<a id="multi-results"></a>

## Multiple results returned from multiple statements

If more than one statement returning results is executed in psycopg2, only the
result of the last statement is returned:

```default
>>> cur_pg2.execute("SELECT 1; SELECT 2")
>>> cur_pg2.fetchone()
(2,)
```

In Psycopg 3 instead, all the results are available. After running the query,
the first result will be readily available in the cursor and can be consumed
using the usual `fetch*()` methods. In order to access the following
results, you can use the [`Cursor.results()`](../api/cursors.md#psycopg.Cursor.results) method (or [`nextset()`](../api/cursors.md#psycopg.Cursor.nextset)
before Psycopg 3.3):

```default
>>> cur_pg3.execute("SELECT 1; SELECT 2")
>>> for _ in cur_pg3.results():
...    print(cur_pg3.fetchone())
(1,)
(2,)
```

Remember though that you cannot use server-side bindings to [execute more
than one statement in the same query](#multi-statements), if you are passing
parameters to the query.

<a id="difference-cast-rules"></a>

## Different cast rules

In rare cases, especially around variadic functions, PostgreSQL might fail to
find a function candidate for the given data types:

```default
>>> conn.execute("SELECT json_build_array(%s, %s)", ["foo", "bar"])
Traceback (most recent call last):
...
psycopg.errors.IndeterminateDatatype: could not determine data type of parameter $1
```

This can be worked around specifying the argument types explicitly via a cast:

```default
>>> conn.execute("SELECT json_build_array(%s::text, %s::text)", ["foo", "bar"])
```

<a id="in-and-tuple"></a>

## You cannot use `IN %s` with a tuple

`IN` cannot be used with a tuple as single parameter, as was possible with
`psycopg2`:

```default
>>> conn.execute("SELECT * FROM foo WHERE id IN %s", [(10,20,30)])
Traceback (most recent call last):
...
psycopg.errors.SyntaxError: syntax error at or near "$1"
LINE 1: SELECT * FROM foo WHERE id IN $1
                                      ^
```

What you can do is to use the [= ANY()](https://www.postgresql.org/docs/current/functions-comparisons.html#id-1.5.8.30.16) construct and pass the candidate
values as a list instead of a tuple, which will be adapted to a PostgreSQL
array:

```default
>>> conn.execute("SELECT * FROM foo WHERE id = ANY(%s)", [[10,20,30]])
```

Note that `ANY()` can be used with `psycopg2` too, and has the advantage of
accepting an empty list of values too as argument, which is not supported by
the `IN` operator instead.

<a id="is-null"></a>

## You cannot use `IS %s`

You cannot use `IS %s` or `IS NOT %s`:

```default
>>> conn.execute("SELECT * FROM foo WHERE field IS %s", [None])
Traceback (most recent call last):
...
psycopg.errors.SyntaxError: syntax error at or near "$1"
LINE 1: SELECT * FROM foo WHERE field IS $1
                                     ^
```

This is probably caused by the fact that `IS` is not a binary predicate in
PostgreSQL; rather, `IS NULL` and `IS NOT NULL` are unary predicates
and you cannot use `IS` with anything else on the right hand side.
Testing in psql:

```text
=# SELECT 10 IS 10;
ERROR:  syntax error at or near "10"
LINE 1: SELECT 10 IS 10;
                     ^
```

What you can do is to use [IS [NOT] DISTINCT FROM](https://www.postgresql.org/docs/current/functions-comparison.html) predicate instead:
`IS NOT DISTINCT FROM %s` can be used in place of `IS %s` (please
pay attention to the awkwardly reversed `NOT`):

```default
>>> conn.execute("SELECT * FROM foo WHERE field IS NOT DISTINCT FROM %s", [None])
```

Analogously you can use `IS DISTINCT FROM %s` as a parametric version of
`IS NOT %s`.

<a id="diff-cursors"></a>

## Cursors subclasses

In `psycopg2`, a few cursor subclasses allowed to return data in different
form than tuples. In Psycopg 3 the same can be achieved by setting a [row
factory](../advanced/rows.md#row-factories):

- instead of [`RealDictCursor`](https://www.psycopg.org/docs/extras.html#psycopg2.extras.RealDictCursor) you can use
  [`dict_row`](../api/rows.md#psycopg.rows.dict_row);
- instead of [`NamedTupleCursor`](https://www.psycopg.org/docs/extras.html#psycopg2.extras.NamedTupleCursor) you can use
  [`namedtuple_row`](../api/rows.md#psycopg.rows.namedtuple_row).

Other row factories are available in the [`psycopg.rows`](../api/rows.md#module-psycopg.rows) module. There isn’t an
object behaving like [`DictCursor`](https://www.psycopg.org/docs/extras.html#psycopg2.extras.DictCursor) (whose results are
indexable both by column position and by column name).

```default
from psycopg.rows import dict_row, namedtuple_row

# By default, every cursor will return dicts.
conn = psycopg.connect(DSN, row_factory=dict_row)

# You can set a row factory on a single cursor too.
cur = conn.cursor(row_factory=namedtuple_row)
```

<a id="diff-adapt"></a>

## Different adaptation system

The adaptation system has been completely rewritten, in order to address
server-side parameters adaptation, but also to consider performance,
flexibility, ease of customization.

The default behaviour with builtin data should be [what you would expect](adapt.md#types-adaptation). If you have customised the way to adapt data, or if you
are managing your own extension types, you should look at the [new
adaptation system](../advanced/adapt.md#adaptation).

#### SEE ALSO
- [Adapting basic Python types](adapt.md#types-adaptation) for the basic behaviour.
- [Data adaptation configuration](../advanced/adapt.md#adaptation) for more advanced use.

<a id="diff-copy"></a>

## Copy is no longer file-based

`psycopg2` exposes [a few copy methods](https://www.psycopg.org/docs/usage.html#copy) to interact with
PostgreSQL `COPY`. Their file-based interface doesn’t make it easy to load
dynamically-generated data into a database.

There is now a single [`copy()`](../api/cursors.md#psycopg.Cursor.copy) method, which is similar to
`psycopg2` `copy_expert()` in accepting a free-form `COPY` command and
returns an object to read/write data, block-wise or record-wise. The different
usage pattern also enables `COPY` to be used in async interactions.

#### SEE ALSO
See [Using COPY TO and COPY FROM](copy.md#copy) for the details.

<a id="diff-with"></a>

## `with` connection

In `psycopg2`, using the syntax [with connection](https://www.psycopg.org/docs/usage.html#with),
only the transaction is closed, not the connection. This behaviour is
surprising for people used to several other Python classes wrapping resources,
such as files.

In Psycopg 3, using [with connection](usage.md#with-connection) will close the
connection at the end of the `with` block, making handling the connection
resources more familiar.

In order to manage transactions as blocks you can use the
[`Connection.transaction()`](../api/connections.md#psycopg.Connection.transaction) method, which allows for finer control, for
instance to use nested transactions.

#### SEE ALSO
See [Transaction contexts](transactions.md#transaction-context) for details.

<a id="diff-callproc"></a>

## `callproc()` is gone

`cursor.callproc()` is not implemented. The method has a simplistic semantic
which doesn’t account for PostgreSQL positional parameters, procedures,
set-returning functions… Use a normal [`execute()`](../api/cursors.md#psycopg.Cursor.execute) with `SELECT
function_name(...)` or `CALL procedure_name(...)` instead.

<a id="diff-client-encoding"></a>

## `client_encoding` is gone

Psycopg automatically uses the database client encoding to decode data to
Unicode strings. Use [`ConnectionInfo.encoding`](../api/objects.md#psycopg.ConnectionInfo.encoding) if you need to read the
encoding. You can select an encoding at connection time using the
`client_encoding` connection parameter and you can change the encoding of a
connection by running a `SET client_encoding` statement… But why would
you?

<a id="transaction-characteristics-and-autocommit"></a>

## Transaction characteristics attributes don’t affect autocommit sessions

[Transactions characteristics attributes](transactions.md#transaction-characteristics)
such as [`read_only`](../api/connections.md#psycopg.Connection.read_only) don’t affect automatically autocommit
sessions: they only affect the implicit transactions started by non-autocommit
sessions and the transactions created by the [`transaction()`](../api/connections.md#psycopg.Connection.transaction)
block (for both autocommit and non-autocommit connections).

If you want to put an autocommit transaction in read-only mode, please use the
[default_transaction_read_only](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-DEFAULT-TRANSACTION-READ-ONLY) GUC, for instance executing the statement
`SET default_transaction_read_only TO true`.

<a id="infinity-datetime"></a>

## No default infinity dates handling

PostgreSQL can represent a much wider range of dates and timestamps than
Python. While Python dates are limited to the years between 1 and 9999
(represented by constants such as [`datetime.date.min`](https://docs.python.org/3/library/datetime.html#datetime.date.min) and
[`max`](https://docs.python.org/3/library/datetime.html#datetime.date.max)), PostgreSQL dates extend to BC dates and past the year
10K. Furthermore PostgreSQL can also represent symbolic dates “infinity”, in
both directions.

In psycopg2, by default, [infinity dates and timestamps map to ‘date.max’](https://www.psycopg.org/docs/usage.html#infinite-dates-handling)
and similar constants. This has the problem of creating a non-bijective
mapping (two Postgres dates, infinity and 9999-12-31, both map to the same
Python date). There is also the perversity that valid Postgres dates, greater
than Python `date.max` but arguably lesser than infinity, will still
overflow.

In Psycopg 3, every date greater than year 9999 will overflow, including
infinity. If you would like to customize this mapping (for instance flattening
every date past Y10K on `date.max`) you can subclass and adapt the
appropriate loaders: take a look at [this example](../advanced/adapt.md#adapt-example-inf-date) to see how.

<a id="whats-new"></a>

## What’s new in Psycopg 3

- [Asynchronous support](../advanced/async.md#async)
- [Server-side parameters binding](#server-side-binding)
- [Prepared statements](../advanced/prepare.md#prepared-statements)
- [Binary communication](params.md#binary-data)
- [Python-based COPY support](copy.md#copy)
- [Support for static typing](../advanced/typing.md#static-typing)
- [A redesigned connection pool](../advanced/pool.md#connection-pools)
- [Direct access to the libpq functionalities](../api/pq.md#psycopg-pq)

# Cursor classes

The [`Cursor`](#psycopg.Cursor) and [`AsyncCursor`](#psycopg.AsyncCursor) classes are the main objects to send commands
to a PostgreSQL database session. They are normally created by the
connection’s [`cursor()`](connections.md#psycopg.Connection.cursor) method.

Using the `name` parameter on `cursor()` will create a [`ServerCursor`](#psycopg.ServerCursor) or
[`AsyncServerCursor`](#psycopg.AsyncServerCursor), which can be used to retrieve partial results from a
database.

Other cursor classes can be created by directly instantiating them, or can be
set as [`Connection.cursor_factory`](connections.md#psycopg.Connection.cursor_factory) to require them on `cursor()` call.

This page describe the details of the `Cursor` class interface. Please refer
to [Cursor types](../advanced/cursors.md#cursor-types) for general information about the different types of
cursors available in Psycopg.

## The `Cursor` class

### *class* psycopg.Cursor(connection: [Connection](connections.md#psycopg.Connection)[Any], , row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None)

This class implements a [DBAPI-compliant interface](https://www.python.org/dev/peps/pep-0249/#cursor-objects). It is what the
classic [`Connection.cursor()`](connections.md#psycopg.Connection.cursor) method returns. [`AsyncConnection.cursor()`](connections.md#psycopg.AsyncConnection.cursor)
will create instead [`AsyncCursor`](#psycopg.AsyncCursor) objects, which have the same set of
method but expose an [`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio) interface and require `async` and
`await` keywords to operate.

Cursors behave as context managers: on block exit they are closed and
further operation will not be possible. Closing a cursor will not
terminate a transaction or a session though.

#### connection *: [Connection](connections.md#psycopg.Connection)*

The connection this cursor is using.

#### adapters *: [AdaptersMap](adapt.md#psycopg.adapt.AdaptersMap)*

The adapters configuration used to convert Python parameters and
PostgreSQL results for the queries executed on this cursor.

#### Versionchanged
Changed in version 3.3: reconfiguring loaders using [`register_loader()`](adapt.md#psycopg.adapt.AdaptersMap.register_loader)
affects the results of a query already executed.

#### close() → [None](https://docs.python.org/3/library/constants.html#None)

Close the current cursor and free associated resources.

#### NOTE
You can use:

```default
with conn.cursor() as cur:
    ...
```

to close the cursor automatically when the block is exited. See
[Main objects in Psycopg 3](../basic/usage.md#usage).

#### closed

[`True`](https://docs.python.org/3/library/constants.html#True) if the cursor is closed.

### Methods to send commands

#### execute(query: QueryNoTemplate, params: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [None](https://docs.python.org/3/library/constants.html#None) = None, , prepare: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, binary: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

#### execute(query: Template, , prepare: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, binary: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

Execute a query or command to the database.

* **Parameters:**
  * **query** ([`LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString), `bytes`, [`sql.SQL`](sql.md#psycopg.sql.SQL), [`sql.Composed`](sql.md#psycopg.sql.Composed),
    or [`Template`](https://docs.python.org/3/library/string.templatelib.html#string.templatelib.Template)) – The query to execute.
  * **params** (*Sequence* *or* *Mapping*) – The parameters to pass to the query, if any.
    Can’t be specified if `query` is a `Template`.
  * **prepare** – Force (`True`) or disallow (`False`) preparation of
    the query. By default (`None`) prepare automatically. See
    [Prepared statements](../advanced/prepare.md#prepared-statements).
  * **binary** – Specify whether the server should return data in binary
    format (`True`) or in text format (`False`). By default
    (`None`) return data as requested by the cursor’s [`format`](#psycopg.Cursor.format).

Return the cursor itself, so that it will be possible to chain a fetch
operation after the call.

See [Passing parameters to SQL queries](../basic/params.md#query-parameters) for all the details about executing
queries.

#### Versionchanged
Changed in version 3.1: The `query` argument must be a `StringLiteral`. If you
need to compose a query dynamically, please use [`sql.SQL`](sql.md#psycopg.sql.SQL) and
related objects.

See [**PEP 675**](https://peps.python.org/pep-0675/) for details.

#### executemany(query: Query, params_seq: Iterable[Params], , returning: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [None](https://docs.python.org/3/library/constants.html#None)

Execute the same command with a sequence of input data.

* **Parameters:**
  * **query** ([`LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString), `bytes`, [`sql.SQL`](sql.md#psycopg.sql.SQL), or [`sql.Composed`](sql.md#psycopg.sql.Composed)) – The query to execute
  * **params_seq** (*Sequence* *of* *Sequences* *or* *Mappings*) – The parameters to pass to the query
  * **returning** (`bool`) – If `True`, fetch the results of the queries executed

This is more efficient than performing separate queries, but in case of
several `INSERT` (and with some SQL creativity for massive
`UPDATE` too) you may consider using [`copy()`](#psycopg.Cursor.copy).

If the queries return data you want to read (e.g. when executing an
`INSERT ... RETURNING` or a `SELECT` with a side-effect),
you can specify `returning=True`. This is equivalent of calling
[`execute()`](#psycopg.Cursor.execute) as many times as the number of items in
`params_seq`, and to store all the results in the cursor’s state.

#### NOTE
Using the usual [`fetchone()`](#psycopg.Cursor.fetchone), [`fetchall()`](#psycopg.Cursor.fetchall), you
will be able to read the records returned *by the first query
executed only*. In order to read the results of the following
queries you can call [`nextset()`](#psycopg.Cursor.nextset) or [`results()`](#psycopg.Cursor.results) to move across the
result set.

A typical use case for `executemany(returning=True)` might be to
insert a bunch of records and to retrieve the primary keys
inserted, taken from a PostgreSQL sequence. In order to do so, you
may execute a query such as `INSERT INTO table VALUES (...)
RETURNING id`. Because every `INSERT` is guaranteed to insert
exactly a single record, you can obtain the list of the new ids
using a pattern such as:

```default
cur.executemany(query, records)
ids = [cur.fetchone()[0] for _ in cur.results()]
```

#### WARNING
More explicitly, `fetchall()` alone will not return all the
values returned! You must iterate on the results using
[`results()`](#psycopg.Cursor.results).

If `returning=False`, the value of [`rowcount`](#psycopg.Cursor.rowcount) is set to the cumulated
number of rows affected by queries. If `returning=True`, `rowcount`
is set to the number of rows in the current result set (i.e. the first
one, until [`nextset()`](#psycopg.Cursor.nextset) gets called).

See [Passing parameters to SQL queries](../basic/params.md#query-parameters) for all the details about executing
queries.

#### Versionchanged
Changed in version 3.1: 

- Added `returning` parameter to receive query results.
- Performance optimised by making use of the pipeline mode, when
  using libpq 14 or newer.

#### copy(statement: Query, params: Params | [None](https://docs.python.org/3/library/constants.html#None) = None, , writer: [Writer](copy.md#psycopg.copy.Writer) | [None](https://docs.python.org/3/library/constants.html#None) = None) → Iterator[[Copy](copy.md#psycopg.Copy)]

Initiate a `COPY` operation and return an object to manage it.

* **Parameters:**
  * **statement** (`str`, `bytes`, [`sql.SQL`](sql.md#psycopg.sql.SQL), or [`sql.Composed`](sql.md#psycopg.sql.Composed)) – The copy operation to execute
  * **params** (*Sequence* *or* *Mapping*) – The parameters to pass to the statement, if any.

#### NOTE
The method must be called with:

```default
with cursor.copy() as copy:
    ...
```

See [Using COPY TO and COPY FROM](../basic/copy.md#copy) for information about `COPY`.

#### Versionchanged
Changed in version 3.1: Added parameters support.

#### stream(query: Query, params: Params | [None](https://docs.python.org/3/library/constants.html#None) = None, , binary: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, size: [int](https://docs.python.org/3/library/functions.html#int) = 1) → Iterator[Row]

Iterate row-by-row on a result from the database.

* **Parameters:**
  **size** – if greater than 1, results will be retrieved by chunks of
  this size from the server (but still yielded row-by-row); this is only
  available from version 17 of the libpq.

This command is similar to execute + iter; however it supports endless
data streams. The feature is not available in PostgreSQL, but some
implementations exist: Materialize [SUBSCRIBE](https://materialize.com/docs/sql/subscribe/) and CockroachDB
[CHANGEFEED](https://www.cockroachlabs.com/docs/stable/changefeed-for.html) for instance.

The feature, and the API supporting it, are still experimental.
Beware… 👀

The parameters are the same of [`execute()`](#psycopg.Cursor.execute), except for `size` which
can be used to set results retrieval by chunks instead of row-by-row.

#### NOTE
This `size` parameter is only available from libpq 17, you can use
the [`has_stream_chunked`](objects.md#psycopg.Capabilities.has_stream_chunked) capability to check if this
is supported.

#### WARNING
Failing to consume the iterator entirely will result in a
connection left in [`transaction_status`](objects.md#psycopg.ConnectionInfo.transaction_status)
[`ACTIVE`](pq.md#psycopg.pq.TransactionStatus.ACTIVE) state: this connection will refuse
to receive further commands (with a message such as *another
command is already in progress*).

If there is a chance that the generator is not consumed entirely,
in order to restore the connection to a working state you can call
[`close`](https://docs.python.org/3/reference/expressions.html#generator.close) on the generator object returned by `stream()`. The
[`contextlib.closing`](https://docs.python.org/3/library/contextlib.html#contextlib.closing) function might be particularly useful to make
sure that `close()` is called:

```default
with closing(cur.stream("select generate_series(1, 10000)")) as gen:
    for rec in gen:
        something(rec)  # might fail
```

Without calling `close()`, in case of error, the connection will
be `ACTIVE` and unusable. If `close()` is called, the connection
might be `INTRANS` or `INERROR`, depending on whether the server
managed to send the entire resultset to the client. An autocommit
connection will be `IDLE` instead.

#### format

The format of the data returned by the queries. It can be selected
initially e.g. specifying [`Connection.cursor`](connections.md#psycopg.Connection.cursor)`(binary=True)` and
changed during the cursor’s lifetime. It is also possible  to override
the value for single queries, e.g. specifying [`execute`](#psycopg.Cursor.execute)`(binary=True)`.

* **Type:**
  [`pq.Format`](pq.md#psycopg.pq.Format)
* **Default:**
  [`TEXT`](pq.md#psycopg.pq.Format.TEXT)

#### SEE ALSO
[Binary parameters and results](../basic/params.md#binary-data)

### Methods to retrieve results

Fetch methods are only available if the current result set contains results,
e.g. a `SELECT` or a command with `RETURNING`. They will raise
an exception if used with operations that don’t return result, such as an
`INSERT` with no `RETURNING` or an `ALTER TABLE`.

#### NOTE
Cursors are iterators, so just using the:

```default
for record in cursor:
    ...
```

syntax will iterate on the records in the current result set.

#### Versionchanged
Changed in version 3.3: it is now possible to use `next(cursor)`. Previously, cursors were
[iterables](https://docs.python.org/3/glossary.html#term-iterable), not [iterators](https://docs.python.org/3/glossary.html#term-iterator).

#### row_factory

Writable attribute to control how result rows are formed.

The property affects the objects returned by the [`fetchone()`](#psycopg.Cursor.fetchone),
[`fetchmany()`](#psycopg.Cursor.fetchmany), [`fetchall()`](#psycopg.Cursor.fetchall) methods. The default
([`tuple_row`](rows.md#psycopg.rows.tuple_row)) returns a tuple for each record fetched.

See [Row factories](../advanced/rows.md#row-factories) for details.

#### fetchone() → Row | [None](https://docs.python.org/3/library/constants.html#None)

Return the next record from the current result set.

Return `None` the result set is finished.

* **Return type:**
  Row | None, with Row defined by [`row_factory`](#psycopg.Cursor.row_factory)

#### fetchmany(size: [int](https://docs.python.org/3/library/functions.html#int) = 0) → [list](https://docs.python.org/3/library/stdtypes.html#list)[Row]

Return the next `size` records from the current result set.

`size` default to `self.arraysize` if not specified.

* **Return type:**
  Sequence[Row], with Row defined by [`row_factory`](#psycopg.Cursor.row_factory)

#### fetchall() → [list](https://docs.python.org/3/library/stdtypes.html#list)[Row]

Return all the remaining records from the current result set.

* **Return type:**
  Sequence[Row], with Row defined by [`row_factory`](#psycopg.Cursor.row_factory)

#### nextset() → [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None)

Move to the result set of the next query executed through [`executemany()`](#psycopg.Cursor.executemany)
or to the next result set if [`execute()`](#psycopg.Cursor.execute) returned more than one.

Return `True` if a new result is available, which will be the one
methods `fetch*()` will operate on.

#### results() → [Iterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[Self](https://docs.python.org/3/library/typing.html#typing.Self)]

Iterate across multiple record sets received by the cursor.

Multiple record sets are received after using [`executemany()`](#psycopg.Cursor.executemany) with
`returning=True` or using [`execute()`](#psycopg.Cursor.execute) with more than one query in the
command.

The iterator yields the cursor itself upon iteration, but the cursor
state changes, in a way equivalent to calling [`nextset()`](#psycopg.Cursor.nextset) in a loop.
Therefore you can ignore the result of the iteration if you are consuming
`results()` in a loop:

```default
for _ in cursor.results():
    for row in cursor:
        ...
```

or make use of it for example using `map()` to consume the iterator:

```default
def cursor_consumer(cur: Cursor) -> Any:
    ...

map(cursor_consumer, cursor.results())
```

#### Versionadded
Added in version 3.3: In previous version you may call [`nextset()`](#psycopg.Cursor.nextset) in a loop until it
returns a false value.

#### set_result(index: [int](https://docs.python.org/3/library/functions.html#int)) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

Move to a specific result set.

* **Parameters:**
  **index** (`int`) – index of the result to go to

More than one result will be available after executing calling
[`executemany()`](#psycopg.Cursor.executemany) or [`execute()`](#psycopg.Cursor.execute) with more than one query.

`index` is 0-based and supports negative values, counting from the end,
the same way you can index items in a list.

The function returns self, so that the result may be followed by a
fetch operation. See [`results()`](#psycopg.Cursor.results) for details.

#### Versionadded
Added in version 3.3.

#### scroll(value: [int](https://docs.python.org/3/library/functions.html#int), mode: [str](https://docs.python.org/3/library/stdtypes.html#str) = 'relative') → [None](https://docs.python.org/3/library/constants.html#None)

Move the cursor in the result set to a new position according to mode.

If `mode` is `'relative'` (default), `value` is taken as offset to
the current position in the result set; if set to `'absolute'`,
`value` states an absolute target position.

Raise `IndexError` in case a scroll operation would leave the result
set. In this case the position will not change.

#### pgresult *: [psycopg.pq.PGresult](pq.md#psycopg.pq.PGresult) | [None](https://docs.python.org/3/library/constants.html#None)*

Representation of the current result set, if available, else `None`.

It can be used to obtain low level info about the current result set
and to access to features not currently wrapped by Psycopg.

### Information about the data

#### description

A list of [`Column`](objects.md#psycopg.Column) objects describing the current resultset.

`None` if the current resultset didn’t return tuples.

#### statusmessage

The status tag of the current result set.

`None` if the cursor doesn’t have a result available.

This is the status tag you typically see in **psql** after
a successful command, such as `CREATE TABLE` or `UPDATE 42`.

#### rowcount

Number of records affected by the operation that produced
the current result set.

From [`executemany()`](#psycopg.Cursor.executemany), unless called with `returning=True`, this is
the cumulated number of rows affected by executed commands.

#### rownumber

Index of the next row to fetch in the current result set.

`None` if there is no result to fetch.

#### \_query

An helper object used to convert queries and parameters before sending
them to PostgreSQL.

#### NOTE
This attribute is exposed because it might be helpful to debug
problems when the communication between Python and PostgreSQL
doesn’t work as expected. For this reason, the attribute is
available when a query fails too.

#### WARNING
You shouldn’t consider it part of the public interface of the
object: it might change without warnings.

Except this warning, I guess.

If you would like to build reliable features using this object,
please get in touch so we can try and design an useful interface
for it.

Among the properties currently exposed by this object:

- `query` (`bytes`): the query effectively sent to PostgreSQL. It
  will have Python placeholders (`%s`-style) replaced with
  PostgreSQL ones (`$1`, `$2`-style).
- `params` (sequence of `bytes`): the parameters passed to
  PostgreSQL, adapted to the database format.
- `types` (sequence of `int`): the OID of the parameters passed to
  PostgreSQL.
- `formats` (sequence of [`pq.Format`](pq.md#psycopg.pq.Format)): whether the parameter format
  is text or binary.

## The `ClientCursor` class

#### SEE ALSO
See [Client-side-binding cursors](../advanced/cursors.md#client-side-binding-cursors) for details.

### *class* psycopg.ClientCursor(connection: [Connection](connections.md#psycopg.Connection)[Any], , row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None)

This [`Cursor`](#psycopg.Cursor) subclass has exactly the same interface of its parent class,
but, instead of sending query and parameters separately to the server, it
merges them on the client and sends them as a non-parametric query on the
server. This allows, for instance, to execute parametrized data definition
statements and other [problematic queries](../basic/from_pg2.md#server-side-binding).

#### Versionadded
Added in version 3.1.

#### mogrify(query: Query, params: Params | [None](https://docs.python.org/3/library/constants.html#None) = None) → [str](https://docs.python.org/3/library/stdtypes.html#str)

Return the query and parameters merged.

Parameters are adapted and merged to the query the same way that
`execute()` would do.

* **Parameters:**
  * **query** (`str`, `bytes`, [`sql.SQL`](sql.md#psycopg.sql.SQL), or [`sql.Composed`](sql.md#psycopg.sql.Composed)) – The query to execute.
  * **params** (*Sequence* *or* *Mapping*) – The parameters to pass to the query, if any.

## The `ServerCursor` class

#### SEE ALSO
See [Server-side cursors](../advanced/cursors.md#server-side-cursors) for details.

### *class* psycopg.ServerCursor(connection: [Connection](connections.md#psycopg.Connection)[Any], name: [str](https://docs.python.org/3/library/stdtypes.html#str), , row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None, scrollable: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, withhold: [bool](https://docs.python.org/3/library/functions.html#bool) = False)

This class also implements a [DBAPI-compliant interface](https://www.python.org/dev/peps/pep-0249/#cursor-objects). It is created
by [`Connection.cursor()`](connections.md#psycopg.Connection.cursor) specifying the `name` parameter. Using this
object results in the creation of an equivalent PostgreSQL cursor in the
server. DBAPI-extension methods (such as [`copy()`](#psycopg.Cursor.copy) or
[`stream()`](#psycopg.Cursor.stream)) are not implemented on this object: use a normal
[`Cursor`](#psycopg.Cursor) instead.

Most attribute and methods behave exactly like in [`Cursor`](#psycopg.Cursor), here are
documented the differences:

#### name

The name of the cursor.

#### scrollable

Whether the cursor is scrollable or not.

If `None` leave the choice to the server. Use `True` if you want to
use [`scroll()`](#psycopg.ServerCursor.scroll) on the cursor.

#### SEE ALSO
The PostgreSQL [DECLARE](https://www.postgresql.org/docs/current/sql-declare.html) statement documentation
for the description of `[NO] SCROLL`.

#### withhold

If the cursor can be used after the creating transaction has committed.

#### SEE ALSO
The PostgreSQL [DECLARE](https://www.postgresql.org/docs/current/sql-declare.html) statement documentation
for the description of `{WITH|WITHOUT} HOLD`.

#### close() → [None](https://docs.python.org/3/library/constants.html#None)

Close the current cursor and free associated resources.

#### WARNING
Closing a server-side cursor is more important than
closing a client-side one because it also releases the resources
on the server, which otherwise might remain allocated until the
end of the session (memory, locks). Using the pattern:

```default
with conn.cursor():
    ...
```

is especially useful so that the cursor is closed at the end of
the block.

#### execute(query: Query, params: Params | [None](https://docs.python.org/3/library/constants.html#None) = None, , binary: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, \*\*kwargs: Any) → Self

Open a cursor to execute a query to the database.

* **Parameters:**
  * **query** ([`LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString), `bytes`, [`sql.SQL`](sql.md#psycopg.sql.SQL), [`sql.Composed`](sql.md#psycopg.sql.Composed),
    or [`Template`](https://docs.python.org/3/library/string.templatelib.html#string.templatelib.Template)) – The query to execute.
  * **params** (*Sequence* *or* *Mapping*) – The parameters to pass to the query, if any.
    Can’t be specified if `query` is a `Template`.
  * **binary** – Specify whether the server should return data in binary
    format (`True`) or in text format (`False`). By default
    (`None`) return data as requested by the cursor’s [`format`](#psycopg.Cursor.format).

Create a server cursor with given `name` and the `query` in argument.

If using `DECLARE` is not appropriate (for instance because the
cursor is returned by calling a stored procedure) you can avoid to use
`execute()`, crete the cursor in other ways, and use directly the
`fetch*()` methods instead. See [“Stealing” an existing cursor](../advanced/cursors.md#cursor-steal) for an example.

Using `execute()` more than once will close the previous cursor and
open a new one with the same name.

#### executemany(query: Query, params_seq: Iterable[Params], , returning: [bool](https://docs.python.org/3/library/functions.html#bool) = True) → [None](https://docs.python.org/3/library/constants.html#None)

Method not implemented for server-side cursors.

#### fetchone() → Row | [None](https://docs.python.org/3/library/constants.html#None)

Return the next record from the current result set.

Return `None` the result set is finished.

* **Return type:**
  Row | None, with Row defined by `row_factory`

#### fetchmany(size: [int](https://docs.python.org/3/library/functions.html#int) = 0) → [list](https://docs.python.org/3/library/stdtypes.html#list)[Row]

Return the next `size` records from the current result set.

`size` default to `self.arraysize` if not specified.

* **Return type:**
  Sequence[Row], with Row defined by `row_factory`

#### fetchall() → [list](https://docs.python.org/3/library/stdtypes.html#list)[Row]

Return all the remaining records from the current result set.

* **Return type:**
  Sequence[Row], with Row defined by `row_factory`

These methods use the [FETCH](https://www.postgresql.org/docs/current/sql-fetch.html) SQL statement to retrieve some of the
records from the cursor’s current position.

#### NOTE
You can also iterate on the cursor to read its result one at
time with:

```default
for record in cur:
    ...
```

In this case, the records are not fetched one at time from the
server but they are retrieved in batches of [`itersize`](#psycopg.ServerCursor.itersize) to reduce
the number of server roundtrips.

#### itersize *: [int](https://docs.python.org/3/library/functions.html#int)*

Number of records to fetch at time when iterating on the cursor. The
default is 100.

#### scroll(value: [int](https://docs.python.org/3/library/functions.html#int), mode: [str](https://docs.python.org/3/library/stdtypes.html#str) = 'relative') → [None](https://docs.python.org/3/library/constants.html#None)

Move the cursor in the result set to a new position according to mode.

If `mode` is `'relative'` (default), `value` is taken as offset to
the current position in the result set; if set to `'absolute'`,
`value` states an absolute target position.

Raise `IndexError` in case a scroll operation would leave the result
set. In this case the position will not change.

This method uses the [MOVE](https://www.postgresql.org/docs/current/sql-fetch.html) SQL statement to move the current position
in the server-side cursor, which will affect following `fetch*()`
operations. If you need to scroll backwards you should probably
call [`cursor()`](connections.md#psycopg.Connection.cursor) using `scrollable=True`.

Note that PostgreSQL doesn’t provide a reliable way to report when a
cursor moves out of bound, so the method might not raise `IndexError`
when it happens, but it might rather stop at the cursor boundary.

## The `RawCursor` and `RawServerCursor` class

#### SEE ALSO
See [Raw query cursors](../advanced/cursors.md#raw-query-cursors) for details.

### *class* psycopg.RawCursor(connection: [Connection](connections.md#psycopg.Connection)[Any], , row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None)

This [`Cursor`](#psycopg.Cursor) subclass has the same interface of the parent class but
supports placeholders in PostgreSQL format (`$1`, `$2`…) rather than
in Python format (`%s`). Only positional parameters are supported.

#### Versionadded
Added in version 3.2.

### *class* psycopg.RawServerCursor(connection: [Connection](connections.md#psycopg.Connection)[Any], name: [str](https://docs.python.org/3/library/stdtypes.html#str), , row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None, scrollable: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, withhold: [bool](https://docs.python.org/3/library/functions.html#bool) = False)

This [`ServerCursor`](#psycopg.ServerCursor) subclass has the same interface of the parent class but
supports placeholders in PostgreSQL format (`$1`, `$2`…) rather than
in Python format (`%s`). Only positional parameters are supported.

#### Versionadded
Added in version 3.2.

## Async cursor classes

Every [`Cursor`](#psycopg.Cursor) class has an equivalent `Async` version exposing the same
semantic with an `async` interface. The main interface is described in
[`AsyncCursor`](#psycopg.AsyncCursor).

### *class* psycopg.AsyncCursor(connection: [AsyncConnection](connections.md#psycopg.AsyncConnection)[Any], , row_factory: [AsyncRowFactory](rows.md#psycopg.rows.AsyncRowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None)

This class implements a DBAPI-inspired interface, with all the blocking
methods implemented as coroutines. Unless specified otherwise,
non-blocking methods are shared with the [`Cursor`](#psycopg.Cursor) class.

The following methods have the same behaviour of the matching `Cursor`
methods, but should be called using the `await` keyword.

#### connection *: [AsyncConnection](connections.md#psycopg.AsyncConnection)*

#### *async* close() → [None](https://docs.python.org/3/library/constants.html#None)

Close the current cursor and free associated resources.

#### NOTE
You can use:

```default
async with conn.cursor():
    ...
```

to close the cursor automatically when the block is exited.

#### *async* execute(query: QueryNoTemplate, params: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [None](https://docs.python.org/3/library/constants.html#None) = None, , prepare: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, binary: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

#### *async* execute(query: Template, , prepare: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, binary: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

Execute a query or command to the database.

#### *async* executemany(query: Query, params_seq: Iterable[Params], , returning: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [None](https://docs.python.org/3/library/constants.html#None)

Execute the same command with a sequence of input data.

#### copy(statement: Query, params: Params | [None](https://docs.python.org/3/library/constants.html#None) = None, , writer: [AsyncWriter](copy.md#psycopg.copy.AsyncWriter) | [None](https://docs.python.org/3/library/constants.html#None) = None) → AsyncIterator[[AsyncCopy](copy.md#psycopg.AsyncCopy)]

Initiate a `COPY` operation and return an object to manage it.

#### NOTE
The method must be called with:

```default
async with cursor.copy() as copy:
    ...
```

#### *async* stream(query: Query, params: Params | [None](https://docs.python.org/3/library/constants.html#None) = None, , binary: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, size: [int](https://docs.python.org/3/library/functions.html#int) = 1) → AsyncIterator[Row]

Iterate row-by-row on a result from the database.

* **Parameters:**
  **size** – if greater than 1, results will be retrieved by chunks of
  this size from the server (but still yielded row-by-row); this is only
  available from version 17 of the libpq.

#### NOTE
The method must be called with:

```default
async for record in cursor.stream(query):
    ...
```

#### *async* fetchone() → Row | [None](https://docs.python.org/3/library/constants.html#None)

Return the next record from the current result set.

Return `None` the result set is finished.

* **Return type:**
  Row | None, with Row defined by `row_factory`

#### *async* fetchmany(size: [int](https://docs.python.org/3/library/functions.html#int) = 0) → [list](https://docs.python.org/3/library/stdtypes.html#list)[Row]

Return the next `size` records from the current result set.

`size` default to `self.arraysize` if not specified.

* **Return type:**
  Sequence[Row], with Row defined by `row_factory`

#### *async* fetchall() → [list](https://docs.python.org/3/library/stdtypes.html#list)[Row]

Return all the remaining records from the current result set.

* **Return type:**
  Sequence[Row], with Row defined by `row_factory`

#### *async* results() → [AsyncIterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator)[[Self](https://docs.python.org/3/library/typing.html#typing.Self)]

Iterate across multiple record sets received by the cursor.

Multiple record sets are received after using [`executemany()`](#psycopg.AsyncCursor.executemany) with
`returning=True` or using [`execute()`](#psycopg.AsyncCursor.execute) with more than one query in the
command.

#### *async* set_result(index: [int](https://docs.python.org/3/library/functions.html#int)) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

Move to a specific result set.

* **Parameters:**
  **index** (`int`) – index of the result to go to

More than one result will be available after executing calling
[`executemany()`](#psycopg.AsyncCursor.executemany) or [`execute()`](#psycopg.AsyncCursor.execute) with more than one query.

`index` is 0-based and supports negative values, counting from the end,
the same way you can index items in a list.

The function returns self, so that the result may be followed by a
fetch operation. See [`results()`](#psycopg.AsyncCursor.results) for details.

#### *async* scroll(value: [int](https://docs.python.org/3/library/functions.html#int), mode: [str](https://docs.python.org/3/library/stdtypes.html#str) = 'relative') → [None](https://docs.python.org/3/library/constants.html#None)

Move the cursor in the result set to a new position according to mode.

If `mode` is `'relative'` (default), `value` is taken as offset to
the current position in the result set; if set to `'absolute'`,
`value` states an absolute target position.

Raise `IndexError` in case a scroll operation would leave the result
set. In this case the position will not change.

#### NOTE
You can also use:

```default
async for record in cursor:
    ...
```

to iterate on the async cursor results.

### *class* psycopg.AsyncClientCursor(connection: [AsyncConnection](connections.md#psycopg.AsyncConnection)[Any], , row_factory: [AsyncRowFactory](rows.md#psycopg.rows.AsyncRowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None)

This class is the `async` equivalent of [`ClientCursor`](#psycopg.ClientCursor). The differences
w.r.t. the sync counterpart are the same described in [`AsyncCursor`](#psycopg.AsyncCursor).

#### Versionadded
Added in version 3.1.

### *class* psycopg.AsyncServerCursor(connection: [AsyncConnection](connections.md#psycopg.AsyncConnection)[Any], name: [str](https://docs.python.org/3/library/stdtypes.html#str), , row_factory: [AsyncRowFactory](rows.md#psycopg.rows.AsyncRowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None, scrollable: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, withhold: [bool](https://docs.python.org/3/library/functions.html#bool) = False)

This class implements a DBAPI-inspired interface as the [`AsyncCursor`](#psycopg.AsyncCursor)
does, but wraps a server-side cursor like the [`ServerCursor`](#psycopg.ServerCursor) class. It is
created by [`AsyncConnection.cursor()`](connections.md#psycopg.AsyncConnection.cursor) specifying the `name` parameter.

The following are the methods exposing a different (async) interface from
the [`ServerCursor`](#psycopg.ServerCursor) counterpart, but sharing the same semantics.

#### *async* close() → [None](https://docs.python.org/3/library/constants.html#None)

Close the current cursor and free associated resources.

#### NOTE
You can close the cursor automatically using:

```default
async with conn.cursor("name") as cursor:
    ...
```

#### *async* execute(query: Query, params: Params | [None](https://docs.python.org/3/library/constants.html#None) = None, , binary: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, \*\*kwargs: Any) → Self

Open a cursor to execute a query to the database.

#### *async* executemany(query: Query, params_seq: Iterable[Params], , returning: [bool](https://docs.python.org/3/library/functions.html#bool) = True) → [None](https://docs.python.org/3/library/constants.html#None)

Method not implemented for server-side cursors.

#### *async* fetchone() → Row | [None](https://docs.python.org/3/library/constants.html#None)

Return the next record from the current result set.

Return `None` the result set is finished.

* **Return type:**
  Row | None, with Row defined by `row_factory`

#### *async* fetchmany(size: [int](https://docs.python.org/3/library/functions.html#int) = 0) → [list](https://docs.python.org/3/library/stdtypes.html#list)[Row]

Return the next `size` records from the current result set.

`size` default to `self.arraysize` if not specified.

* **Return type:**
  Sequence[Row], with Row defined by `row_factory`

#### *async* fetchall() → [list](https://docs.python.org/3/library/stdtypes.html#list)[Row]

Return all the remaining records from the current result set.

* **Return type:**
  Sequence[Row], with Row defined by `row_factory`

#### NOTE
You can also iterate on the cursor using:

```default
async for record in cur:
    ...
```

#### *async* scroll(value: [int](https://docs.python.org/3/library/functions.html#int), mode: [str](https://docs.python.org/3/library/stdtypes.html#str) = 'relative') → [None](https://docs.python.org/3/library/constants.html#None)

Move the cursor in the result set to a new position according to mode.

If `mode` is `'relative'` (default), `value` is taken as offset to
the current position in the result set; if set to `'absolute'`,
`value` states an absolute target position.

Raise `IndexError` in case a scroll operation would leave the result
set. In this case the position will not change.

### *class* psycopg.AsyncRawCursor(connection: [AsyncConnection](connections.md#psycopg.AsyncConnection)[Any], , row_factory: [AsyncRowFactory](rows.md#psycopg.rows.AsyncRowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None)

This class is the `async` equivalent of [`RawCursor`](#psycopg.RawCursor). The differences
w.r.t. the sync counterpart are the same described in [`AsyncCursor`](#psycopg.AsyncCursor).

#### Versionadded
Added in version 3.2.

### *class* psycopg.AsyncRawServerCursor(connection: [AsyncConnection](connections.md#psycopg.AsyncConnection)[Any], name: [str](https://docs.python.org/3/library/stdtypes.html#str), , row_factory: [AsyncRowFactory](rows.md#psycopg.rows.AsyncRowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None, scrollable: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, withhold: [bool](https://docs.python.org/3/library/functions.html#bool) = False)

This class is the `async` equivalent of [`RawServerCursor`](#psycopg.RawServerCursor). The differences
w.r.t. the sync counterpart are the same described in [`AsyncServerCursor`](#psycopg.AsyncServerCursor).

#### Versionadded
Added in version 3.2.

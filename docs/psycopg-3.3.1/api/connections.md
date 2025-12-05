# Connection classes

The [`Connection`](#psycopg.Connection) and [`AsyncConnection`](#psycopg.AsyncConnection) classes are the main wrappers for a
PostgreSQL database session. You can imagine them similar to a **psql**
session.

One of the differences compared to **psql** is that a [`Connection`](#psycopg.Connection)
usually handles a transaction automatically: other sessions will not be able
to see the changes until you have committed them, more or less explicitly.
Take a look to [Transactions management](../basic/transactions.md#transactions) for the details.

## The `Connection` class

### *class* psycopg.Connection

Wrapper for a connection to the database.

This class implements a [DBAPI-compliant interface](https://www.python.org/dev/peps/pep-0249/#connection-objects). It is what you want
to use if you write a “classic”, blocking program (eventually using
threads or Eventlet/gevent for concurrency). If your program uses [`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio)
you might want to use [`AsyncConnection`](#psycopg.AsyncConnection) instead.

Connections behave as context managers: on block exit, the current
transaction will be committed (or rolled back, in case of exception) and
the connection will be closed.

#### *classmethod* connect(conninfo: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', , autocommit: [bool](https://docs.python.org/3/library/functions.html#bool) = False, prepare_threshold: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = 5, context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None, row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None, cursor_factory: [type](https://docs.python.org/3/library/functions.html#type)[[Cursor](cursors.md#psycopg.Cursor)[Row]] | [None](https://docs.python.org/3/library/constants.html#None) = None, \*\*kwargs: [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

Connect to a database server and return a new [`Connection`](#psycopg.Connection) instance.

* **Parameters:**
  * **conninfo** – The [connection string](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING) (a `postgresql://` url or
    a list of `key=value` pairs) to specify where and how to connect.
  * **kwargs** – Further parameters specifying the connection string.
    They override the ones specified in `conninfo`.
  * **autocommit** – If `True` don’t start transactions automatically.
    See [Transactions management](../basic/transactions.md#transactions) for details.
  * **row_factory** – The row factory specifying what type of records
    to create fetching data (default: [`tuple_row()`](rows.md#psycopg.rows.tuple_row)). See
    [Row factories](../advanced/rows.md#row-factories) for details.
  * **cursor_factory** – Initial value for the [`cursor_factory`](#psycopg.Connection.cursor_factory) attribute
    of the connection (new in Psycopg 3.1).
  * **prepare_threshold** – Initial value for the [`prepare_threshold`](#psycopg.Connection.prepare_threshold)
    attribute of the connection (new in Psycopg 3.1).

More specialized use:

* **Parameters:**
  **context** – A context to copy the initial adapters configuration
  from. It might be an [`AdaptersMap`](adapt.md#psycopg.adapt.AdaptersMap) with customized
  loaders and dumpers, used as a template to create several connections.
  See [Data adaptation configuration](../advanced/adapt.md#adaptation) for further details.

This method is also aliased as [`psycopg.connect()`](module.md#psycopg.connect).

#### SEE ALSO
- the list of [the accepted connection parameters](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS)
- the [environment variables](https://www.postgresql.org/docs/current/libpq-envars.html) affecting connection

#### Versionchanged
Changed in version 3.1: added `prepare_threshold` and `cursor_factory` parameters.

#### adapters *: [AdaptersMap](adapt.md#psycopg.adapt.AdaptersMap)*

The adapters configuration used to convert Python parameters and
PostgreSQL results for the queries executed on this cursor.

It affects all the cursors created by this connection afterwards.

#### close() → [None](https://docs.python.org/3/library/constants.html#None)

Close the database connection.

#### NOTE
You can use:

```default
with psycopg.connect() as conn:
    ...
```

to close the connection automatically when the block is exited.
See [Connection context](../basic/usage.md#with-connection).

#### closed

`True` if the connection is closed.

#### broken

`True` if the connection was interrupted.

A broken connection is always [`closed`](#psycopg.Connection.closed), but wasn’t closed in a clean
way, such as using [`close()`](#psycopg.Connection.close) or a `with` block.

#### cursor(, binary: [bool](https://docs.python.org/3/library/functions.html#bool) = False, row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [Cursor](cursors.md#psycopg.Cursor)

#### cursor(name: [str](https://docs.python.org/3/library/stdtypes.html#str), , binary: [bool](https://docs.python.org/3/library/functions.html#bool) = False, row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory) | [None](https://docs.python.org/3/library/constants.html#None) = None, scrollable: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, withhold: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [ServerCursor](cursors.md#psycopg.ServerCursor)

Return a new cursor to send commands and queries to the connection.

* **Parameters:**
  * **name** – If not specified create a client-side cursor, if
    specified create a server-side cursor. See
    [Cursor types](../advanced/cursors.md#cursor-types) for details.
  * **binary** – If `True` return binary values from the database. All
    the types returned by the query must have a binary
    loader. See [Binary parameters and results](../basic/params.md#binary-data) for details.
  * **row_factory** – If specified override the [`row_factory`](#psycopg.Connection.row_factory) set on the
    connection. See [Row factories](../advanced/rows.md#row-factories) for details.
  * **scrollable** – Specify the [`scrollable`](cursors.md#psycopg.ServerCursor.scrollable) property of
    the server-side cursor created.
  * **withhold** – Specify the [`withhold`](cursors.md#psycopg.ServerCursor.withhold) property of
    the server-side cursor created.
* **Returns:**
  A cursor of the class specified by [`cursor_factory`](#psycopg.Connection.cursor_factory) (or
  [`server_cursor_factory`](#psycopg.Connection.server_cursor_factory) if `name` is specified).

#### NOTE
You can use:

```default
with conn.cursor() as cur:
    ...
```

to close the cursor automatically when the block is exited.

#### cursor_factory *: [type](https://docs.python.org/3/library/functions.html#type)[[Cursor](cursors.md#psycopg.Cursor)[Row]]*

The type, or factory function, returned by [`cursor()`](#psycopg.Connection.cursor) and [`execute()`](#psycopg.Connection.execute).

Default is [`psycopg.Cursor`](cursors.md#psycopg.Cursor).

#### server_cursor_factory *: [type](https://docs.python.org/3/library/functions.html#type)[[ServerCursor](cursors.md#psycopg.ServerCursor)[Row]]*

The type, or factory function, returned by [`cursor()`](#psycopg.Connection.cursor) when a name is
specified.

Default is [`psycopg.ServerCursor`](cursors.md#psycopg.ServerCursor).

#### row_factory *: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row]*

The row factory defining the type of rows returned by
[`fetchone()`](cursors.md#psycopg.Cursor.fetchone) and the other cursor fetch methods.

The default is [`tuple_row`](rows.md#psycopg.rows.tuple_row), which means that the fetch
methods will return simple tuples.

#### SEE ALSO
See [Row factories](../advanced/rows.md#row-factories) for details about defining the
objects returned by cursors.

#### execute(query: QueryNoTemplate, params: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [None](https://docs.python.org/3/library/constants.html#None) = None, , prepare: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, binary: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [Cursor](cursors.md#psycopg.Cursor)[Row]

#### execute(query: Template, , prepare: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, binary: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [Cursor](cursors.md#psycopg.Cursor)[Row]

Execute a query and return a cursor to read its results.

* **Parameters:**
  * **query** ([`LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString), `bytes`, [`sql.SQL`](sql.md#psycopg.sql.SQL), [`sql.Composed`](sql.md#psycopg.sql.Composed),
    or [`Template`](https://docs.python.org/3/library/string.templatelib.html#string.templatelib.Template)) – The query to execute.
  * **params** (*Sequence* *or* *Mapping*) – The parameters to pass to the query, if any.
    Can’t be specified if `query` is a `Template`.
  * **prepare** – Force (`True`) or disallow (`False`) preparation of
    the query. By default (`None`) prepare automatically. See
    [Prepared statements](../advanced/prepare.md#prepared-statements).
  * **binary** – If `True` the cursor will return binary values from the
    database. All the types returned by the query must have a binary
    loader. See [Binary parameters and results](../basic/params.md#binary-data) for details.

The method simply creates a [`Cursor`](cursors.md#psycopg.Cursor) instance, [`execute()`](cursors.md#psycopg.Cursor.execute) the
query requested, and returns it.

See [Passing parameters to SQL queries](../basic/params.md#query-parameters) for all the details about executing
queries.

#### pipeline() → [Iterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[Pipeline](objects.md#psycopg.Pipeline)]

Context manager to switch the connection into pipeline mode.

The method is a context manager: you should call it using:

```default
with conn.pipeline() as p:
    ...
```

At the end of the block, a synchronization point is established and
the connection returns in normal mode.

You can call the method recursively from within a pipeline block.
Innermost blocks will establish a synchronization point on exit, but
pipeline mode will be kept until the outermost block exits.

See [Pipeline mode support](../advanced/pipeline.md#pipeline-mode) for details.

#### Versionadded
Added in version 3.1.

### Transaction management methods

For details see [Transactions management](../basic/transactions.md#transactions).

#### commit() → [None](https://docs.python.org/3/library/constants.html#None)

Commit any pending transaction to the database.

#### rollback() → [None](https://docs.python.org/3/library/constants.html#None)

Roll back to the start of any pending transaction.

#### transaction(savepoint_name: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None, force_rollback: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [Iterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[Transaction](objects.md#psycopg.Transaction)]

Start a context block with a new transaction or nested transaction.

* **Parameters:**
  * **savepoint_name** – Name of the savepoint used to manage a nested
    transaction. If `None`, one will be chosen automatically.
  * **force_rollback** – Roll back the transaction at the end of the
    block even if there were no error (e.g. to try a no-op process).
* **Return type:**
  [Transaction](objects.md#psycopg.Transaction)

#### NOTE
The method must be called with a syntax such as:

```default
with conn.transaction():
    ...

with conn.transaction() as tx:
    ...
```

The latter is useful if you need to interact with the
[`Transaction`](objects.md#psycopg.Transaction) object. See [Transaction contexts](../basic/transactions.md#transaction-context) for details.

Inside a transaction block it will not be possible to call [`commit()`](#psycopg.Connection.commit)
or [`rollback()`](#psycopg.Connection.rollback).

#### autocommit

The autocommit state of the connection.

The property is writable for sync connections, read-only for async
ones: you should call `await` [`set_autocommit`](#psycopg.AsyncConnection.set_autocommit)
`(*value*)` instead.

#### set_autocommit(value: [bool](https://docs.python.org/3/library/functions.html#bool)) → [None](https://docs.python.org/3/library/constants.html#None)

Method version of the [`autocommit`](#psycopg.Connection.autocommit) setter.

#### Versionadded
Added in version 3.2.

The following three properties control the characteristics of new
transactions. See [Transaction characteristics](../basic/transactions.md#transaction-characteristics) for details.

#### isolation_level

The isolation level of the new transactions started on the connection.

`None` means use the default set in the [default_transaction_isolation](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-DEFAULT-TRANSACTION-ISOLATION)
configuration parameter of the server.

#### set_isolation_level(value: [IsolationLevel](objects.md#psycopg.IsolationLevel) | [None](https://docs.python.org/3/library/constants.html#None)) → [None](https://docs.python.org/3/library/constants.html#None)

Method version of the [`isolation_level`](#psycopg.Connection.isolation_level) setter.

#### Versionadded
Added in version 3.2.

#### read_only

The read-only state of the new transactions started on the connection.

`None` means use the default set in the [default_transaction_read_only](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-DEFAULT-TRANSACTION-READ-ONLY)
configuration parameter of the server.

#### set_read_only(value: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None)) → [None](https://docs.python.org/3/library/constants.html#None)

Method version of the [`read_only`](#psycopg.Connection.read_only) setter.

#### Versionadded
Added in version 3.2.

#### deferrable

The deferrable state of the new transactions started on the connection.

`None` means use the default set in the [default_transaction_deferrable](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-DEFAULT-TRANSACTION-DEFERRABLE)
configuration parameter of the server.

#### set_deferrable(value: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None)) → [None](https://docs.python.org/3/library/constants.html#None)

Method version of the [`deferrable`](#psycopg.Connection.deferrable) setter.

#### Versionadded
Added in version 3.2.

### Checking and configuring the connection state

#### pgconn *: [psycopg.pq.PGconn](pq.md#psycopg.pq.PGconn)*

The [`PGconn`](pq.md#psycopg.pq.PGconn) libpq connection wrapper underlying the `Connection`.

It can be used to send low level commands to PostgreSQL and access
features not currently wrapped by Psycopg.

#### info

A [`ConnectionInfo`](objects.md#psycopg.ConnectionInfo) attribute to inspect connection properties.

#### prepare_threshold

Number of times a query is executed before it is prepared.

- If it is set to 0, every query is prepared the first time it is
  executed.
- If it is set to `None`, prepared statements are disabled on the
  connection.

Default value: 5

See [Prepared statements](../advanced/prepare.md#prepared-statements) for details.

#### prepared_max

Maximum number of prepared statements on the connection.

`None` means no max number of prepared statements. The default value
is 100.

If more queries need to be prepared, old ones are [deallocated](https://www.postgresql.org/docs/current/sql-deallocate.html).

Specifying `None` can be useful for middleware that don’t support
deallocation; see [prepared statements notes](../advanced/prepare.md#pgbouncer).

#### Versionchanged
Changed in version 3.2: Added support for the `None` value.

### Methods you can use to do something cool

#### cancel_safe(, timeout: [float](https://docs.python.org/3/library/functions.html#float) = 30.0) → [None](https://docs.python.org/3/library/constants.html#None)

Cancel the current operation on the connection.

* **Parameters:**
  **timeout** – raise a [`CancellationTimeout`](errors.md#psycopg.errors.CancellationTimeout) if the
  cancellation request does not succeed within `timeout` seconds.

Note that a successful cancel attempt on the client is not a guarantee
that the server will successfully manage to cancel the operation.

This is a non-blocking version of [`cancel()`](#psycopg.Connection.cancel) which
leverages a more secure and improved cancellation feature of the libpq,
which is only available from version 17.

If the underlying libpq is older than version 17, the method will fall
back to using the same implementation of `cancel()`.

#### NOTE
You can use the [`has_cancel_safe`](objects.md#psycopg.Capabilities.has_cancel_safe) capability to check
if `cancel_safe()` will not fall back on the legacy libpq
functions.

#### WARNING
The `timeout` parameter has no effect for libpq older than version
17.

#### WARNING
This method shouldn’t be used as a [`signal`](https://docs.python.org/3/library/signal.html#signal.signal) handler.
Please use [`cancel()`](#psycopg.Connection.cancel) instead.

#### Versionadded
Added in version 3.2.

#### cancel() → [None](https://docs.python.org/3/library/constants.html#None)

Cancel the current operation on the connection.

#### WARNING
The `cancel()` method is implemented using the `[PQcancel](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQCANCEL)`
function, which is deprecated since PostgreSQL 17, and has a few
shortcomings:

- it is blocking even on async connections,
- it [might use an insecure connection](https://www.postgresql.org/docs/devel/libpq-cancel.html#LIBPQ-CANCEL-DEPRECATED) even if the original
  connection was secure.

Therefore you should use the [`cancel_safe()`](#psycopg.Connection.cancel_safe) method whenever
possible.

#### NOTE
Unlike [`cancel_safe()`](#psycopg.Connection.cancel_safe), it is safe to call this method as a
[`signal`](https://docs.python.org/3/library/signal.html#signal.signal) handler. This is pretty much the only case in
which you might want to use this function.

#### notifies(, timeout: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None) = None, stop_after: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [Generator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Generator)[[Notify](objects.md#psycopg.Notify)]

Yield [`Notify`](objects.md#psycopg.Notify) objects as soon as they are received from the database.

* **Parameters:**
  * **timeout** – maximum amount of time to wait for notifications.
    `None` means no timeout.
  * **stop_after** – stop after receiving this number of notifications.
    You might actually receive more than this number if more than one
    notifications arrives in the same packet.

Notifies are received after using `LISTEN` in a connection, when
any sessions in the database generates a `NOTIFY` on one of the
listened channels.

#### Versionchanged
Changed in version 3.2: Added `timeout` and `stop_after` parameters.

#### add_notify_handler(callback: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[Notify](objects.md#psycopg.Notify)], [None](https://docs.python.org/3/library/constants.html#None)]) → [None](https://docs.python.org/3/library/constants.html#None)

Register a callable to be invoked whenever a notification is received.

* **Parameters:**
  **callback** (*Callable* *[* *[*[*Notify*](objects.md#psycopg.Notify) *]* *,* *None* *]*) – the callback to call upon notification received.

See [Asynchronous notifications](../advanced/async.md#async-notify) for details.

#### remove_notify_handler(callback: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[Notify](objects.md#psycopg.Notify)], [None](https://docs.python.org/3/library/constants.html#None)]) → [None](https://docs.python.org/3/library/constants.html#None)

Unregister a notification callable previously registered.

* **Parameters:**
  **callback** (*Callable* *[* *[*[*Notify*](objects.md#psycopg.Notify) *]* *,* *None* *]*) – the callback to remove.

#### add_notice_handler(callback: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[Diagnostic](errors.md#psycopg.errors.Diagnostic)], [None](https://docs.python.org/3/library/constants.html#None)]) → [None](https://docs.python.org/3/library/constants.html#None)

Register a callable to be invoked when a notice message is received.

* **Parameters:**
  **callback** (*Callable* *[* *[*[*Diagnostic*](errors.md#psycopg.errors.Diagnostic) *]* *,* *None* *]*) – the callback to call upon message received.

See [Server messages](../advanced/async.md#async-messages) for details.

#### remove_notice_handler(callback: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[Diagnostic](errors.md#psycopg.errors.Diagnostic)], [None](https://docs.python.org/3/library/constants.html#None)]) → [None](https://docs.python.org/3/library/constants.html#None)

Unregister a notice message callable previously registered.

* **Parameters:**
  **callback** (*Callable* *[* *[*[*Diagnostic*](errors.md#psycopg.errors.Diagnostic) *]* *,* *None* *]*) – the callback to remove.

#### fileno() → [int](https://docs.python.org/3/library/functions.html#int)

Return the file descriptor of the connection.

This function allows to use the connection as file-like object in
functions waiting for readiness, such as the ones defined in the
[`selectors`](https://docs.python.org/3/library/selectors.html#module-selectors) module.

<a id="tpc-methods"></a>

### Two-Phase Commit support methods

#### Versionadded
Added in version 3.1.

#### SEE ALSO
[Two-Phase Commit protocol support](../basic/transactions.md#two-phase-commit) for an introductory explanation of
these methods.

#### xid(format_id: [int](https://docs.python.org/3/library/functions.html#int), gtrid: [str](https://docs.python.org/3/library/stdtypes.html#str), bqual: [str](https://docs.python.org/3/library/stdtypes.html#str)) → [Xid](objects.md#psycopg.Xid)

Returns a [`Xid`](objects.md#psycopg.Xid) to pass to the `tpc_*()` methods of this connection.

The argument types and constraints are explained in
[Two-Phase Commit protocol support](../basic/transactions.md#two-phase-commit).

The values passed to the method will be available on the returned
object as the members [`format_id`](objects.md#psycopg.Xid.format_id), [`gtrid`](objects.md#psycopg.Xid.gtrid), [`bqual`](objects.md#psycopg.Xid.bqual).

#### tpc_begin(xid: [Xid](objects.md#psycopg.Xid) | [str](https://docs.python.org/3/library/stdtypes.html#str)) → [None](https://docs.python.org/3/library/constants.html#None)

Begin a TPC transaction with the given transaction ID `xid`.

* **Parameters:**
  **xid** ([*Xid*](objects.md#psycopg.Xid) *or* [*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The id of the transaction

This method should be called outside of a transaction (i.e. nothing
may have executed since the last [`commit()`](#psycopg.Connection.commit) or [`rollback()`](#psycopg.Connection.rollback) and
[`transaction_status`](objects.md#psycopg.ConnectionInfo.transaction_status) is [`IDLE`](pq.md#psycopg.pq.TransactionStatus.IDLE)).

Furthermore, it is an error to call `commit()` or `rollback()`
within the TPC transaction: in this case a [`ProgrammingError`](errors.md#psycopg.ProgrammingError)
is raised.

The `xid` may be either an object returned by the [`xid()`](#psycopg.Connection.xid) method or a
plain string: the latter allows to create a transaction using the
provided string as PostgreSQL transaction id. See also
[`tpc_recover()`](#psycopg.Connection.tpc_recover).

#### tpc_prepare() → [None](https://docs.python.org/3/library/constants.html#None)

Perform the first phase of a transaction started with [`tpc_begin()`](#psycopg.Connection.tpc_begin).

A [`ProgrammingError`](errors.md#psycopg.ProgrammingError) is raised if this method is used outside of a TPC
transaction.

After calling `tpc_prepare()`, no statements can be executed until
[`tpc_commit()`](#psycopg.Connection.tpc_commit) or [`tpc_rollback()`](#psycopg.Connection.tpc_rollback) will be
called.

#### SEE ALSO
The [`PREPARE TRANSACTION`](https://www.postgresql.org/docs/current/static/sql-prepare-transaction.html) PostgreSQL command.

#### tpc_commit(xid: [Xid](objects.md#psycopg.Xid) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Commit a prepared two-phase transaction.

* **Parameters:**
  **xid** ([*Xid*](objects.md#psycopg.Xid) *or* [*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The id of the transaction

When called with no arguments, `tpc_commit()` commits a TPC
transaction previously prepared with [`tpc_prepare()`](#psycopg.Connection.tpc_prepare).

If `tpc_commit()` is called prior to `tpc_prepare()`, a single phase
commit is performed.  A transaction manager may choose to do this if
only a single resource is participating in the global transaction.

When called with a transaction ID `xid`, the database commits the
given transaction.  If an invalid transaction ID is provided, a
[`ProgrammingError`](errors.md#psycopg.ProgrammingError) will be raised.  This form should be called outside
of a transaction, and is intended for use in recovery.

On return, the TPC transaction is ended.

#### SEE ALSO
The [`COMMIT PREPARED`](https://www.postgresql.org/docs/current/static/sql-commit-prepared.html) PostgreSQL command.

#### tpc_rollback(xid: [Xid](objects.md#psycopg.Xid) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Roll back a prepared two-phase transaction.

* **Parameters:**
  **xid** ([*Xid*](objects.md#psycopg.Xid) *or* [*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The id of the transaction

When called with no arguments, `tpc_rollback()` rolls back a TPC
transaction.  It may be called before or after [`tpc_prepare()`](#psycopg.Connection.tpc_prepare).

When called with a transaction ID `xid`, it rolls back the given
transaction.  If an invalid transaction ID is provided, a
[`ProgrammingError`](errors.md#psycopg.ProgrammingError) is raised.  This form should be called outside of a
transaction, and is intended for use in recovery.

On return, the TPC transaction is ended.

#### SEE ALSO
The [`ROLLBACK PREPARED`](https://www.postgresql.org/docs/current/static/sql-rollback-prepared.html) PostgreSQL command.

#### tpc_recover() → [list](https://docs.python.org/3/library/stdtypes.html#list)[[Xid](objects.md#psycopg.Xid)]

Returns a list of [`Xid`](objects.md#psycopg.Xid) representing pending transactions, suitable
for use with [`tpc_commit()`](#psycopg.Connection.tpc_commit) or [`tpc_rollback()`](#psycopg.Connection.tpc_rollback).

If a transaction was not initiated by Psycopg, the returned Xids will
have attributes [`format_id`](objects.md#psycopg.Xid.format_id) and [`bqual`](objects.md#psycopg.Xid.bqual) set to `None` and
the [`gtrid`](objects.md#psycopg.Xid.gtrid) set to the PostgreSQL transaction ID: such Xids are
still usable for recovery.  Psycopg uses the same algorithm of the
[PostgreSQL JDBC driver](https://jdbc.postgresql.org/) to encode a XA triple in a string, so
transactions initiated by a program using such driver should be
unpacked correctly.

Xids returned by `tpc_recover()` also have extra attributes
[`prepared`](objects.md#psycopg.Xid.prepared), [`owner`](objects.md#psycopg.Xid.owner), [`database`](objects.md#psycopg.Xid.database) populated with the
values read from the server.

#### SEE ALSO
the [`pg_prepared_xacts`](https://www.postgresql.org/docs/current/static/view-pg-prepared-xacts.html) system view.

## The `AsyncConnection` class

### *class* psycopg.AsyncConnection

Wrapper for a connection to the database.

This class implements a DBAPI-inspired interface, with all the blocking
methods implemented as coroutines. Unless specified otherwise,
non-blocking methods are shared with the [`Connection`](#psycopg.Connection) class.

The following methods have the same behaviour of the matching `Connection`
methods, but should be called using the `await` keyword.

#### *async classmethod* connect(conninfo: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', , autocommit: [bool](https://docs.python.org/3/library/functions.html#bool) = False, prepare_threshold: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = 5, context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None, row_factory: [AsyncRowFactory](rows.md#psycopg.rows.AsyncRowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None, cursor_factory: [type](https://docs.python.org/3/library/functions.html#type)[[AsyncCursor](cursors.md#psycopg.AsyncCursor)[Row]] | [None](https://docs.python.org/3/library/constants.html#None) = None, \*\*kwargs: [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

Connect to a database server and return a new [`AsyncConnection`](#psycopg.AsyncConnection) instance.

#### Versionchanged
Changed in version 3.1: Automatically resolve domain names asynchronously. In previous
versions, name resolution blocks, unless the `hostaddr`
parameter is specified, or the [`resolve_hostaddr_async()`](dns.md#psycopg._dns.resolve_hostaddr_async)
function is used.

#### *async* close() → [None](https://docs.python.org/3/library/constants.html#None)

Close the database connection.

#### NOTE
You can use `async with` to close the connection
automatically when the block is exited, but be careful about
the async quirkness: see [with async connections](../advanced/async.md#async-with) for details.

#### cursor(, binary: [bool](https://docs.python.org/3/library/functions.html#bool) = False, row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [AsyncCursor](cursors.md#psycopg.AsyncCursor)

#### cursor(name: [str](https://docs.python.org/3/library/stdtypes.html#str), , binary: [bool](https://docs.python.org/3/library/functions.html#bool) = False, row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory) | [None](https://docs.python.org/3/library/constants.html#None) = None, scrollable: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, withhold: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [AsyncServerCursor](cursors.md#psycopg.AsyncServerCursor)

#### NOTE
You can use:

```default
async with conn.cursor() as cur:
    ...
```

to close the cursor automatically when the block is exited.

#### cursor_factory *: [type](https://docs.python.org/3/library/functions.html#type)[[AsyncCursor](cursors.md#psycopg.AsyncCursor)[Row]]*

Default is [`psycopg.AsyncCursor`](cursors.md#psycopg.AsyncCursor).

#### server_cursor_factory *: [type](https://docs.python.org/3/library/functions.html#type)[[AsyncServerCursor](cursors.md#psycopg.AsyncServerCursor)[Row]]*

Default is [`psycopg.AsyncServerCursor`](cursors.md#psycopg.AsyncServerCursor).

#### row_factory *: [AsyncRowFactory](rows.md#psycopg.rows.AsyncRowFactory)[Row]*

#### *async* execute(query: QueryNoTemplate, params: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [None](https://docs.python.org/3/library/constants.html#None) = None, , prepare: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, binary: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [AsyncCursor](cursors.md#psycopg.AsyncCursor)[Row]

#### *async* execute(query: Template, , prepare: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None) = None, binary: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [AsyncCursor](cursors.md#psycopg.AsyncCursor)[Row]

Execute a query and return a cursor to read its results.

#### pipeline() → [AsyncIterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator)[[AsyncPipeline](objects.md#psycopg.AsyncPipeline)]

Context manager to switch the connection into pipeline mode.

#### NOTE
It must be called as:

```default
async with conn.pipeline() as p:
    ...
```

#### *async* commit() → [None](https://docs.python.org/3/library/constants.html#None)

Commit any pending transaction to the database.

#### *async* rollback() → [None](https://docs.python.org/3/library/constants.html#None)

Roll back to the start of any pending transaction.

#### transaction(savepoint_name: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None, force_rollback: [bool](https://docs.python.org/3/library/functions.html#bool) = False) → [AsyncIterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator)[[AsyncTransaction](objects.md#psycopg.AsyncTransaction)]

Start a context block with a new transaction or nested transaction.

* **Parameters:**
  * **savepoint_name** – Name of the savepoint used to manage a nested
    transaction. If `None`, one will be chosen automatically.
  * **force_rollback** – Roll back the transaction at the end of the
    block even if there were no error (e.g. to try a no-op process).
* **Return type:**
  [AsyncTransaction](objects.md#psycopg.AsyncTransaction)

#### NOTE
It must be called as:

```default
async with conn.transaction() as tx:
    ...
```

#### *async* cancel_safe(, timeout: [float](https://docs.python.org/3/library/functions.html#float) = 30.0) → [None](https://docs.python.org/3/library/constants.html#None)

Cancel the current operation on the connection.

* **Parameters:**
  **timeout** – raise a [`CancellationTimeout`](errors.md#psycopg.errors.CancellationTimeout) if the
  cancellation request does not succeed within `timeout` seconds.

Note that a successful cancel attempt on the client is not a guarantee
that the server will successfully manage to cancel the operation.

This is a non-blocking version of [`cancel()`](#psycopg.Connection.cancel) which
leverages a more secure and improved cancellation feature of the libpq,
which is only available from version 17.

If the underlying libpq is older than version 17, the method will fall
back to using the same implementation of `cancel()`.

#### Versionadded
Added in version 3.2.

#### *async* notifies(, timeout: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None) = None, stop_after: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [AsyncGenerator](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncGenerator)[[Notify](objects.md#psycopg.Notify)]

Yield [`Notify`](objects.md#psycopg.Notify) objects as soon as they are received from the database.

* **Parameters:**
  * **timeout** – maximum amount of time to wait for notifications.
    `None` means no timeout.
  * **stop_after** – stop after receiving this number of notifications.
    You might actually receive more than this number if more than one
    notifications arrives in the same packet.

#### Versionchanged
Changed in version 3.2: Added `timeout` and `stop_after` parameters.

#### *async* set_autocommit(value: [bool](https://docs.python.org/3/library/functions.html#bool)) → [None](https://docs.python.org/3/library/constants.html#None)

Method version of the [`autocommit`](#psycopg.Connection.autocommit) setter.

#### *async* set_isolation_level(value: [IsolationLevel](objects.md#psycopg.IsolationLevel) | [None](https://docs.python.org/3/library/constants.html#None)) → [None](https://docs.python.org/3/library/constants.html#None)

Method version of the [`isolation_level`](#psycopg.Connection.isolation_level) setter.

#### *async* set_read_only(value: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None)) → [None](https://docs.python.org/3/library/constants.html#None)

Method version of the [`read_only`](#psycopg.Connection.read_only) setter.

#### *async* set_deferrable(value: [bool](https://docs.python.org/3/library/functions.html#bool) | [None](https://docs.python.org/3/library/constants.html#None)) → [None](https://docs.python.org/3/library/constants.html#None)

Method version of the [`deferrable`](#psycopg.Connection.deferrable) setter.

#### *async* tpc_prepare() → [None](https://docs.python.org/3/library/constants.html#None)

Perform the first phase of a transaction started with `tpc_begin()`.

#### *async* tpc_commit(xid: [Xid](objects.md#psycopg.Xid) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Commit a prepared two-phase transaction.

#### *async* tpc_rollback(xid: [Xid](objects.md#psycopg.Xid) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Roll back a prepared two-phase transaction.

#### *async* tpc_recover() → [list](https://docs.python.org/3/library/stdtypes.html#list)[[Xid](objects.md#psycopg.Xid)]

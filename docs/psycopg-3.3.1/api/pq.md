<a id="psycopg-pq"></a>

# `pq` – libpq wrapper module

<a id="index-0"></a>

<a id="module-psycopg.pq"></a>

Psycopg is built around the [libpq](https://www.postgresql.org/docs/current/libpq.html), the PostgreSQL client library, which
performs most of the network communications and returns query results in C
structures.

The low-level functions of the library are exposed by the objects in the
`psycopg.pq` module.

<a id="pq-impl"></a>

## `pq` module implementations

There are actually several implementations of the module, all offering the
same interface. Current implementations are:

- `python`: a pure-python implementation, implemented using the [`ctypes`](https://docs.python.org/3/library/ctypes.html#module-ctypes)
  module. It is less performing than the others, but it doesn’t need a C
  compiler to install. It requires the libpq installed in the system.
- `c`: a C implementation of the libpq wrapper (more precisely, implemented
  in [Cython](https://cython.org/)). It is much better performing than the `python`
  implementation, however it requires development packages installed on the
  client machine. It can be installed using the `c` extra, i.e. running
  `pip install "psycopg[c]"`.
- `binary`: a pre-compiled C implementation, bundled with all the required
  libraries. It is the easiest option to deal with, fast to install and it
  should require no development tool or client library, however it may be not
  available for every platform. You can install it using the `binary` extra,
  i.e. running `pip install "psycopg[binary]"`.

The implementation currently used is available in the [`__impl__`](#psycopg.pq.__impl__)
module constant.

At import time, Psycopg 3 will try to use the best implementation available
and will fail if none is usable. You can force the use of a specific
implementation by exporting the env var `PSYCOPG_IMPL`: importing the
library will fail if the requested implementation is not available:

```default
$ PSYCOPG_IMPL=c python -c "import psycopg"
Traceback (most recent call last):
   ...
ImportError: couldn't import requested psycopg 'c' implementation: No module named 'psycopg_c'
```

## Module content

### psycopg.pq.\_\_impl_\_ *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'python'*

The currently loaded implementation of the `psycopg.pq` package.

Possible values include `python`, `c`, `binary`.

The choice of implementation is automatic but can be forced setting the
`PSYCOPG_IMPL` env var.

### psycopg.pq.version() → [int](https://docs.python.org/3/library/functions.html#int)

Return the version number of the libpq currently loaded.

The number is in the same format of [`server_version`](objects.md#psycopg.ConnectionInfo.server_version).

Certain features might not be available if the libpq library used is too old.

#### SEE ALSO
the `[PQlibVersion()](https://www.postgresql.org/docs/18/libpq-misc.html#LIBPQ-PQLIBVERSION)` function

### psycopg.pq.\_\_build_version_\_ *: [int](https://docs.python.org/3/library/functions.html#int)* *= 170005*

The libpq version the C package was built with.

A number in the same format of [`server_version`](objects.md#psycopg.ConnectionInfo.server_version)
representing the libpq used to build the speedup module (`c`, `binary`) if
available.

Certain features might not be available if the built version is too old.

## Objects wrapping libpq structures and functions

### *class* psycopg.pq.PGconn

Python representation of a libpq connection.

#### pgconn_ptr

The pointer to the underlying `PGconn` structure, as integer.

`None` if the connection is closed.

The value can be used to pass the structure to libpq functions which
psycopg doesn’t (currently) wrap, either in C or in Python using FFI
libraries such as [`ctypes`](https://docs.python.org/3/library/ctypes.html#module-ctypes).

#### cancel_conn() → [PGcancelConn](#psycopg.pq.PGcancelConn)

Create a connection over which a cancel request can be sent.

See `[PQcancelCreate](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQCANCELCREATE)` for details.

#### get_cancel() → [PGcancel](#psycopg.pq.PGcancel)

Create an object with the information needed to cancel a command.

See `[PQgetCancel](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQGETCANCEL)` for details.

#### needs_password

True if the connection authentication method required a password,
but none was available.

See `[PQconnectionNeedsPassword](https://www.postgresql.org/docs/18/libpq-status.html#LIBPQ-PQCONNECTIONNEEDSPASSWORD)` for details.

#### used_password

True if the connection authentication method used a password.

See `[PQconnectionUsedPassword](https://www.postgresql.org/docs/18/libpq-status.html#LIBPQ-PQCONNECTIONUSEDPASSWORD)` for details.

#### used_gssapi

True if the connection authentication method used GSSAPI.

See `[PQconnectionUsedGSSAPI](https://www.postgresql.org/docs/18/libpq-status.html#LIBPQ-PQCONNECTIONUSEDGSSAPI)` for details.

#### Versionadded
Added in version 3.3.

#### encrypt_password(passwd: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes), user: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes), algorithm: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)

Return the encrypted form of a PostgreSQL password.

See `[PQencryptPasswordConn](https://www.postgresql.org/docs/18/libpq-misc.html#LIBPQ-PQENCRYPTPASSWORDCONN)` for details.

```python
>>> enc = conn.info.encoding
>>> encrypted = conn.pgconn.encrypt_password(password.encode(enc), rolename.encode(enc))
b'SCRAM-SHA-256$4096:...
```

#### change_password(user: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes), passwd: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)) → [None](https://docs.python.org/3/library/constants.html#None)

Change a PostgreSQL password.

* **Raises:**
  [**OperationalError**](errors.md#psycopg.OperationalError) – if the command to change password failed.

See `[PQchangePassword](https://www.postgresql.org/docs/18/libpq-misc.html#LIBPQ-PQCHANGEPASSWORD)` for details.

#### trace(fileno: [int](https://docs.python.org/3/library/functions.html#int)) → [None](https://docs.python.org/3/library/constants.html#None)

Enable tracing of the client/server communication to a file stream.

See `[PQtrace](https://www.postgresql.org/docs/18/libpq-control.html#LIBPQ-PQTRACE)` for details.

#### set_trace_flags(flags: [Trace](#psycopg.pq.Trace)) → [None](https://docs.python.org/3/library/constants.html#None)

Configure tracing behavior of client/server communication.

* **Parameters:**
  **flags** – operating mode of tracing.

See `[PQsetTraceFlags](https://www.postgresql.org/docs/18/libpq-control.html#LIBPQ-PQSETTRACEFLAGS)` for details.

#### untrace() → [None](https://docs.python.org/3/library/constants.html#None)

Disable tracing, previously enabled through [`trace()`](#psycopg.pq.PGconn.trace).

See `[PQuntrace](https://www.postgresql.org/docs/18/libpq-control.html#LIBPQ-PQUNTRACE)` for details.

```python
>>> conn.pgconn.trace(sys.stderr.fileno())
>>> conn.pgconn.set_trace_flags(pq.Trace.SUPPRESS_TIMESTAMPS | pq.Trace.REGRESS_MODE)
>>> conn.execute("select now()")
F       13      Parse    "" "BEGIN" 0
F       14      Bind     "" "" 0 0 1 0
F       6       Describe         P ""
F       9       Execute  "" 0
F       4       Sync
B       4       ParseComplete
B       4       BindComplete
B       4       NoData
B       10      CommandComplete  "BEGIN"
B       5       ReadyForQuery    T
F       17      Query    "select now()"
B       28      RowDescription   1 "now" NNNN 0 NNNN 8 -1 0
B       39      DataRow  1 29 '2022-09-14 14:12:16.648035+02'
B       13      CommandComplete  "SELECT 1"
B       5       ReadyForQuery    T
<psycopg.Cursor [TUPLES_OK] [INTRANS] (database=postgres) at 0x7f18a18ba040>
>>> conn.pgconn.untrace()
```

### *class* psycopg.pq.PGresult

Python representation of a libpq result.

#### pgresult_ptr

The pointer to the underlying `PGresult` structure, as integer.

`None` if the result was cleared.

The value can be used to pass the structure to libpq functions which
psycopg doesn’t (currently) wrap, either in C or in Python using FFI
libraries such as [`ctypes`](https://docs.python.org/3/library/ctypes.html#module-ctypes).

### *class* psycopg.pq.Conninfo

Utility object to manipulate connection strings.

### *class* psycopg.pq.Escaping(conn: [PGconn](#psycopg.pq.PGconn) | [None](https://docs.python.org/3/library/constants.html#None) = None)

Utility object to escape strings for SQL interpolation.

### *class* psycopg.pq.PGcancelConn

Token to handle non-blocking cancellation requests.

Created by [`PGconn.cancel_conn()`](#psycopg.pq.PGconn.cancel_conn).

#### start() → [None](https://docs.python.org/3/library/constants.html#None)

Requests that the server abandons processing of the current command
in a non-blocking manner.

See `[PQcancelStart](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQCANCELSTART)` for details.

#### blocking() → [None](https://docs.python.org/3/library/constants.html#None)

Requests that the server abandons processing of the current command
in a blocking manner.

See `[PQcancelBlocking](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQCANCELBLOCKING)` for details.

#### finish(\_PGcancelConn_\_PQcancelFinish: ~typing.Any = <_FuncPtr object>) → [None](https://docs.python.org/3/library/constants.html#None)

Free the data structure created by `PQcancelCreate()`.

Automatically invoked by `__del__()`.

See `[PQcancelFinish()](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQCANCELFINISH)` for details.

### *class* psycopg.pq.PGcancel

Token to cancel the current operation on a connection.

Created by [`PGconn.get_cancel()`](#psycopg.pq.PGconn.get_cancel).

#### free(\_PGcancel_\_PQfreeCancel: ~typing.Any = <_FuncPtr object>) → [None](https://docs.python.org/3/library/constants.html#None)

Free the data structure created by `[PQgetCancel()](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQGETCANCEL)`.

Automatically invoked by `__del__()`.

See `[PQfreeCancel()](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQFREECANCEL)` for details.

#### cancel() → [None](https://docs.python.org/3/library/constants.html#None)

Requests that the server abandon processing of the current command.

See `[PQcancel()](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQCANCEL)` for details.

## Enumerations

### *class* psycopg.pq.ConnStatus(\*values)

Current status of the connection.

There are other values in this enum, but only [`OK`](#psycopg.pq.ConnStatus.OK) and [`BAD`](#psycopg.pq.ConnStatus.BAD) are seen
after a connection has been established. Other statuses might only be seen
during the connection phase and are considered internal.
`ALLOCATED` is only expected to be returned by `PGcancelConn.status`.

#### SEE ALSO
`[PQstatus()](https://www.postgresql.org/docs/18/libpq-status.html#LIBPQ-PQSTATUS)` and `[PQcancelStatus()](https://www.postgresql.org/docs/18/libpq-cancel.html#LIBPQ-PQCANCELSTATUS)` return this value.

#### OK *= 0*

#### BAD *= 1*

### *class* psycopg.pq.PollingStatus(\*values)

The status of the socket during a connection.

If `READING` or `WRITING` you may select before polling again.

#### SEE ALSO
`[PQconnectPoll](https://www.postgresql.org/docs/18/libpq-connect.html#LIBPQ-PQCONNECTSTARTPARAMS)` for a description of these states.

#### FAILED *= 0*

#### READING *= 1*

#### WRITING *= 2*

#### OK *= 3*

### *class* psycopg.pq.TransactionStatus(\*values)

The transaction status of a connection.

#### SEE ALSO
`[PQtransactionStatus](https://www.postgresql.org/docs/18/libpq-status.html#LIBPQ-PQTRANSACTIONSTATUS)` for a description of these states.

#### IDLE *= 0*

#### ACTIVE *= 1*

#### INTRANS *= 2*

#### INERROR *= 3*

#### UNKNOWN *= 4*

### *class* psycopg.pq.ExecStatus(\*values)

The status of a command.

#### SEE ALSO
`[PQresultStatus](https://www.postgresql.org/docs/18/libpq-exec.html#LIBPQ-PQRESULTSTATUS)` for a description of these states.

#### EMPTY_QUERY *= 0*

#### COMMAND_OK *= 1*

#### TUPLES_OK *= 2*

#### COPY_OUT *= 3*

#### COPY_IN *= 4*

#### BAD_RESPONSE *= 5*

#### NONFATAL_ERROR *= 6*

#### FATAL_ERROR *= 7*

#### COPY_BOTH *= 8*

#### SINGLE_TUPLE *= 9*

#### PIPELINE_SYNC *= 10*

#### PIPELINE_ABORTED *= 11*

#### TUPLES_CHUNK *= 12*

### *class* psycopg.pq.PipelineStatus(\*values)

Pipeline mode status of the libpq connection.

#### SEE ALSO
`[PQpipelineStatus](https://www.postgresql.org/docs/18/libpq-pipeline-mode.html#LIBPQ-PQPIPELINESTATUS)` for a description of these states.

#### OFF *= 0*

#### ON *= 1*

#### ABORTED *= 2*

### *class* psycopg.pq.Format(\*values)

Enum representing the format of a query argument or return value.

These values are only the ones managed by the libpq. [`psycopg`](module.md#module-psycopg) may also
support automatically-chosen values: see [`psycopg.adapt.PyFormat`](adapt.md#psycopg.adapt.PyFormat).

#### TEXT *= 0*

#### BINARY *= 1*

### *class* psycopg.pq.DiagnosticField(\*values)

Fields in an error report.

Available attributes:

#### SEVERITY

#### SEVERITY_NONLOCALIZED

#### SQLSTATE

#### MESSAGE_PRIMARY

#### MESSAGE_DETAIL

#### MESSAGE_HINT

#### STATEMENT_POSITION

#### INTERNAL_POSITION

#### INTERNAL_QUERY

#### CONTEXT

#### SCHEMA_NAME

#### TABLE_NAME

#### COLUMN_NAME

#### DATATYPE_NAME

#### CONSTRAINT_NAME

#### SOURCE_FILE

#### SOURCE_LINE

#### SOURCE_FUNCTION

#### SEE ALSO
`[PQresultErrorField](https://www.postgresql.org/docs/18/libpq-exec.html#LIBPQ-PQRESULTERRORFIELD)` for a description of these values.

### *class* psycopg.pq.Ping(\*values)

Response from a ping attempt.

#### SEE ALSO
`[PQpingParams](https://www.postgresql.org/docs/18/libpq-connect.html#LIBPQ-PQPINGPARAMS)` for a description of these values.

#### OK *= 0*

#### REJECT *= 1*

#### NO_RESPONSE *= 2*

#### NO_ATTEMPT *= 3*

### *class* psycopg.pq.Trace(\*values)

Enum to control tracing of the client/server communication.

#### SEE ALSO
`[PQsetTraceFlags](https://www.postgresql.org/docs/18/libpq-control.html#LIBPQ-PQSETTRACEFLAGS)` for a description of these values.

#### SUPPRESS_TIMESTAMPS *= 1*

#### REGRESS_MODE *= 2*

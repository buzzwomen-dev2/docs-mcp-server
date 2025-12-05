<a id="index-0"></a>

# `psycopg` release notes

## Current release

### Psycopg 3.3.1

Fix iteration on server-side cursors (ticket [#1226](https://github.com/psycopg/psycopg/issues/1226)).

## Psycopg 3.3.0

### New top-level features

- Add [template strings queries](basic/tstrings.md#template-strings) (ticket [#1054](https://github.com/psycopg/psycopg/issues/1054)).
- More flexible [composite adaptation](basic/pgtypes.md#adapt-composite): it is now possible
  to adapt Python objects to PostgreSQL composites and back even if they are not
  sequences or if they take keyword arguments (ticket [#932](https://github.com/psycopg/psycopg/issues/932), ticket [#1202](https://github.com/psycopg/psycopg/issues/1202)).
- Cursors are now [iterators](https://docs.python.org/3/glossary.html#term-iterator), not just [iterables](https://docs.python.org/3/glossary.html#term-iterable). This means you can call
  [`next`](https://docs.python.org/3/library/functions.html#next)`(cur)` or [`anext`](https://docs.python.org/3/library/functions.html#anext)`(cur)`, which is useful as a [type-safe
  expression](advanced/typing.md#typing-fetchone) (ticket [#1064](https://github.com/psycopg/psycopg/issues/1064)).
- Add [`Cursor.set_result()`](api/cursors.md#psycopg.Cursor.set_result) and [`Cursor.results()`](api/cursors.md#psycopg.Cursor.results) to move across the result
  sets of queries executed though [`executemany()`](api/cursors.md#psycopg.Cursor.executemany) or
  [`execute()`](api/cursors.md#psycopg.Cursor.execute) with multiple statements (tickets [#1080](https://github.com/psycopg/psycopg/issues/1080), [#1170](https://github.com/psycopg/psycopg/issues/1170)).
- Add [Transaction status](basic/transactions.md#transaction-status) to report the status during and after a
  [`transaction()`](api/connections.md#psycopg.Connection.transaction) block (ticket [#969](https://github.com/psycopg/psycopg/issues/969)).
- Allow to change loaders using [`register_loader()`](api/adapt.md#psycopg.adapt.AdaptersMap.register_loader) on
  [`Cursor.adapters`](api/cursors.md#psycopg.Cursor.adapters) after a query result has been already returned
  (ticket [#884](https://github.com/psycopg/psycopg/issues/884)).

### New libpq wrapper features

- Add [`pq.PGconn.used_gssapi`](api/pq.md#psycopg.pq.PGconn.used_gssapi) attribute and [`Capabilities.has_used_gssapi()`](api/objects.md#psycopg.Capabilities.has_used_gssapi)
  function (ticket [#1138](https://github.com/psycopg/psycopg/issues/1138)).
- Add [`ConnectionInfo.full_protocol_version`](api/objects.md#psycopg.ConnectionInfo.full_protocol_version) attribute,
  [`Capabilities.has_full_protocol_version()`](api/objects.md#psycopg.Capabilities.has_full_protocol_version) function (ticket [#1079](https://github.com/psycopg/psycopg/issues/1079)).

### Other changes

- Disable default GSSAPI preferential connection in the binary package
  (ticket [#1136](https://github.com/psycopg/psycopg/issues/1136)).

  #### WARNING
  Please explicitly set the [gssencmode](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNECT-GSSENCMODE) connection parameter or the
  `PGGSSENCMODE` environment variable to interact reliably with the
  GSSAPI.
- Drop support for Python 3.8 (ticket [#976](https://github.com/psycopg/psycopg/issues/976)) and 3.9 (ticket [#1056](https://github.com/psycopg/psycopg/issues/1056)).

### Psycopg 3.2.13

- Show the host name in the error message in case of name resolution error
  (ticket [#1205](https://github.com/psycopg/psycopg/issues/1205)).
- Fix [`Cursor.copy()`](api/cursors.md#psycopg.Cursor.copy) and [`AsyncCursor.copy()`](api/cursors.md#psycopg.AsyncCursor.copy) to hold the connection lock
  for the entire operation, preventing concurrent access issues (ticket [#1210](https://github.com/psycopg/psycopg/issues/1210)).
- Fix GSSAPI check with C extension built with libpq < v16 (ticket [#1216](https://github.com/psycopg/psycopg/issues/1216)).

### Psycopg 3.2.12

- Allow copy to pass different types per column, as long as the database can
  convert them. Regression introduced in 3.2.11 (ticket [#1192](https://github.com/psycopg/psycopg/issues/1192)).

### Psycopg 3.2.11

- Fix spurious readiness flags in some of the wait functions (ticket [#1141](https://github.com/psycopg/psycopg/issues/1141)).
- Fix high CPU usage using the `wait_c` function on Windows (ticket [#645](https://github.com/psycopg/psycopg/issues/645)).
- Fix bad data on error in binary copy (ticket [#1147](https://github.com/psycopg/psycopg/issues/1147)).
- Respect [`Copy.set_types()`](api/copy.md#psycopg.Copy.set_types) in TEXT copy in C version, consistently with
  the Python version (ticket [#1153](https://github.com/psycopg/psycopg/issues/1153)).
- Don’t raise warning, and don’t leak resources, if a builtin function is used
  as JSON dumper/loader function (ticket [#1165](https://github.com/psycopg/psycopg/issues/1165)).
- Improve performance of Python conversion on results loading (ticket [#1155](https://github.com/psycopg/psycopg/issues/1155)).

<a id="psycopg-3-2-10"></a>

### Psycopg 3.2.10

- Fix `TypeError` shadowing [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) upon task cancellation
  during pipeline execution (ticket [#1005](https://github.com/psycopg/psycopg/issues/1005)).
- Fix memory leak when lambda/local functions are used as argument for
  [`set_json_dumps()`](api/types.md#psycopg.types.json.set_json_dumps), [`set_json_loads()`](api/types.md#psycopg.types.json.set_json_loads)
  (ticket [#1108](https://github.com/psycopg/psycopg/issues/1108)).
- Fix coordination of [`executemany()`](api/cursors.md#psycopg.Cursor.executemany) with other concurrent operations
  on other cursors (ticket [#1130](https://github.com/psycopg/psycopg/issues/1130)).
- Fix leak receiving notifications if the [`notifies()`](api/connections.md#psycopg.Connection.notifies) generator
  is not called (ticket [#1091](https://github.com/psycopg/psycopg/issues/1091)).

  #### WARNING
  This bugfix required the introduction of a change in [notifies
  reception](advanced/async.md#async-notify) behaviour.

  If a notification is received when a handler is registered via
  [`add_notify_handler()`](api/connections.md#psycopg.Connection.add_notify_handler) and the [`notifies()`](api/connections.md#psycopg.Connection.notifies)
  generator is not running the notification will not be yielded by the
  generator. This is a behaviour similar to before [Psycopg 3.2.4](), but
  *notifications are not lost if no handler is registered*.

  Using both the generator and handlers to receive notifications on the same
  connection is therefore deprecated and will now generate a runtime
  warning.
- Add support for Python 3.14 (ticket [#1053](https://github.com/psycopg/psycopg/issues/1053)).
- Fix `psycopg_binary.__version__`.
- Raise a warning if a GSSAPI connection is obtained using the
  `gssencmode=prefer` libpq default (see ticket [#1136](https://github.com/psycopg/psycopg/issues/1136)).

  #### WARNING
  In a future Psycopg version the default in the binary package will be
  changed to `disable`. If you need to interact with the GSSAPI reliably
  you should explicitly set the [gssencmode](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNECT-GSSENCMODE) parameter in the connection
  string or the `PGGSSENCMODE` environment variable to `prefer` or
  `require`.

### Psycopg 3.2.9

- Revert the libpq included in the binary packages from conda forge to vcpkg
  because GSS connection crashes (ticket [#1088](https://github.com/psycopg/psycopg/issues/1088)).

### Psycopg 3.2.8

- Fix `DateFromTicks` and `TimeFromTicks` return values to return a date and a
  time referred to the UTC timezone rather than to the local timezone. For
  consistency, `TimestampFromTicks` to return a datetime in UTC rather than in
  the local timezone (ticket [#1058](https://github.com/psycopg/psycopg/issues/1058)).
- Fix [`rownumber`](api/cursors.md#psycopg.Cursor.rownumber) after using [`scroll()`](api/cursors.md#psycopg.AsyncServerCursor.scroll) on
  [`AsyncServerCursor`](api/cursors.md#psycopg.AsyncServerCursor) (ticket [#1066](https://github.com/psycopg/psycopg/issues/1066)).
- Fix interval parsing with days or other parts and negative time in C module
  (ticket [#1071](https://github.com/psycopg/psycopg/issues/1071)).
- Don’t process further connection attempts after Ctrl-C (ticket [#1077](https://github.com/psycopg/psycopg/issues/1077)).
- Fix cursors to correctly iterate over rows even if their row factory
  returns [`None`](https://docs.python.org/3/library/constants.html#None) (ticket [#1073](https://github.com/psycopg/psycopg/issues/1073)).
- Fix [`ConnectionInfo.port`](api/objects.md#psycopg.ConnectionInfo.port) when the port is specified as an empty string
  (ticket [#1078](https://github.com/psycopg/psycopg/issues/1078)).
- Report all the attempts error messages in the exception raised for a
  connection failure (ticket [#1069](https://github.com/psycopg/psycopg/issues/1069)).
- Improve logging on connection (ticket [#1085](https://github.com/psycopg/psycopg/issues/1085)).
- Add support for PostgreSQL 18 libpq (ticket [#1082](https://github.com/psycopg/psycopg/issues/1082)).

### Psycopg 3.2.7

- Add SRID support to shapely dumpers/loaders (ticket [#1028](https://github.com/psycopg/psycopg/issues/1028)).
- Add support for binary hstore (ticket [#1030](https://github.com/psycopg/psycopg/issues/1030)).

### Psycopg 3.2.6

- Fix connection semantic when using `target_session_attrs=prefer-standby`
  (ticket [#1021](https://github.com/psycopg/psycopg/issues/1021)).

### Psycopg 3.2.5

- 3x faster UUID loading thanks to C implementation (tickets [#447](https://github.com/psycopg/psycopg/issues/447), [#998](https://github.com/psycopg/psycopg/issues/998)).

<a id="psycopg-3-2-4"></a>

### Psycopg 3.2.4

- Don’t lose notifies received whilst the [`notifies()`](api/connections.md#psycopg.Connection.notifies) iterator
  is not running (ticket [#962](https://github.com/psycopg/psycopg/issues/962)).

  #### WARNING
  If you were using notifications to bridge the time between issuing a LISTEN
  on a channel and starting the iterator you might receive duplicate
  notifications.
- Make sure that the notifies callback is called during the use of the
  [`notifies()`](api/connections.md#psycopg.Connection.notifies) generator (ticket [#972](https://github.com/psycopg/psycopg/issues/972)).
- Raise the correct error returned by the database (such as `AdminShutdown`
  or `IdleInTransactionSessionTimeout`) instead of a generic
  [`OperationalError`](api/errors.md#psycopg.OperationalError) when a server error causes a client disconnection
  (ticket [#988](https://github.com/psycopg/psycopg/issues/988)).
- Build macOS dependencies from sources instead using the Homebrew versions
  in order to avoid problems with `MACOSX_DEPLOYMENT_TARGET` (ticket [#858](https://github.com/psycopg/psycopg/issues/858)).
- Bump libpq to 17.2 in Linux and macOS binary packages.
- Bump libpq to 16.4 in Windows binary packages, using the [vcpkg library](https://vcpkg.io/en/package/libpq)
  (ticket [#966](https://github.com/psycopg/psycopg/issues/966)).

### Psycopg 3.2.3

- Release binary packages including PostgreSQL 17 libpq (ticket [#852](https://github.com/psycopg/psycopg/issues/852)).

### Psycopg 3.2.2

- Drop `TypeDef` specifications as string from public modules, as they cannot
  be composed by users as `typing` objects previously could (ticket [#860](https://github.com/psycopg/psycopg/issues/860)).
- Release Python 3.13 binary packages.

### Psycopg 3.2.1

- Fix packaging metadata breaking `[c]`, `[binary]` dependencies
  (ticket [#853](https://github.com/psycopg/psycopg/issues/853)).

## Psycopg 3.2

### New top-level features

- Add support for integer, floating point, boolean [NumPy scalar types](https://numpy.org/doc/stable/reference/arrays.scalars.html#built-in-scalar-types)
  (ticket [#332](https://github.com/psycopg/psycopg/issues/332)).
- Add `timeout` and `stop_after` parameters to [`Connection.notifies()`](api/connections.md#psycopg.Connection.notifies)
  (ticket [340](https://github.com/psycopg/psycopg/issues/340)).
- Allow dumpers to return `None`, to be converted to NULL (ticket [#377](https://github.com/psycopg/psycopg/issues/377)).
- Add [Raw query cursors](advanced/cursors.md#raw-query-cursors) to execute queries using placeholders in
  PostgreSQL format (`$1`, `$2`…) (tickets [#560](https://github.com/psycopg/psycopg/issues/560), [#839](https://github.com/psycopg/psycopg/issues/839)).
- Add [`capabilities`](api/module.md#psycopg.capabilities) object to [inspect the libpq capabilities](api/objects.md#capabilities) (ticket [#772](https://github.com/psycopg/psycopg/issues/772)).
- Add [`scalar_row`](api/rows.md#psycopg.rows.scalar_row) to return scalar values from a query (ticket [#723](https://github.com/psycopg/psycopg/issues/723)).
- Add [`cancel_safe()`](api/connections.md#psycopg.Connection.cancel_safe) for encrypted and non-blocking cancellation
  when using libpq v17. Use such method internally to implement
  `KeyboardInterrupt` and `copy` termination (ticket [#754](https://github.com/psycopg/psycopg/issues/754)).
- The `context` parameter of [`sql`](api/sql.md#module-psycopg.sql) objects [`as_string()`](api/sql.md#psycopg.sql.Composable.as_string) and
  [`as_bytes()`](api/sql.md#psycopg.sql.Composable.as_bytes) methods is now optional (ticket [#716](https://github.com/psycopg/psycopg/issues/716)).
- Add [`set_autocommit()`](api/connections.md#psycopg.Connection.set_autocommit) on sync connections, and similar
  transaction control methods available on the async connections.
- Add a `size` parameter to [`stream()`](api/cursors.md#psycopg.Cursor.stream) to enable results retrieval in
  chunks instead of row-by-row (ticket [#794](https://github.com/psycopg/psycopg/issues/794)).

### New libpq wrapper features

- Add support for libpq functions to close prepared statements and portals
  introduced in libpq v17 (ticket [#603](https://github.com/psycopg/psycopg/issues/603)).
- Add support for libpq encrypted and non-blocking query cancellation
  functions introduced in libpq v17 (ticket [#754](https://github.com/psycopg/psycopg/issues/754)).
- Add support for libpq function to retrieve results in chunks introduced in
  libpq v17 (ticket [#793](https://github.com/psycopg/psycopg/issues/793)).
- Add support for libpq function to change role passwords introduced in
  libpq v17 (ticket [#818](https://github.com/psycopg/psycopg/issues/818)).

### Other changes

- Drop support for Python 3.7.
- Prepared statements are now [compatible with PgBouncer](advanced/prepare.md#pgbouncer).
  (ticket [#589](https://github.com/psycopg/psycopg/issues/589)).
- Disable receiving more than one result on the same cursor in pipeline mode,
  to iterate through [`nextset()`](api/cursors.md#psycopg.Cursor.nextset). The behaviour was different than
  in non-pipeline mode and not totally reliable (ticket [#604](https://github.com/psycopg/psycopg/issues/604)).
  The [`Cursor`](api/cursors.md#psycopg.Cursor) now only preserves the results set of the last
  [`execute()`](api/cursors.md#psycopg.Cursor.execute), consistently with non-pipeline mode.

### Psycopg 3.1.20

- Use the simple query protocol to execute COMMIT/ROLLBACK when possible.
  This should make querying the PgBouncer admin database easier
  (ticket [#820](https://github.com/psycopg/psycopg/issues/820)).
- Avoid unneeded escaping checks and memory over-allocation in text copy
  (ticket [#829](https://github.com/psycopg/psycopg/issues/829)).
- Bundle binary package with OpenSSL 3.3.x (ticket [#847](https://github.com/psycopg/psycopg/issues/847)).
- Drop macOS ARM64 binary packages for macOS versions before 14.0 and Python
  before 3.10 (not for our choice but for the lack of available CI runners;
  ticket [#858](https://github.com/psycopg/psycopg/issues/858))

### Psycopg 3.1.19

- Fix unaligned access undefined behaviour in C extension (ticket [#734](https://github.com/psycopg/psycopg/issues/734)).
- Fix excessive stripping of error message prefixes (ticket [#752](https://github.com/psycopg/psycopg/issues/752)).
- Allow to specify the `connect_timeout` connection parameter as float
  (ticket [#796](https://github.com/psycopg/psycopg/issues/796)).
- Improve COPY performance on macOS (ticket [#745](https://github.com/psycopg/psycopg/issues/745)).

### Psycopg 3.1.18

- Fix possible deadlock on pipeline exit (ticket [#685](https://github.com/psycopg/psycopg/issues/685)).
- Fix overflow loading large intervals in C module (ticket [#719](https://github.com/psycopg/psycopg/issues/719)).
- Fix compatibility with musl libc distributions affected by [CPython issue
  #65821](https://github.com/python/cpython/issues/65821) (ticket [#725](https://github.com/psycopg/psycopg/issues/725)).

### Psycopg 3.1.17

- Fix multiple connection attempts when a host name resolve to multiple
  IP addresses (ticket [#699](https://github.com/psycopg/psycopg/issues/699)).
- Use [`typing.Self`](https://docs.python.org/3/library/typing.html#typing.Self) as a more correct return value annotation of context
  managers and other self-returning methods (see ticket [#708](https://github.com/psycopg/psycopg/issues/708)).

### Psycopg 3.1.16

- Fix empty ports handling in async multiple connection attempts
  (ticket [#703](https://github.com/psycopg/psycopg/issues/703)).

### Psycopg 3.1.15

- Fix use of `service` in connection string (regression in 3.1.13,
  ticket [#694](https://github.com/psycopg/psycopg/issues/694)).
- Fix async connection to hosts resolving to multiple IP addresses (regression
  in 3.1.13, ticket [#695](https://github.com/psycopg/psycopg/issues/695)).
- Respect the `PGCONNECT_TIMEOUT` environment variable to determine
  the connection timeout.

### Psycopg 3.1.14

- Fix [interaction with gevent](advanced/async.md#gevent) (ticket [#527](https://github.com/psycopg/psycopg/issues/527)).
- Add support for PyPy (ticket [#686](https://github.com/psycopg/psycopg/issues/686)).

### Psycopg 3.1.13

- Raise [`DataError`](api/errors.md#psycopg.DataError) instead of whatever internal failure trying to dump a
  [`time`](https://docs.python.org/3/library/datetime.html#datetime.time) object with with a `tzinfo` specified as
  [`ZoneInfo`](https://docs.python.org/3/library/zoneinfo.html#zoneinfo.ZoneInfo) (ambiguous offset, see ticket [#652](https://github.com/psycopg/psycopg/issues/652)).
- Handle gracefully EINTR on signals instead of raising [`InterruptedError`](https://docs.python.org/3/library/exceptions.html#InterruptedError),
  consistently with [**PEP 475**](https://peps.python.org/pep-0475/) guideline (ticket [#667](https://github.com/psycopg/psycopg/issues/667)).
- Fix support for connection strings with multiple hosts/ports and for the
  `load_balance_hosts` connection parameter (ticket [#674](https://github.com/psycopg/psycopg/issues/674)).
- Fix memory leak receiving notifications in Python implementation
  (ticket [#679](https://github.com/psycopg/psycopg/issues/679)).

### Psycopg 3.1.12

- Fix possible hanging if a connection is closed while querying (ticket [#608](https://github.com/psycopg/psycopg/issues/608)).
- Fix memory leak when `register_*()` functions are called repeatedly
  (ticket [#647](https://github.com/psycopg/psycopg/issues/647)).
- Release Python 3.12 binary packages.

### Psycopg 3.1.11

- Avoid caching the parsing results of large queries to avoid excessive memory
  usage (ticket [#628](https://github.com/psycopg/psycopg/issues/628)).
- Fix integer overflow in C/binary extension with OID > 2^31 (ticket [#630](https://github.com/psycopg/psycopg/issues/630)).
- Fix loading of intervals with days and months or years (ticket [#643](https://github.com/psycopg/psycopg/issues/643)).
- Work around excessive CPU usage on Windows (reported in ticket [#645](https://github.com/psycopg/psycopg/issues/645)).
- Fix building on Solaris and derivatives (ticket [#632](https://github.com/psycopg/psycopg/issues/632)).
- Fix possible lack of critical section guard in async
  [`executemany()`](api/cursors.md#psycopg.AsyncCursor.executemany).
- Fix missing pipeline fetch in async [`scroll()`](api/cursors.md#psycopg.AsyncCursor.scroll).
- Build binary packages with libpq 15.4, which allows group-readable
  permissions on the SSL certificate on the client (ticket [#528](https://github.com/psycopg/psycopg/issues/528)).

### Psycopg 3.1.10

- Allow JSON dumpers to dump [`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes) directly instead of [`str`](https://docs.python.org/3/library/stdtypes.html#str),
  for better compatibility with libraries like orjson and msgspec
  (ticket [#569](https://github.com/psycopg/psycopg/issues/569))
- Fix prepared statement cache validation when exiting pipeline mode (or
  [`executemany()`](api/cursors.md#psycopg.Cursor.executemany)) in case an error occurred within the pipeline
  (ticket [#585](https://github.com/psycopg/psycopg/issues/585)).
- Fix [`connect()`](api/module.md#psycopg.connect) to avoid “leaking” an open [`PGconn`](api/pq.md#psycopg.pq.PGconn) attached to the
  [`OperationalError`](api/errors.md#psycopg.OperationalError) in case of connection failure. [`Error.pgconn`](api/errors.md#psycopg.Error.pgconn) is now a
  shallow copy of the real libpq connection, and the latter is closed before
  the exception propagates (ticket [#565](https://github.com/psycopg/psycopg/issues/565)).
- Fix possible (ignored) exception on objects deletion (ticket [#591](https://github.com/psycopg/psycopg/issues/591)).
- Don’t clobber a Python exception raised during COPY FROM with the resulting
  `QueryCanceled` raised as a consequence (ticket [#593](https://github.com/psycopg/psycopg/issues/593)).
- Fix resetting [`Connection.read_only`](api/connections.md#psycopg.Connection.read_only) and [`deferrable`](api/connections.md#psycopg.Connection.deferrable) to their
  default value using `None` (ticket [#612](https://github.com/psycopg/psycopg/issues/612)).
- Add support for Python 3.12.

### Psycopg 3.1.9

- Fix `TypeInfo.fetch()` using a connection in `sql_ascii` encoding
  (ticket [#503](https://github.com/psycopg/psycopg/issues/503)).
- Fix “filedescriptor out of range” using a large number of files open
  in Python implementation (ticket [#532](https://github.com/psycopg/psycopg/issues/532)).
- Allow JSON dumpers to be registered on `dict` or any other object, as was
  possible in psycopg2 (ticket [#541](https://github.com/psycopg/psycopg/issues/541)).
- Fix canceling running queries on process interruption in async connections
  (ticket [#543](https://github.com/psycopg/psycopg/issues/543)).
- Fix loading ROW values with different types in the same query using the
  binary protocol (ticket [#545](https://github.com/psycopg/psycopg/issues/545)).
- Fix dumping recursive composite types (ticket [#547](https://github.com/psycopg/psycopg/issues/547)).

### Psycopg 3.1.8

- Don’t pollute server logs when types looked for by `TypeInfo.fetch()`
  are not found (ticket [#473](https://github.com/psycopg/psycopg/issues/473)).
- Set [`Cursor.rowcount`](api/cursors.md#psycopg.Cursor.rowcount) to the number of rows of each result set from
  [`executemany()`](api/cursors.md#psycopg.Cursor.executemany) when called with `returning=True` (ticket [#479](https://github.com/psycopg/psycopg/issues/479)).
- Fix `TypeInfo.fetch()` when used with [`ClientCursor`](api/cursors.md#psycopg.ClientCursor) (ticket [#484](https://github.com/psycopg/psycopg/issues/484)).

### Psycopg 3.1.7

- Fix server-side cursors using row factories (ticket [#464](https://github.com/psycopg/psycopg/issues/464)).

### Psycopg 3.1.6

- Fix `cursor.copy()` with cursors using row factories (ticket [#460](https://github.com/psycopg/psycopg/issues/460)).

### Psycopg 3.1.5

- Fix array loading slowness compared to psycopg2 (ticket [#359](https://github.com/psycopg/psycopg/issues/359)).
- Improve performance around network communication (ticket [#414](https://github.com/psycopg/psycopg/issues/414)).
- Return `bytes` instead of `memoryview` from `pq.Encoding` methods
  (ticket [#422](https://github.com/psycopg/psycopg/issues/422)).
- Fix [`Cursor.rownumber`](api/cursors.md#psycopg.Cursor.rownumber) to return `None` when the result has no row to fetch
  (ticket [#437](https://github.com/psycopg/psycopg/issues/437)).
- Avoid error in Pyright caused by aliasing `TypeAlias` (ticket [#439](https://github.com/psycopg/psycopg/issues/439)).
- Fix [`Copy.set_types()`](api/copy.md#psycopg.Copy.set_types) used with `varchar` and `name` types (ticket [#452](https://github.com/psycopg/psycopg/issues/452)).
- Improve performance using [Row factories](advanced/rows.md#row-factories) (ticket [#457](https://github.com/psycopg/psycopg/issues/457)).

### Psycopg 3.1.4

- Include [error classes](api/errors.md#sqlstate-exceptions) defined in PostgreSQL 15.
- Add support for Python 3.11 (ticket [#305](https://github.com/psycopg/psycopg/issues/305)).
- Build binary packages with libpq from PostgreSQL 15.0.

### Psycopg 3.1.3

- Restore the state of the connection if [`Cursor.stream()`](api/cursors.md#psycopg.Cursor.stream) is terminated
  prematurely (ticket [#382](https://github.com/psycopg/psycopg/issues/382)).
- Fix regression introduced in 3.1 with different named tuples mangling rules
  for non-ascii attribute names (ticket [#386](https://github.com/psycopg/psycopg/issues/386)).
- Fix handling of queries with escaped percent signs (`%%`) in [`ClientCursor`](api/cursors.md#psycopg.ClientCursor)
  (ticket [#399](https://github.com/psycopg/psycopg/issues/399)).
- Fix possible duplicated BEGIN statements emitted in pipeline mode
  (ticket [#401](https://github.com/psycopg/psycopg/issues/401)).

### Psycopg 3.1.2

- Fix handling of certain invalid time zones causing problems on Windows
  (ticket [#371](https://github.com/psycopg/psycopg/issues/371)).
- Fix segfault occurring when a loader fails initialization (ticket [#372](https://github.com/psycopg/psycopg/issues/372)).
- Fix invalid SAVEPOINT issued when entering [`Connection.transaction()`](api/connections.md#psycopg.Connection.transaction) within
  a pipeline using an implicit transaction (ticket [#374](https://github.com/psycopg/psycopg/issues/374)).
- Fix queries with repeated named parameters in [`ClientCursor`](api/cursors.md#psycopg.ClientCursor) (ticket [#378](https://github.com/psycopg/psycopg/issues/378)).
- Distribute macOS arm64 (Apple M1) binary packages (ticket [#344](https://github.com/psycopg/psycopg/issues/344)).

### Psycopg 3.1.1

- Work around broken Homebrew installation of the libpq in a non-standard path
  (ticket [#364](https://github.com/psycopg/psycopg/issues/364))
- Fix possible “unrecognized service” error in async connection when no port
  is specified (ticket [#366](https://github.com/psycopg/psycopg/issues/366)).

## Psycopg 3.1

- Add [Pipeline mode](advanced/pipeline.md#pipeline-mode) (ticket [#74](https://github.com/psycopg/psycopg/issues/74)).
- Add [Client-side-binding cursors](advanced/cursors.md#client-side-binding-cursors) (ticket [#101](https://github.com/psycopg/psycopg/issues/101)).
- Add [CockroachDB](https://www.cockroachlabs.com/) support in [`psycopg.crdb`](api/crdb.md#module-psycopg.crdb)
  (ticket [#313](https://github.com/psycopg/psycopg/issues/313)).
- Add [Two-Phase Commit](basic/transactions.md#two-phase-commit) support (ticket [#72](https://github.com/psycopg/psycopg/issues/72)).
- Add [Enum adaptation](basic/adapt.md#adapt-enum) (ticket [#274](https://github.com/psycopg/psycopg/issues/274)).
- Add `returning` parameter to [`executemany()`](api/cursors.md#psycopg.Cursor.executemany) to retrieve query
  results (ticket [#164](https://github.com/psycopg/psycopg/issues/164)).
- [`executemany()`](api/cursors.md#psycopg.Cursor.executemany) performance improved by using batch mode internally
  (ticket [#145](https://github.com/psycopg/psycopg/issues/145)).
- Add parameters to [`copy()`](api/cursors.md#psycopg.Cursor.copy).
- Add [COPY Writer objects](api/copy.md#copy-writers).
- Resolve domain names asynchronously in [`AsyncConnection.connect()`](api/connections.md#psycopg.AsyncConnection.connect)
  (ticket [#259](https://github.com/psycopg/psycopg/issues/259)).
- Add [`pq.PGconn.trace()`](api/pq.md#psycopg.pq.PGconn.trace) and related trace functions (ticket [#167](https://github.com/psycopg/psycopg/issues/167)).
- Add `prepare_threshold` parameter to [`Connection`](api/connections.md#psycopg.Connection) init (ticket [#200](https://github.com/psycopg/psycopg/issues/200)).
- Add `cursor_factory` parameter to [`Connection`](api/connections.md#psycopg.Connection) init.
- Add [`Error.pgconn`](api/errors.md#psycopg.Error.pgconn) and [`Error.pgresult`](api/errors.md#psycopg.Error.pgresult) attributes (ticket [#242](https://github.com/psycopg/psycopg/issues/242)).
- Restrict queries to be [`LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString) as per [**PEP 675**](https://peps.python.org/pep-0675/)
  (ticket [#323](https://github.com/psycopg/psycopg/issues/323)).
- Add explicit type cast to values converted by [`sql.Literal`](api/sql.md#psycopg.sql.Literal) (ticket [#205](https://github.com/psycopg/psycopg/issues/205)).
- Drop support for Python 3.6.

### Psycopg 3.0.17

- Fix segfaults on fork on some Linux systems using [`ctypes`](https://docs.python.org/3/library/ctypes.html#module-ctypes) implementation
  (ticket [#300](https://github.com/psycopg/psycopg/issues/300)).
- Load bytea as bytes, not memoryview, using [`ctypes`](https://docs.python.org/3/library/ctypes.html#module-ctypes) implementation.

### Psycopg 3.0.16

- Fix missing [`rowcount`](api/cursors.md#psycopg.Cursor.rowcount) after SHOW (ticket [#343](https://github.com/psycopg/psycopg/issues/343)).
- Add scripts to build macOS arm64 packages (ticket [#162](https://github.com/psycopg/psycopg/issues/162)).

### Psycopg 3.0.15

- Fix wrong escaping of unprintable chars in COPY (nonetheless correctly
  interpreted by PostgreSQL).
- Restore the connection to usable state after an error in [`stream()`](api/cursors.md#psycopg.Cursor.stream).
- Raise [`DataError`](api/errors.md#psycopg.DataError) instead of [`OverflowError`](https://docs.python.org/3/library/exceptions.html#OverflowError) loading binary intervals
  out-of-range.
- Distribute `manylinux2014` wheel packages (ticket [#124](https://github.com/psycopg/psycopg/issues/124)).

### Psycopg 3.0.14

- Raise [`DataError`](api/errors.md#psycopg.DataError) dumping arrays of mixed types (ticket [#301](https://github.com/psycopg/psycopg/issues/301)).
- Fix handling of incorrect server results, with blank sqlstate (ticket [#303](https://github.com/psycopg/psycopg/issues/303)).
- Fix bad Float4 conversion on ppc64le/musllinux (ticket [#304](https://github.com/psycopg/psycopg/issues/304)).

### Psycopg 3.0.13

- Fix [`Cursor.stream()`](api/cursors.md#psycopg.Cursor.stream) slowness (ticket [#286](https://github.com/psycopg/psycopg/issues/286)).
- Fix oid for lists of integers, which might cause the server choosing
  bad plans (ticket [#293](https://github.com/psycopg/psycopg/issues/293)).
- Make [`Connection.cancel()`](api/connections.md#psycopg.Connection.cancel) on a closed connection a no-op instead of an
  error.

### Psycopg 3.0.12

- Allow [`bytearray`](https://docs.python.org/3/library/stdtypes.html#bytearray)/[`memoryview`](https://docs.python.org/3/library/stdtypes.html#memoryview) data too as [`Copy.write()`](api/copy.md#psycopg.Copy.write) input
  (ticket [#254](https://github.com/psycopg/psycopg/issues/254)).
- Fix dumping [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) in text mode, Python implementation.

### Psycopg 3.0.11

- Fix [`DataError`](api/errors.md#psycopg.DataError) loading arrays with dimensions information (ticket [#253](https://github.com/psycopg/psycopg/issues/253)).
- Fix hanging during COPY in case of memory error (ticket [#255](https://github.com/psycopg/psycopg/issues/255)).
- Fix error propagation from COPY worker thread (mentioned in ticket [#255](https://github.com/psycopg/psycopg/issues/255)).

### Psycopg 3.0.10

- Leave the connection in working state after interrupting a query with Ctrl-C
  (ticket [#231](https://github.com/psycopg/psycopg/issues/231)).
- Fix [`Cursor.description`](api/cursors.md#psycopg.Cursor.description) after a COPY … TO STDOUT operation
  (ticket [#235](https://github.com/psycopg/psycopg/issues/235)).
- Fix building on FreeBSD and likely other BSD flavours (ticket [#241](https://github.com/psycopg/psycopg/issues/241)).

### Psycopg 3.0.9

- Set [`Error.sqlstate`](api/errors.md#psycopg.Error.sqlstate) when an unknown code is received (ticket [#225](https://github.com/psycopg/psycopg/issues/225)).
- Add the `tzdata` package as a dependency on Windows in order to handle time
  zones (ticket [#223](https://github.com/psycopg/psycopg/issues/223)).

### Psycopg 3.0.8

- Decode connection errors in the `client_encoding` specified in the
  connection string, if available (ticket [#194](https://github.com/psycopg/psycopg/issues/194)).
- Fix possible warnings in objects deletion on interpreter shutdown
  (ticket [#198](https://github.com/psycopg/psycopg/issues/198)).
- Don’t leave connections in ACTIVE state in case of error during COPY … TO
  STDOUT (ticket [#203](https://github.com/psycopg/psycopg/issues/203)).

### Psycopg 3.0.7

- Fix crash in [`executemany()`](api/cursors.md#psycopg.Cursor.executemany) with no input sequence
  (ticket [#179](https://github.com/psycopg/psycopg/issues/179)).
- Fix wrong [`rowcount`](api/cursors.md#psycopg.Cursor.rowcount) after an [`executemany()`](api/cursors.md#psycopg.Cursor.executemany) returning no
  rows (ticket [#178](https://github.com/psycopg/psycopg/issues/178)).

### Psycopg 3.0.6

- Allow to use [`Cursor.description`](api/cursors.md#psycopg.Cursor.description) if the connection is closed
  (ticket [#172](https://github.com/psycopg/psycopg/issues/172)).
- Don’t raise exceptions on [`ServerCursor.close()`](api/cursors.md#psycopg.ServerCursor.close) if the connection is closed
  (ticket [#173](https://github.com/psycopg/psycopg/issues/173)).
- Fail on [`Connection.cursor()`](api/connections.md#psycopg.Connection.cursor) if the connection is closed (ticket [#174](https://github.com/psycopg/psycopg/issues/174)).
- Raise [`ProgrammingError`](api/errors.md#psycopg.ProgrammingError) if out-of-order exit from transaction contexts is
  detected (tickets [#176](https://github.com/psycopg/psycopg/issues/176), [#177](https://github.com/psycopg/psycopg/issues/177)).
- Add `CHECK_STANDBY` value to [`ConnStatus`](api/pq.md#psycopg.pq.ConnStatus) enum.

### Psycopg 3.0.5

- Fix possible “Too many open files” OS error, reported on macOS but possible
  on other platforms too (ticket [#158](https://github.com/psycopg/psycopg/issues/158)).
- Don’t clobber exceptions if a transaction block exit with error and rollback
  fails (ticket [#165](https://github.com/psycopg/psycopg/issues/165)).

### Psycopg 3.0.4

- Allow to use the module with strict strings comparison (ticket [#147](https://github.com/psycopg/psycopg/issues/147)).
- Fix segfault on Python 3.6 running in `-W error` mode, related to
  `backport.zoneinfo` (ticket [#109](https://github.com/psycopg/psycopg/issues/109)).
  <[https://github.com/pganssle/zoneinfo/issues/109](https://github.com/pganssle/zoneinfo/issues/109)>\`_\_.
- Build binary package with libpq versions not affected by [CVE-2021-23222](https://www.postgresql.org/support/security/CVE-2021-23222/)
  (ticket [#149](https://github.com/psycopg/psycopg/issues/149)).

### Psycopg 3.0.3

- Release musllinux binary packages, compatible with Alpine Linux
  (ticket [#141](https://github.com/psycopg/psycopg/issues/141)).
- Reduce size of binary package by stripping debug symbols (ticket [#142](https://github.com/psycopg/psycopg/issues/142)).
- Include typing information in the `psycopg_binary` package.

### Psycopg 3.0.2

- Fix type hint for [`sql.SQL.join()`](api/sql.md#psycopg.sql.SQL.join) (ticket [#127](https://github.com/psycopg/psycopg/issues/127)).
- Fix type hint for [`Connection.notifies()`](api/connections.md#psycopg.Connection.notifies) (ticket [#128](https://github.com/psycopg/psycopg/issues/128)).
- Fix call to `MultiRange.__setitem__()` with a non-iterable value and a
  slice, now raising a [`TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError) (ticket [#129](https://github.com/psycopg/psycopg/issues/129)).
- Fix disable cursors methods after close() (ticket [#125](https://github.com/psycopg/psycopg/issues/125)).

### Psycopg 3.0.1

- Fix use of the wrong dumper reusing cursors with the same query but different
  parameter types (ticket [#112](https://github.com/psycopg/psycopg/issues/112)).

## Psycopg 3.0

First stable release. Changed from 3.0b1:

- Add [Geometry adaptation using Shapely](basic/pgtypes.md#adapt-shapely) (ticket [#80](https://github.com/psycopg/psycopg/issues/80)).
- Add [Multirange adaptation](basic/pgtypes.md#adapt-multirange) (ticket [#75](https://github.com/psycopg/psycopg/issues/75)).
- Add [`pq.__build_version__`](api/pq.md#psycopg.pq.__build_version__) constant.
- Don’t use the extended protocol with COPY, (tickets [#78](https://github.com/psycopg/psycopg/issues/78), [#82](https://github.com/psycopg/psycopg/issues/82)).
- Add `context` parameter to [`connect()`](api/connections.md#psycopg.Connection.connect) (ticket [#83](https://github.com/psycopg/psycopg/issues/83)).
- Fix selection of dumper by oid after [`set_types()`](api/copy.md#psycopg.Copy.set_types).
- Drop `Connection.client_encoding`. Use [`ConnectionInfo.encoding`](api/objects.md#psycopg.ConnectionInfo.encoding) to read
  it, and a `SET` statement to change it.
- Add binary packages for Python 3.10 (ticket [#103](https://github.com/psycopg/psycopg/issues/103)).

### Psycopg 3.0b1

- First public release on PyPI.

# `psycopg_pool` – Connection pool implementations

<a id="index-0"></a>

<a id="module-psycopg_pool"></a>

A connection pool is an object used to create and maintain a limited amount of
PostgreSQL connections, reducing the time requested by the program to obtain a
working connection and allowing an arbitrary large number of concurrent
threads or tasks to use a controlled amount of resources on the server. See
[Connection pools](../advanced/pool.md#connection-pools) for more details and usage pattern.

This package exposes a few connection pool classes:

- [`ConnectionPool`](#psycopg_pool.ConnectionPool) is a synchronous connection pool yielding
  [`Connection`](connections.md#psycopg.Connection) objects and can be used by multithread applications.
- [`AsyncConnectionPool`](#psycopg_pool.AsyncConnectionPool) has an interface similar to `ConnectionPool`, but
  with [`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio) functions replacing blocking functions, and yields
  [`AsyncConnection`](connections.md#psycopg.AsyncConnection) instances.
- [`NullConnectionPool`](#psycopg_pool.NullConnectionPool) is a `ConnectionPool` subclass exposing the same
  interface of its parent, but not keeping any unused connection in its state.
  See [Null connection pools](../advanced/pool.md#null-pool) for details about related use cases.
- [`AsyncNullConnectionPool`](#psycopg_pool.AsyncNullConnectionPool) has the same behaviour of the
  `NullConnectionPool`, but with the same async interface of the
  `AsyncConnectionPool`.

#### NOTE
The `psycopg_pool` package is distributed separately from the main
[`psycopg`](module.md#module-psycopg) package: use `pip install "psycopg[pool]"`, or `pip install
psycopg_pool`, to make it available. See [Installing the connection pool](../basic/install.md#pool-installation).

The version numbers indicated in this page refer to the `psycopg_pool`
package, not to [`psycopg`](module.md#module-psycopg).

## The `ConnectionPool` class

### *class* psycopg_pool.ConnectionPool(conninfo: str | ~collections.abc.Callable[[], str] = '', \*, connection_class: type[~psycopg_pool.abc.CT] = <class 'psycopg.Connection'>, kwargs: dict[str, ~typing.Any] | ~collections.abc.Callable[[], dict[str, ~typing.Any]] | None = None, min_size: int = 4, max_size: int | None = None, open: bool | None = None, configure: ~collections.abc.Callable[[~psycopg_pool.abc.CT], None] | None = None, check: ~collections.abc.Callable[[~psycopg_pool.abc.CT], None] | None = None, reset: ~collections.abc.Callable[[~psycopg_pool.abc.CT], None] | None = None, name: str | None = None, close_returns: bool = False, timeout: float = 30.0, max_waiting: int = 0, max_lifetime: float = 3600.0, max_idle: float = 600.0, reconnect_timeout: float = 300.0, reconnect_failed: ~collections.abc.Callable[[~psycopg_pool.pool.ConnectionPool[~typing.Any]], None] | None = None, num_workers: int = 3)

This class implements a connection pool serving [`Connection`](connections.md#psycopg.Connection)
instances (or subclasses). The constructor has *alot* of arguments, but
only `conninfo` and `min_size` are the fundamental ones, all the other
arguments have meaningful defaults and can probably be tweaked later, if
required.

* **Parameters:**
  * **conninfo** (`str` or `Callable[[], str]`) – The connection string. See [`connect()`](connections.md#psycopg.Connection.connect)
    for details. If it is a callable it will be called at
    every connection attempt.
  * **connection_class** (`type`, default: [`Connection`](connections.md#psycopg.Connection)) – The class of the connections to serve. It should
    be a `Connection` subclass.
  * **kwargs** (`dict[str, Any]` or `Callable[[], dict[str, Any]]`) – Extra arguments to pass to `connect()`. Note that this is
    *one dict argument* of the pool constructor, which is
    expanded as `connect()` keyword parameters. If it is a
    callable it will be called at every connection attempt.
  * **min_size** (`int`, default: 4) – The minimum number of connection the pool will hold. The
    pool will actively try to create new connections if some
    are lost (closed, broken) and will try to never go below
    `min_size`.
  * **max_size** (`int`, default: `None`) – The maximum number of connections the pool will hold. If
    `None`, or equal to `min_size`, the pool will not grow or
    shrink. If larger than `min_size`, the pool can grow if
    more than `min_size` connections are requested at the same
    time and will shrink back after the extra connections have
    been unused for more than `max_idle` seconds.
  * **open** (`bool`, default: `True`) – If `True`, open the pool, creating the required connections,
    on init. If `False`, open the pool when `open()` is called or
    when the pool context is entered. See the [`open()`](#psycopg_pool.ConnectionPool.open) method
    documentation for more details.
  * **configure** (`Callable[[Connection], None]`) – A callback to configure a connection after creation.
    Useful, for instance, to configure its adapters. If the
    connection is used to run internal queries (to inspect the
    database) make sure to close an eventual transaction
    before leaving the function.
  * **check** (`Callable[[Connection], None]`) – A callback to check that a connection is working correctly
    when obtained by the pool. The callback is called at every
    [`getconn()`](#psycopg_pool.ConnectionPool.getconn) or [`connection()`](#psycopg_pool.ConnectionPool.connection): the connection is only passed
    to the client if the callback doesn’t throw an exception.
    By default no check is made on the connection. You can
    provide the [`check_connection()`](#psycopg_pool.ConnectionPool.check_connection) pool static method if you
    want to perform a simple check.
  * **close_returns** (`bool`, default: `False`) – If `True`, calling [`close()`](connections.md#psycopg.Connection.close) on
    the connection will not actually close it, but it
    will return the connection to the pool, like in
    [`putconn()`](#psycopg_pool.ConnectionPool.putconn). Use it if you want to
    use Psycopg pool with SQLAlchemy. See
    [Integration with SQLAlchemy](../advanced/pool.md#pool-sqlalchemy).
  * **reset** (`Callable[[Connection], None]`) – A callback to reset a function after it has been returned to
    the pool. The connection is guaranteed to be passed to the
    `reset()` function in “idle” state (no transaction). When
    leaving the `reset()` function the connection must be left in
    *idle* state, otherwise it is discarded.
  * **name** (`str`) – An optional name to give to the pool, useful, for instance, to
    identify it in the logs if more than one pool is used. if not
    specified pick a sequential name such as `pool-1`,
    `pool-2`, etc.
  * **timeout** (`float`, default: 30 seconds) – The default maximum time in seconds that a client can wait
    to receive a connection from the pool (using [`connection()`](#psycopg_pool.ConnectionPool.connection)
    or [`getconn()`](#psycopg_pool.ConnectionPool.getconn)). Note that these methods allow to override
    the `timeout` default.
  * **max_waiting** (`int`, default: 0) – Maximum number of requests that can be queued to the
    pool, after which new requests will fail, raising
    [`TooManyRequests`](#psycopg_pool.TooManyRequests). 0 means no queue limit.
  * **max_lifetime** (`float`, default: 1 hour) – The maximum lifetime of a connection in the pool, in
    seconds. Connections used for longer get closed and
    replaced by a new one. The amount is reduced by a
    random amount up to 5% to avoid mass eviction.
  * **max_idle** (`float`, default: 10 minutes) – Maximum time, in seconds, that a connection can stay unused
    in the pool before being closed, and the pool shrunk. This
    only happens to connections more than `min_size`, if
    `max_size` allowed the pool to grow.
  * **reconnect_timeout** (`float`, default: 5 minutes) – Maximum time, in seconds, the pool will try to
    create a connection. If a connection attempt
    fails, the pool will try to reconnect a few
    times, using an exponential backoff and some
    random factor to avoid mass attempts. If repeated
    attempts fail, after `reconnect_timeout` second
    the connection attempt is aborted and the
    `reconnect_failed()` callback invoked.
  * **reconnect_failed** (`Callable[[ConnectionPool], None]`) – Callback invoked if an attempt to create a new
    connection fails for more than `reconnect_timeout`
    seconds. The user may decide, for instance, to
    terminate the program (executing `sys.exit()`).
    By default don’t do anything: restart a new
    connection attempt (if the number of connection
    fell below `min_size`).
  * **num_workers** (`int`, default: 3) – Number of background worker threads used to maintain the
    pool state. Background workers are used for example to
    create new connections and to clean up connections when
    they are returned to the pool.

#### Versionchanged
Changed in version 3.1: added `open` parameter to the constructor.

#### Versionchanged
Changed in version 3.2: added `check` parameter to the constructor.

#### Versionchanged
Changed in version 3.2: the class is generic and `connection_class` provides types type
variable. See [Generic pool types](../advanced/typing.md#pool-generic).

#### Versionchanged
Changed in version 3.3: added `close_returns` parameter to the constructor.

#### Versionchanged
Changed in version 3.3: `conninfo` and `kwargs` can be callable.

#### WARNING
At the moment, the default value for the `open` parameter is `True`;
In a future version, the default will be changed to `False`.

If you expect the pool to be open on creation even if you don’t use
the pool as context manager, you should specify the parameter
`open=True` explicitly.

Starting from psycopg_pool 3.2, a warning is raised if the pool is
used with the expectation of being implicitly opened in the
constructor and `open` is not specified.

#### connection(timeout: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [Iterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[CT]

Context manager to obtain a connection from the pool.

Return the connection immediately if available, otherwise wait up to
*timeout* or `self.timeout` seconds and throw [`PoolTimeout`](#psycopg_pool.PoolTimeout) if a
connection is not available in time.

Upon context exit, return the connection to the pool. Apply the normal
[connection context behaviour](../basic/usage.md#with-connection) (commit/rollback
the transaction in case of success/error). If the connection is no more
in working state, replace it with a new one.

```python
with my_pool.connection() as conn:
    conn.execute(...)

# the connection is now back in the pool
```

#### Versionchanged
Changed in version 3.2: The connection returned is annotated as defined in `connection_class`.
See [Generic pool types](../advanced/typing.md#pool-generic).

#### open(wait: [bool](https://docs.python.org/3/library/functions.html#bool) = False, timeout: [float](https://docs.python.org/3/library/functions.html#float) = 30.0) → [None](https://docs.python.org/3/library/constants.html#None)

Open the pool by starting connecting and and accepting clients.

If *wait* is `False`, return immediately and let the background worker
fill the pool if [`min_size`](#psycopg_pool.ConnectionPool.min_size) > 0. Otherwise wait up to *timeout* seconds
for the requested number of connections to be ready (see [`wait()`](#psycopg_pool.ConnectionPool.wait) for
details).

It is safe to call `open()` again on a pool already open (because the
method was already called, or because the pool context was entered, or
because the pool was initialized with *open* = `True`) but you cannot
currently re-open a closed pool.

#### Versionadded
Added in version 3.1.

#### close(timeout: [float](https://docs.python.org/3/library/functions.html#float) = 5.0) → [None](https://docs.python.org/3/library/constants.html#None)

Close the pool and make it unavailable to new clients.

All the waiting and future clients will fail to acquire a connection
with a [`PoolClosed`](#psycopg_pool.PoolClosed) exception. Currently used connections will not be
closed until returned to the pool.

Wait *timeout* seconds for threads to terminate their job, if positive.
If the timeout expires the pool is closed anyway, although it may raise
some warnings on exit.

#### NOTE
The pool can be also used as a context manager, in which case it will
be opened (if necessary) on entering the block and closed on exiting it:

```python
with ConnectionPool(...) as pool:
    # code using the pool
```

#### wait(timeout: [float](https://docs.python.org/3/library/functions.html#float) = 30.0) → [None](https://docs.python.org/3/library/constants.html#None)

Wait for the pool to be full (with [`min_size`](#psycopg_pool.ConnectionPool.min_size) connections) after creation.

Close the pool, and raise [`PoolTimeout`](#psycopg_pool.PoolTimeout), if not ready within *timeout*
sec.

Calling this method is not mandatory: you can try and use the pool
immediately after its creation. The first client will be served as soon
as a connection is ready. You can use this method if you prefer your
program to terminate in case the environment is not configured
properly, rather than trying to stay up the hardest it can.

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

The name of the pool set on creation, or automatically generated if not
set.

#### min_size

#### max_size

The current minimum and maximum size of the pool. Use [`resize()`](#psycopg_pool.ConnectionPool.resize) to
change them at runtime.

#### resize(min_size: [int](https://docs.python.org/3/library/functions.html#int), max_size: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Change the size of the pool during runtime.

#### check() → [None](https://docs.python.org/3/library/constants.html#None)

Verify the state of the connections currently in the pool.

Test each connection: if it works return it to the pool, otherwise
dispose of it and create a new one.

#### *static* check_connection(conn: CT) → [None](https://docs.python.org/3/library/constants.html#None)

A simple check to verify that a connection is still working.

Return quietly if the connection is still working, otherwise raise
an exception.

Used internally by [`check()`](#psycopg_pool.ConnectionPool.check), but also available for client usage,
for instance as `check` callback when a pool is created.

#### Versionadded
Added in version 3.2.

#### drain() → [None](https://docs.python.org/3/library/constants.html#None)

Remove all the connections from the pool and create new ones.

If a connection is currently out of the pool it will be closed when
returned to the pool and replaced with a new one.

This method is useful to force a connection re-configuration, for
example when the adapters map changes after the pool was created.

#### Versionadded
Added in version 3.3.

#### get_stats() → [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [int](https://docs.python.org/3/library/functions.html#int)]

Return current stats about the pool usage.

#### pop_stats() → [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [int](https://docs.python.org/3/library/functions.html#int)]

Return current stats about the pool usage.

After the call, all the counters are reset to zero.

See [Pool stats](../advanced/pool.md#pool-stats) for the metrics returned.

### Functionalities you may not need

#### getconn(timeout: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None) = None) → CT

Obtain a connection from the pool.

You should preferably use [`connection()`](#psycopg_pool.ConnectionPool.connection). Use this function only if
it is not possible to use the connection as context manager.

After using this function you *must* call a corresponding [`putconn()`](#psycopg_pool.ConnectionPool.putconn):
failing to do so will deplete the pool. A depleted pool is a sad pool:
you don’t want a depleted pool.

#### putconn(conn: CT) → [None](https://docs.python.org/3/library/constants.html#None)

Return a connection to the loving hands of its pool.

Use this function only paired with a [`getconn()`](#psycopg_pool.ConnectionPool.getconn). You don’t need to use
it if you use the much more comfortable [`connection()`](#psycopg_pool.ConnectionPool.connection) context manager.

## Pool exceptions

### *class* psycopg_pool.PoolTimeout

The pool couldn’t provide a connection in acceptable time.

Subclass of [`OperationalError`](errors.md#psycopg.OperationalError)

### *class* psycopg_pool.PoolClosed

Attempt to get a connection from a closed pool.

Subclass of [`OperationalError`](errors.md#psycopg.OperationalError)

### *class* psycopg_pool.TooManyRequests

Too many requests in the queue waiting for a connection from the pool.

Subclass of [`OperationalError`](errors.md#psycopg.OperationalError)

## The `AsyncConnectionPool` class

`AsyncConnectionPool` has a very similar interface to the [`ConnectionPool`](#psycopg_pool.ConnectionPool)
class but its blocking methods are implemented as `async` coroutines. It
returns instances of [`AsyncConnection`](connections.md#psycopg.AsyncConnection), or of its subclass if
specified so in the `connection_class` parameter.

Only the functions and parameters with different signature from
`ConnectionPool` are listed here.

### *class* psycopg_pool.AsyncConnectionPool(conninfo: str | ~collections.abc.Callable[[], str] | ~collections.abc.Callable[[], ~collections.abc.Awaitable[str]] = '', \*, connection_class: type[~psycopg_pool.abc.ACT] = <class 'psycopg.AsyncConnection'>, kwargs: dict[str, ~typing.Any] | ~collections.abc.Callable[[], dict[str, ~typing.Any]] | ~collections.abc.Callable[[], ~collections.abc.Awaitable[dict[str, ~typing.Any]]] | None = None, min_size: int = 4, max_size: int | None = None, open: bool | None = None, configure: ~collections.abc.Callable[[~psycopg_pool.abc.ACT], ~collections.abc.Awaitable[None]] | None = None, check: ~collections.abc.Callable[[~psycopg_pool.abc.ACT], ~collections.abc.Awaitable[None]] | None = None, reset: ~collections.abc.Callable[[~psycopg_pool.abc.ACT], ~collections.abc.Awaitable[None]] | None = None, name: str | None = None, close_returns: bool = False, timeout: float = 30.0, max_waiting: int = 0, max_lifetime: float = 3600.0, max_idle: float = 600.0, reconnect_timeout: float = 300.0, reconnect_failed: ~collections.abc.Callable[[~psycopg_pool.pool_async.AsyncConnectionPool[~typing.Any]], None] | ~collections.abc.Callable[[~psycopg_pool.pool_async.AsyncConnectionPool[~typing.Any]], ~collections.abc.Awaitable[None]] | None = None, num_workers: int = 3)

* **Parameters:**
  * **conninfo** (`str` or `Callable[[], str]` or `async Callable[[], str]`) – The connection string. It can be an async function too.
  * **connection_class** (`type`, default: [`AsyncConnection`](connections.md#psycopg.AsyncConnection)) – The class of the connections to serve. It should
    be an `AsyncConnection` subclass.
  * **kwargs** (`dict[str, Any]` or `Callable[[], dict[str, Any]]`
    or `async !Callable[[], dict[str, Any]]`) – Extra arguments to pass to `connect()`. It can be an async
    function too.
  * **check** (`async Callable[[Connection], None]`) – A callback to check that a connection is working correctly
    when obtained by the pool.
  * **configure** (`async Callable[[AsyncConnection], None]`) – A callback to configure a connection after creation.
  * **reset** (`async Callable[[AsyncConnection], None]`) – A callback to reset a function after it has been returned to
    the pool.
  * **reconnect_failed** (`Callable[[AsyncConnectionPool], None]` or
    `async Callable[[AsyncConnectionPool], None]`) – Callback invoked if an attempt to create a new
    connection fails for more than `reconnect_timeout` seconds.

#### Versionchanged
Changed in version 3.2: added `check` parameter to the constructor.

#### Versionchanged
Changed in version 3.2: The `reconnect_failed` parameter can be `async`.

#### Versionchanged
Changed in version 3.3: added `close_returns` parameter to the constructor.

#### Versionchanged
Changed in version 3.3: `conninfo` and `kwargs` can be callable (sync or async).

#### WARNING
Opening an async pool in the constructor (using `open=True` on init)
will become an error in a future pool versions. Please note that,
currently, `open=True` is the default; in a future version, the
default for the parameter will be changed to `False`.

In order to make sure that your code will keep working as expected in
future versions, please specify `open=False` in the constructor and
use an explicit `await pool.open()`:

```default
pool = AsyncConnectionPool(..., open=False)
await pool.open()
```

or use the pool context manager:

```default
async with AsyncConnectionPool(..., open=False) as pool:
    ...
```

Starting from psycopg_pool 3.2, opening an async pool in the
constructor raises a warning.

#### connection(timeout: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [AsyncIterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator)[ACT]

Context manager to obtain a connection from the pool.

Return the connection immediately if available, otherwise wait up to
*timeout* or `self.timeout` seconds and throw [`PoolTimeout`](#psycopg_pool.PoolTimeout) if a
connection is not available in time.

Upon context exit, return the connection to the pool. Apply the normal
[connection context behaviour](../basic/usage.md#with-connection) (commit/rollback
the transaction in case of success/error). If the connection is no more
in working state, replace it with a new one.

```python
async with my_pool.connection() as conn:
    await conn.execute(...)

# the connection is now back in the pool
```

#### *async* open(wait: [bool](https://docs.python.org/3/library/functions.html#bool) = False, timeout: [float](https://docs.python.org/3/library/functions.html#float) = 30.0) → [None](https://docs.python.org/3/library/constants.html#None)

Open the pool by starting connecting and and accepting clients.

If *wait* is `False`, return immediately and let the background worker
fill the pool if `min_size` > 0. Otherwise wait up to *timeout* seconds
for the requested number of connections to be ready (see [`wait()`](#psycopg_pool.AsyncConnectionPool.wait) for
details).

It is safe to call `open()` again on a pool already open (because the
method was already called, or because the pool context was entered, or
because the pool was initialized with *open* = `True`) but you cannot
currently re-open a closed pool.

#### *async* close(timeout: [float](https://docs.python.org/3/library/functions.html#float) = 5.0) → [None](https://docs.python.org/3/library/constants.html#None)

Close the pool and make it unavailable to new clients.

All the waiting and future clients will fail to acquire a connection
with a [`PoolClosed`](#psycopg_pool.PoolClosed) exception. Currently used connections will not be
closed until returned to the pool.

Wait *timeout* seconds for threads to terminate their job, if positive.
If the timeout expires the pool is closed anyway, although it may raise
some warnings on exit.

#### NOTE
The pool can be also used as an async context manager, in which case it
will be opened (if necessary) on entering the block and closed on
exiting it:

```python
async with AsyncConnectionPool(...) as pool:
    # code using the pool
```

All the other constructor parameters are the same of `ConnectionPool`.

#### *async* wait(timeout: [float](https://docs.python.org/3/library/functions.html#float) = 30.0) → [None](https://docs.python.org/3/library/constants.html#None)

Wait for the pool to be full (with `min_size` connections) after creation.

Close the pool, and raise [`PoolTimeout`](#psycopg_pool.PoolTimeout), if not ready within *timeout*
sec.

Calling this method is not mandatory: you can try and use the pool
immediately after its creation. The first client will be served as soon
as a connection is ready. You can use this method if you prefer your
program to terminate in case the environment is not configured
properly, rather than trying to stay up the hardest it can.

#### *async* resize(min_size: [int](https://docs.python.org/3/library/functions.html#int), max_size: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Change the size of the pool during runtime.

#### *async* check() → [None](https://docs.python.org/3/library/constants.html#None)

Verify the state of the connections currently in the pool.

Test each connection: if it works return it to the pool, otherwise
dispose of it and create a new one.

#### *async static* check_connection(conn: ACT) → [None](https://docs.python.org/3/library/constants.html#None)

A simple check to verify that a connection is still working.

Return quietly if the connection is still working, otherwise raise
an exception.

Used internally by [`check()`](#psycopg_pool.AsyncConnectionPool.check), but also available for client usage,
for instance as `check` callback when a pool is created.

#### Versionadded
Added in version 3.2.

#### *async* getconn(timeout: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None) = None) → ACT

Obtain a connection from the pool.

You should preferably use [`connection()`](#psycopg_pool.AsyncConnectionPool.connection). Use this function only if
it is not possible to use the connection as context manager.

After using this function you *must* call a corresponding [`putconn()`](#psycopg_pool.AsyncConnectionPool.putconn):
failing to do so will deplete the pool. A depleted pool is a sad pool:
you don’t want a depleted pool.

#### *async* putconn(conn: ACT) → [None](https://docs.python.org/3/library/constants.html#None)

Return a connection to the loving hands of its pool.

Use this function only paired with a [`getconn()`](#psycopg_pool.AsyncConnectionPool.getconn). You don’t need to use
it if you use the much more comfortable [`connection()`](#psycopg_pool.AsyncConnectionPool.connection) context manager.

## Null connection pools

#### Versionadded
Added in version 3.1.

The [`NullConnectionPool`](#psycopg_pool.NullConnectionPool) is a [`ConnectionPool`](#psycopg_pool.ConnectionPool) subclass which doesn’t create
connections preemptively and doesn’t keep unused connections in its state. See
[Null connection pools](../advanced/pool.md#null-pool) for further details.

The interface of the object is entirely compatible with its parent class. Its
behaviour is similar, with the following differences:

### *class* psycopg_pool.NullConnectionPool(conninfo: ConninfoParam = '', \*, connection_class: type[CT] = <class 'psycopg.Connection'>, kwargs: KwargsParam | None = None, min_size: int = 0, max_size: int | None = None, open: bool | None = None, configure: ConnectionCB[CT] | None = None, check: ConnectionCB[CT] | None = None, reset: ConnectionCB[CT] | None = None, name: str | None = None, close_returns: bool = False, timeout: float = 30.0, max_waiting: int = 0, max_lifetime: float = 3600.0, max_idle: float = 600.0, reconnect_timeout: float = 300.0, reconnect_failed: ConnectFailedCB | None = None, num_workers: int = 3)

All the other constructor parameters are the same as in [`ConnectionPool`](#psycopg_pool.ConnectionPool).

* **Parameters:**
  * **min_size** (`int`, default: 0) – Always 0, cannot be changed.
  * **max_size** (`int`, default: None) – If None or 0, create a new connection at every request,
    without a maximum. If greater than 0, don’t create more
    than `max_size` connections and queue the waiting clients.
  * **reset** (`Callable[[Connection], None]`) – It is only called when there are waiting clients in the
    queue, before giving them a connection already open. If no
    client is waiting, the connection is closed and discarded
    without a fuss.
  * **max_idle** – Ignored, as null pools don’t leave idle connections
    sitting around.

#### wait(timeout: [float](https://docs.python.org/3/library/functions.html#float) = 30.0) → [None](https://docs.python.org/3/library/constants.html#None)

Create a connection for test.

Calling this function will verify that the connectivity with the
database works as expected. However the connection will not be stored
in the pool.

Close the pool, and raise [`PoolTimeout`](#psycopg_pool.PoolTimeout), if not ready within *timeout*
sec.

#### resize(min_size: [int](https://docs.python.org/3/library/functions.html#int), max_size: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Change the size of the pool during runtime.

Only *max_size* can be changed; *min_size* must remain 0.

#### check() → [None](https://docs.python.org/3/library/constants.html#None)

No-op, as the pool doesn’t have connections in its state.

The [`AsyncNullConnectionPool`](#psycopg_pool.AsyncNullConnectionPool) is, similarly, an [`AsyncConnectionPool`](#psycopg_pool.AsyncConnectionPool) subclass
with the same behaviour of the [`NullConnectionPool`](#psycopg_pool.NullConnectionPool).

### *class* psycopg_pool.AsyncNullConnectionPool(conninfo: AsyncConninfoParam = '', \*, connection_class: type[ACT] = <class 'psycopg.AsyncConnection'>, kwargs: AsyncKwargsParam | None = None, min_size: int = 0, max_size: int | None = None, open: bool | None = None, configure: AsyncConnectionCB[ACT] | None = None, check: AsyncConnectionCB[ACT] | None = None, reset: AsyncConnectionCB[ACT] | None = None, name: str | None = None, close_returns: bool = False, timeout: float = 30.0, max_waiting: int = 0, max_lifetime: float = 3600.0, max_idle: float = 600.0, reconnect_timeout: float = 300.0, reconnect_failed: AsyncConnectFailedCB | None = None, num_workers: int = 3)

The interface is the same of its parent class [`AsyncConnectionPool`](#psycopg_pool.AsyncConnectionPool). The
behaviour is different in the same way described for [`NullConnectionPool`](#psycopg_pool.NullConnectionPool).

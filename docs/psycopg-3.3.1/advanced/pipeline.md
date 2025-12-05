<a id="pipeline-mode"></a>

# Pipeline mode support

#### Versionadded
Added in version 3.1.

The *pipeline mode* allows PostgreSQL client applications to send a query
without having to read the result of the previously sent query. Taking
advantage of the pipeline mode, a client will wait less for the server, since
multiple queries/results can be sent/received in a single network roundtrip.
Pipeline mode can provide a significant performance boost to the application.

Pipeline mode is most useful when the server is distant, i.e., network latency
(“ping time”) is high, and also when many small operations are being performed
in rapid succession. There is usually less benefit in using pipelined commands
when each query takes many multiples of the client/server round-trip time to
execute. A 100-statement operation run on a server 300 ms round-trip-time away
would take 30 seconds in network latency alone without pipelining; with
pipelining it may spend as little as 0.3 s waiting for results from the
server.

The server executes statements, and returns results, in the order the client
sends them. The server will begin executing the commands in the pipeline
immediately, not waiting for the end of the pipeline. Note that results are
buffered on the server side; the server flushes that buffer when a
[synchronization point](#pipeline-sync) is established.

#### SEE ALSO
The PostgreSQL documentation about:

- [pipeline mode](https://www.postgresql.org/docs/current/libpq-pipeline-mode.html)
- [extended query message flow](https://www.postgresql.org/docs/current/protocol-flow.html#PROTOCOL-FLOW-EXT-QUERY)

contains many details around when it is most useful to use the pipeline
mode and about errors management and interaction with transactions.

## Client-server messages flow

In order to understand better how the pipeline mode works, we should take a
closer look at the [PostgreSQL client-server message flow](https://www.postgresql.org/docs/current/protocol-flow.html).

During normal querying, each statement is transmitted by the client to the
server as a stream of request messages, terminating with a **Sync** message to
tell it that it should process the messages sent so far. The server will
execute the statement and describe the results back as a stream of messages,
terminating with a **ReadyForQuery**, telling the client that it may now send a
new query.

For example, the statement (returning no result):

```python
conn.execute("INSERT INTO mytable (data) VALUES (%s)", ["hello"])
```

results in the following two groups of messages:

| Direction                             | Message                                                                                                                                                                          |
|---------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Python<br/><br/>▶<br/><br/>PostgreSQL | - Parse `INSERT INTO ... (VALUE $1)` (skipped if<br/>  [the statement is prepared](prepare.md#prepared-statements))<br/>- Bind `'hello'`<br/>- Describe<br/>- Execute<br/>- Sync |
| PostgreSQL<br/><br/>◀<br/><br/>Python | - ParseComplete<br/>- BindComplete<br/>- NoData<br/>- CommandComplete `INSERT 0 1`<br/>- ReadyForQuery                                                                           |

and the query:

```python
conn.execute("SELECT data FROM mytable WHERE id = %s", [1])
```

results in the two groups of messages:

| Direction                             | Message                                                                                                                                                |
|---------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Python<br/><br/>▶<br/><br/>PostgreSQL | - Parse `SELECT data FROM mytable WHERE id = $1`<br/>- Bind `1`<br/>- Describe<br/>- Execute<br/>- Sync                                                |
| PostgreSQL<br/><br/>◀<br/><br/>Python | - ParseComplete<br/>- BindComplete<br/>- RowDescription    `data`<br/>- DataRow           `hello`<br/>- CommandComplete `SELECT 1`<br/>- ReadyForQuery |

The two statements, sent consecutively, pay the communication overhead four
times, once per leg.

The pipeline mode allows the client to combine several operations in longer
streams of messages to the server, then to receive more than one response in a
single batch. If we execute the two operations above in a pipeline:

```python
with conn.pipeline():
    conn.execute("INSERT INTO mytable (data) VALUES (%s)", ["hello"])
    conn.execute("SELECT data FROM mytable WHERE id = %s", [1])
```

they will result in a single roundtrip between the client and the server:

| Direction                             | Message                                                                                                                                                                                                                                                        |
|---------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Python<br/><br/>▶<br/><br/>PostgreSQL | - Parse `INSERT INTO ... (VALUE $1)`<br/>- Bind `'hello'`<br/>- Describe<br/>- Execute<br/>- Parse `SELECT data FROM mytable WHERE id = $1`<br/>- Bind `1`<br/>- Describe<br/>- Execute<br/>- Sync (sent only once)                                            |
| PostgreSQL<br/><br/>◀<br/><br/>Python | - ParseComplete<br/>- BindComplete<br/>- NoData<br/>- CommandComplete `INSERT 0 1`<br/>- ParseComplete<br/>- BindComplete<br/>- RowDescription    `data`<br/>- DataRow           `hello`<br/>- CommandComplete `SELECT 1`<br/>- ReadyForQuery (sent only once) |

<a id="pipeline-usage"></a>

## Pipeline mode usage

Psycopg supports the pipeline mode via the [`Connection.pipeline()`](../api/connections.md#psycopg.Connection.pipeline) method. The
method is a context manager: entering the `with` block yields a [`Pipeline`](../api/objects.md#psycopg.Pipeline)
object. At the end of block, the connection resumes the normal operation mode.

Within the pipeline block, you can use normally one or more cursors to execute
several operations, using [`Connection.execute()`](../api/connections.md#psycopg.Connection.execute), [`Cursor.execute()`](../api/cursors.md#psycopg.Cursor.execute) and
[`executemany()`](../api/cursors.md#psycopg.Cursor.executemany).

```python
>>> with conn.pipeline():
...     conn.execute("INSERT INTO mytable VALUES (%s)", ["hello"])
...     with conn.cursor() as cur:
...         cur.execute("INSERT INTO othertable VALUES (%s)", ["world"])
...         cur.executemany(
...             "INSERT INTO elsewhere VALUES (%s)",
...             [("one",), ("two",), ("four",)])
```

Unlike in normal mode, Psycopg will not wait for the server to receive the
result of each query; the client will receive results in batches when the
server flushes it output buffer. You can receive more than a single result
by using more than one cursor in the same pipeline.

If any statement encounters an error, the server aborts the current
transaction and will not execute any subsequent command in the queue until the
next [synchronization point](#pipeline-sync); a [`PipelineAborted`](../api/errors.md#psycopg.errors.PipelineAborted)
exception is raised for each such command. Query processing resumes after the
synchronization point.

#### WARNING
Certain features are not available in pipeline mode, including:

- COPY is not supported in pipeline mode by PostgreSQL.
- [`Cursor.stream()`](../api/cursors.md#psycopg.Cursor.stream) doesn’t make sense in pipeline mode (its job is the
  opposite of batching!).
- [`ServerCursor`](../api/cursors.md#psycopg.ServerCursor) are currently not implemented in pipeline mode.
- You cannot execute [multiple statements in the same query](../basic/from_pg2.md#multi-statements).

#### NOTE
Starting from Psycopg 3.1, [`executemany()`](../api/cursors.md#psycopg.Cursor.executemany) makes use internally of
the pipeline mode; as a consequence there is no need to handle a pipeline
block just to call `executemany()` once.

<a id="pipeline-sync"></a>

## Synchronization points

Flushing query results to the client can happen either when a synchronization
point is established by Psycopg:

- using the [`Pipeline.sync()`](../api/objects.md#psycopg.Pipeline.sync) method;
- on [`Connection.commit()`](../api/connections.md#psycopg.Connection.commit) or [`rollback()`](../api/connections.md#psycopg.Connection.rollback);
- at the end of a `Pipeline` block;
- possibly when opening a nested `Pipeline` block;
- using a fetch method such as [`Cursor.fetchone()`](../api/cursors.md#psycopg.Cursor.fetchone) (which only flushes the
  query but doesn’t issue a Sync and doesn’t reset a pipeline state error).

The server might perform a flush on its own initiative, for instance when the
output buffer is full.

Note that, even in [autocommit](../basic/transactions.md#autocommit), the server wraps the
statements sent in pipeline mode in an implicit transaction, which will be
only committed when the Sync is received. As such, a failure in a group of
statements will probably invalidate the effect of statements executed after
the previous Sync, and will propagate to the following Sync.

For example, in the following block:

```python
>>> with psycopg.connect(autocommit=True) as conn:
...     with conn.pipeline() as p, conn.cursor() as cur:
...         try:
...             cur.execute("INSERT INTO mytable (data) VALUES (%s)", ["one"])
...             cur.execute("INSERT INTO no_such_table (data) VALUES (%s)", ["two"])
...             conn.execute("INSERT INTO mytable (data) VALUES (%s)", ["three"])
...             p.sync()
...         except psycopg.errors.UndefinedTable:
...             pass
...         cur.execute("INSERT INTO mytable (data) VALUES (%s)", ["four"])
```

there will be an error in the block, `relation "no_such_table" does not
exist` caused by the insert `two`, but probably raised by the `sync()`
call. At at the end of the block, the table will contain:

```text
=# SELECT * FROM mytable;
+----+------+
| id | data |
+----+------+
|  2 | four |
+----+------+
(1 row)
```

because:

- the value 1 of the sequence is consumed by the statement `one`, but
  the record discarded because of the error in the same implicit transaction;
- the statement `three` is not executed because the pipeline is aborted (so
  it doesn’t consume a sequence item);
- the statement `four` is executed with
  success after the Sync has terminated the failed transaction.

#### WARNING
The exact Python statement where an exception caused by a server error is
raised is somewhat arbitrary: it depends on when the server flushes its
buffered result.

If you want to make sure that a group of statements is applied atomically
by the server, do make use of transaction methods such as
[`commit()`](../api/connections.md#psycopg.Connection.commit) or [`transaction()`](../api/connections.md#psycopg.Connection.transaction): these methods will
also sync the pipeline and raise an exception if there was any error in
the commands executed so far.

## The fine prints

#### WARNING
The Pipeline mode is an experimental feature.

Its behaviour, especially around error conditions and concurrency, hasn’t
been explored as much as the normal request-response messages pattern, and
its async nature makes it inherently more complex.

As we gain more experience and feedback (which is welcome), we might find
bugs and shortcomings forcing us to change the current interface or
behaviour.

The pipeline mode is available on any currently supported PostgreSQL version,
but, in order to make use of it, the client must use a libpq from PostgreSQL
14 or higher. You can use the [`has_pipeline`](../api/objects.md#psycopg.Capabilities.has_pipeline) capability to make
sure your client has the right library.

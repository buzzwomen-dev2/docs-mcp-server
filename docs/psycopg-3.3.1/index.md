# Psycopg 3 – PostgreSQL database adapter for Python

Psycopg 3 is a newly designed [PostgreSQL](https://www.postgresql.org/) database adapter for the [Python](https://www.python.org/)
programming language.

Psycopg 3 presents a familiar interface for everyone who has used
[Psycopg 2](https://www.psycopg.org/docs/) or any other [DB-API 2.0](https://www.python.org/dev/peps/pep-0249/) database adapter, but allows to use
more modern PostgreSQL and Python features, such as:

- [Asynchronous support](advanced/async.md#async)
- [COPY support from Python objects](basic/copy.md#copy)
- [A redesigned connection pool](advanced/pool.md#connection-pools)
- [Support for static typing](advanced/typing.md#static-typing)
- [Server-side parameters binding](basic/from_pg2.md#server-side-binding)
- [Prepared statements](advanced/prepare.md#prepared-statements)
- [Statements pipeline](advanced/pipeline.md#pipeline-mode)
- [Binary communication](basic/params.md#binary-data)
- [Direct access to the libpq functionalities](api/pq.md#psycopg-pq)

## Documentation

* [Getting started with Psycopg 3](basic/index.md)
  * [Installation](basic/install.md)
  * [Basic module usage](basic/usage.md)
  * [Passing parameters to SQL queries](basic/params.md)
  * [Template string queries](basic/tstrings.md)
  * [Adapting basic Python types](basic/adapt.md)
  * [Adapting other PostgreSQL types](basic/pgtypes.md)
  * [Transactions management](basic/transactions.md)
  * [Using COPY TO and COPY FROM](basic/copy.md)
  * [Differences from `psycopg2`](basic/from_pg2.md)
* [More advanced topics](advanced/index.md)
  * [Concurrent operations](advanced/async.md)
  * [Static Typing](advanced/typing.md)
  * [Row factories](advanced/rows.md)
  * [Connection pools](advanced/pool.md)
  * [Cursor types](advanced/cursors.md)
  * [Data adaptation configuration](advanced/adapt.md)
  * [Prepared statements](advanced/prepare.md)
  * [Pipeline mode support](advanced/pipeline.md)
* [Psycopg 3 API](api/index.md)
  * [The `psycopg` module](api/module.md)
  * [Connection classes](api/connections.md)
  * [Cursor classes](api/cursors.md)
  * [COPY-related objects](api/copy.md)
  * [Other top-level objects](api/objects.md)
  * [`sql` – SQL string composition](api/sql.md)
  * [`rows` – row factory implementations](api/rows.md)
  * [`errors` – Package exceptions](api/errors.md)
  * [`psycopg_pool` – Connection pool implementations](api/pool.md)
  * [`conninfo` – manipulate connection strings](api/conninfo.md)
  * [`adapt` – Types adaptation](api/adapt.md)
  * [`types` – Types information and adapters](api/types.md)
  * [`abc` – Psycopg abstract classes](api/abc.md)
  * [`pq` – libpq wrapper module](api/pq.md)
  * [`crdb` – CockroachDB support](api/crdb.md)
  * [`_dns` – DNS resolution utilities](api/dns.md)

### Release notes

* [`psycopg` release notes](news.md)
* [`psycopg_pool` release notes](news_pool.md)

### Indices and tables

* [Index](genindex.md)
* [Module Index](py-modindex.md)

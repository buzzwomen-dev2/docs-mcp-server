# The `psycopg` module

Psycopg implements the [Python Database DB API 2.0 specification](https://www.python.org/dev/peps/pep-0249/). As such
it also exposes the [module-level objects](https://www.python.org/dev/peps/pep-0249/#module-interface) required by the specifications.

<a id="module-psycopg"></a>

### psycopg.connect(conninfo: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', , autocommit: [bool](https://docs.python.org/3/library/functions.html#bool) = False, prepare_threshold: [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None) = 5, context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None, row_factory: [RowFactory](rows.md#psycopg.rows.RowFactory)[Row] | [None](https://docs.python.org/3/library/constants.html#None) = None, cursor_factory: [type](https://docs.python.org/3/library/functions.html#type)[[Cursor](cursors.md#psycopg.Cursor)[Row]] | [None](https://docs.python.org/3/library/constants.html#None) = None, \*\*kwargs: [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)) → [Self](https://docs.python.org/3/library/typing.html#typing.Self)

Connect to a database server and return a new [`Connection`](connections.md#psycopg.Connection) instance.

This is an alias of the class method [`Connection.connect`](connections.md#psycopg.Connection.connect): see its
documentation for details.

If you need an asynchronous connection use [`AsyncConnection.connect`](connections.md#psycopg.AsyncConnection.connect)
instead.

### psycopg.capabilities

An object that can be used to verify that the client library used by
psycopg implements a certain feature. For instance:

```default
# Fail at import time if encrypted passwords is not available
import psycopg
psycopg.capabilities.has_encrypt_password(check=True)

# Verify at runtime if a feature can be used
if psycopg.capabilities.has_hostaddr():
    print(conn.info.hostaddr)
else:
    print("unknown connection hostadd")
```

* **Type:**
  [`Capabilities`](objects.md#psycopg.Capabilities)

#### Versionadded
Added in version 3.2.

### Exceptions

The standard [DBAPI exceptions](https://www.python.org/dev/peps/pep-0249/#exceptions) are exposed both by the `psycopg` module
and by the [`psycopg.errors`](errors.md#module-psycopg.errors) module. The latter also exposes more specific
exceptions, mapping to the database error states (see
[SQLSTATE exceptions](errors.md#sqlstate-exceptions)).

```default
`Exception`
|__ [`Warning`](errors.md#psycopg.Warning)
|__ [`Error`](errors.md#psycopg.Error)
    |__ [`InterfaceError`](errors.md#psycopg.InterfaceError)
    |__ [`DatabaseError`](errors.md#psycopg.DatabaseError)
        |__ [`DataError`](errors.md#psycopg.DataError)
        |__ [`OperationalError`](errors.md#psycopg.OperationalError)
        |__ [`IntegrityError`](errors.md#psycopg.IntegrityError)
        |__ [`InternalError`](errors.md#psycopg.InternalError)
        |__ [`ProgrammingError`](errors.md#psycopg.ProgrammingError)
        |__ [`NotSupportedError`](errors.md#psycopg.NotSupportedError)
```

### psycopg.adapters

The default adapters map establishing how Python and PostgreSQL types are
converted into each other.

This map is used as a template when new connections are created, using
[`psycopg.connect()`](#psycopg.connect). Its [`types`](adapt.md#psycopg.adapt.AdaptersMap.types) attribute is a
[`TypesRegistry`](types.md#psycopg.types.TypesRegistry) containing information about every
PostgreSQL builtin type, useful for adaptation customisation (see
[Data adaptation configuration](../advanced/adapt.md#adaptation)):

```default
>>> psycopg.adapters.types["int4"]
<TypeInfo: int4 (oid: 23, array oid: 1007)>
```

* **Type:**
  [`AdaptersMap`](adapt.md#psycopg.adapt.AdaptersMap)

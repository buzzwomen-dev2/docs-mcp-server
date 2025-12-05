<a id="psycopg-types"></a>

# `types` – Types information and adapters

The `psycopg.types` package exposes:

- objects to describe PostgreSQL types, such as [`TypeInfo`](#psycopg.types.TypeInfo), [`TypesRegistry`](#psycopg.types.TypesRegistry),
  to help or [customise the types conversion](../advanced/adapt.md#adaptation);
- concrete implementations of [`Loader`](abc.md#psycopg.abc.Loader) and [`Dumper`](abc.md#psycopg.abc.Dumper)
  protocols to [handle builtin data types](../basic/adapt.md#types-adaptation);
- helper objects to represent PostgreSQL data types which [don’t have a
  straightforward Python representation](../basic/pgtypes.md#extra-adaptation), such as
  [`Range`](../basic/pgtypes.md#psycopg.types.range.Range).

## Types information

The [`TypeInfo`](#psycopg.types.TypeInfo) object describes simple information about a PostgreSQL data
type, such as its name, oid and array oid. `TypeInfo` subclasses may hold more
information, for instance the components of a composite type.

You can use [`TypeInfo.fetch()`](#psycopg.types.TypeInfo.fetch) to query information from a database catalog,
which is then used by helper functions, such as
[`register_hstore()`](../basic/pgtypes.md#psycopg.types.hstore.register_hstore), to register adapters on types whose
OID is not known upfront or to create more specialised adapters.

The `TypeInfo` object doesn’t instruct Psycopg to convert a PostgreSQL type
into a Python type: this is the role of a [`Loader`](abc.md#psycopg.abc.Loader). However it
can extend the behaviour of other adapters: if you create a loader for
`MyType`, using the [`TypeInfo`](#psycopg.types.TypeInfo) information, Psycopg will be able to manage
seamlessly arrays of `MyType` or ranges and composite types using `MyType`
as a subtype.

#### SEE ALSO
[Data adaptation configuration](../advanced/adapt.md#adaptation) describes how to convert from Python objects to
PostgreSQL types and back.

```python
from psycopg.adapt import Loader
from psycopg.types import TypeInfo

t = TypeInfo.fetch(conn, "mytype")
t.register(conn)

for record in conn.execute("SELECT mytypearray FROM mytable"):
    # records will return lists of "mytype" as string

class MyTypeLoader(Loader):
    def load(self, data):
        # parse the data and return a MyType instance

conn.adapters.register_loader("mytype", MyTypeLoader)

for record in conn.execute("SELECT mytypearray FROM mytable"):
    # records will return lists of MyType instances
```

### *class* psycopg.types.TypeInfo(name: str, oid: int, array_oid: int, \*, regtype: str = '', delimiter: str = ', ', typemod: type[~psycopg._typemod.TypeModifier] = <class 'psycopg._typemod.TypeModifier'>)

Hold information about a PostgreSQL base type.

#### *classmethod* fetch(conn, name)

#### *async classmethod* fetch(aconn, name)

Query a system catalog to read information about a type.

* **Parameters:**
  * **conn** ([*Connection*](connections.md#psycopg.Connection) *or* [*AsyncConnection*](connections.md#psycopg.AsyncConnection)) – the connection to query
  * **name** (`str` or [`Identifier`](sql.md#psycopg.sql.Identifier)) – the name of the type to query. It can include a schema
    name.
* **Returns:**
  a `TypeInfo` object (or subclass) populated with the type
  information, `None` if not found.

If the connection is async, `fetch()` will behave as a coroutine and
the caller will need to `await` on it to get the result:

```default
t = await TypeInfo.fetch(aconn, "mytype")
```

#### register(context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Register the type information, globally or in the specified `context`.

* **Parameters:**
  **context** (*Optional* *[*[*AdaptContext*](abc.md#psycopg.abc.AdaptContext) *]*) – the context where the type is registered, for instance
  a [`Connection`](connections.md#psycopg.Connection) or [`Cursor`](cursors.md#psycopg.Cursor). `None` registers
  the `TypeInfo` globally.

Registering the [`TypeInfo`](#psycopg.types.TypeInfo) in a context allows the adapters of that
context to look up type information: for instance it allows to
recognise automatically arrays of that type and load them from the
database as a list of the base type.

In order to get information about dynamic PostgreSQL types, Psycopg offers a
few `TypeInfo` subclasses, whose `fetch()` method can extract more complete
information about the type, such as [`CompositeInfo`](../basic/pgtypes.md#psycopg.types.composite.CompositeInfo),
[`RangeInfo`](../basic/pgtypes.md#psycopg.types.range.RangeInfo), [`MultirangeInfo`](../basic/pgtypes.md#psycopg.types.multirange.MultirangeInfo),
[`EnumInfo`](../basic/adapt.md#psycopg.types.enum.EnumInfo).

`TypeInfo` objects are collected in [`TypesRegistry`](#psycopg.types.TypesRegistry) instances, which help type
information lookup. Every [`AdaptersMap`](adapt.md#psycopg.adapt.AdaptersMap) exposes its type map on
its [`types`](adapt.md#psycopg.adapt.AdaptersMap.types) attribute.

### *class* psycopg.types.TypesRegistry(template: [TypesRegistry](#psycopg.types.TypesRegistry) | [None](https://docs.python.org/3/library/constants.html#None) = None)

Container for the information about types in a database.

`TypeRegistry` instances are typically exposed by
[`AdaptersMap`](adapt.md#psycopg.adapt.AdaptersMap) objects in adapt contexts such as
[`Connection`](connections.md#psycopg.Connection) or [`Cursor`](cursors.md#psycopg.Cursor) (e.g. `conn.adapters.types`).

The global registry, from which the others inherit from, is available as
[`psycopg.adapters`](module.md#psycopg.adapters)`.types`.

#### \_\_getitem_\_(key: [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int)) → [TypeInfo](#psycopg.types.TypeInfo)

#### \_\_getitem_\_(key: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[type](https://docs.python.org/3/library/functions.html#type)[T], [int](https://docs.python.org/3/library/functions.html#int)]) → T

Return info about a type, specified by name or oid

* **Parameters:**
  **key** – the name or oid of the type to look for.

Raise KeyError if not found.

```python
>>> import psycopg

>>> psycopg.adapters.types["text"]
<TypeInfo: text (oid: 25, array oid: 1009)>

>>> psycopg.adapters.types[23]
<TypeInfo: int4 (oid: 23, array oid: 1007)>
```

#### get(key: [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int)) → [TypeInfo](#psycopg.types.TypeInfo) | [None](https://docs.python.org/3/library/constants.html#None)

#### get(key: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[type](https://docs.python.org/3/library/functions.html#type)[T], [int](https://docs.python.org/3/library/functions.html#int)]) → T | [None](https://docs.python.org/3/library/constants.html#None)

Return info about a type, specified by name or oid

* **Parameters:**
  **key** – the name or oid of the type to look for.

Unlike [`__getitem__`](#psycopg.types.TypesRegistry.__getitem__), return None if not found.

#### get_oid(name: [str](https://docs.python.org/3/library/stdtypes.html#str)) → [int](https://docs.python.org/3/library/functions.html#int)

Return the oid of a PostgreSQL type by name.

* **Parameters:**
  **key** – the name of the type to look for.

Return the array oid if the type ends with “`[]`”

Raise KeyError if the name is unknown.

```python
>>> psycopg.adapters.types.get_oid("text[]")
1009
```

#### get_by_subtype(cls: [type](https://docs.python.org/3/library/functions.html#type)[T], subtype: [int](https://docs.python.org/3/library/functions.html#int) | [str](https://docs.python.org/3/library/stdtypes.html#str)) → T | [None](https://docs.python.org/3/library/constants.html#None)

Return info about a [`TypeInfo`](#psycopg.types.TypeInfo) subclass by its element name or oid.

* **Parameters:**
  * **cls** – the subtype of `TypeInfo` to look for. Currently
    supported are [`RangeInfo`](../basic/pgtypes.md#psycopg.types.range.RangeInfo) and
    [`MultirangeInfo`](../basic/pgtypes.md#psycopg.types.multirange.MultirangeInfo).
  * **subtype** – The name or OID of the subtype of the element to look for.
* **Returns:**
  The `TypeInfo` object of class `cls` whose subtype is
  `subtype`. `None` if the element or its range are not found.

<a id="json-adapters"></a>

## JSON adapters

See [JSON adaptation](../basic/adapt.md#adapt-json) for details.

### *class* psycopg.types.json.Json(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any), dumps: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[Any](https://docs.python.org/3/library/typing.html#typing.Any)], [str](https://docs.python.org/3/library/stdtypes.html#str) | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)] | [None](https://docs.python.org/3/library/constants.html#None) = None)

### *class* psycopg.types.json.Jsonb(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any), dumps: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[Any](https://docs.python.org/3/library/typing.html#typing.Any)], [str](https://docs.python.org/3/library/stdtypes.html#str) | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)] | [None](https://docs.python.org/3/library/constants.html#None) = None)

Wrappers to signal to convert `obj` to a json or jsonb PostgreSQL value.

Any object supported by the underlying `dumps()` function can be wrapped.

If a `dumps` function is passed to the wrapper, use it to dump the wrapped
object. Otherwise use the function specified by [`set_json_dumps()`](#psycopg.types.json.set_json_dumps).

### psycopg.types.json.set_json_dumps(dumps: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[Any](https://docs.python.org/3/library/typing.html#typing.Any)], [str](https://docs.python.org/3/library/stdtypes.html#str) | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)], context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Set the JSON serialisation function to store JSON objects in the database.

* **Parameters:**
  * **dumps** (`Callable[[Any], str]`) – The dump function to use.
  * **context** ([`Connection`](connections.md#psycopg.Connection) or [`Cursor`](cursors.md#psycopg.Cursor)) – Where to use the `dumps` function. If not specified, use it
    globally.

By default dumping JSON uses the builtin [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps). You can override
it to use a different JSON library or to use customised arguments.

If the [`Json`](#psycopg.types.json.Json) wrapper specified a `dumps` function, use it in precedence
of the one set by this function.

### psycopg.types.json.set_json_loads(loads: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[str](https://docs.python.org/3/library/stdtypes.html#str) | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)], [Any](https://docs.python.org/3/library/typing.html#typing.Any)], context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Set the JSON parsing function to fetch JSON objects from the database.

* **Parameters:**
  * **loads** (`Callable[[bytes], Any]`) – The load function to use.
  * **context** ([`Connection`](connections.md#psycopg.Connection) or [`Cursor`](cursors.md#psycopg.Cursor)) – Where to use the `loads` function. If not specified, use
    it globally.

By default loading JSON uses the builtin [`json.loads`](https://docs.python.org/3/library/json.html#json.loads). You can override
it to use a different JSON library or to use customised arguments.

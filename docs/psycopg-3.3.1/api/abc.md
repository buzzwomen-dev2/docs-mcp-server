# `abc` – Psycopg abstract classes

The module exposes Psycopg definitions which can be used for static type
checking.

<a id="module-psycopg.abc"></a>

#### SEE ALSO
[Dumpers and loaders life cycle](../advanced/adapt.md#adapt-life-cycle) for more information about how these objects
are used by Psycopg,

### *class* psycopg.abc.Dumper(cls, context=None)

Convert Python objects of type `cls` to PostgreSQL representation.

This class is a formal [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol). A partial implementation of
this protocol (implementing everything except the [`dump()`](#psycopg.abc.Dumper.dump) metood) is
available as [`psycopg.adapt.Dumper`](adapt.md#psycopg.adapt.Dumper).

* **Parameters:**
  * **cls** ([*type*](https://docs.python.org/3/library/functions.html#type)) – The type that will be managed by this dumper.
  * **context** ([`AdaptContext`](#psycopg.abc.AdaptContext) or None) – The context where the transformation is performed. If not
    specified the conversion might be inaccurate, for instance it will not
    be possible to know the connection encoding or the server date format.

#### format *: [Format](pq.md#psycopg.pq.Format)*

The format that this class [`dump()`](#psycopg.abc.Dumper.dump) method produces,
[`TEXT`](pq.md#psycopg.pq.Format.TEXT) or [`BINARY`](pq.md#psycopg.pq.Format.BINARY).

This is a class attribute.

#### dump(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any)) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [bytearray](https://docs.python.org/3/library/stdtypes.html#bytearray) | [memoryview](https://docs.python.org/3/library/stdtypes.html#memoryview) | [None](https://docs.python.org/3/library/constants.html#None)

Convert the object `obj` to PostgreSQL representation.

* **Parameters:**
  **obj** – the object to convert.

The format returned by dump shouldn’t contain quotes or escaped
values.

#### Versionchanged
Changed in version 3.2: `dump()` can also return `None`, to represent a `NULL` in
the database.

#### quote(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any)) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [bytearray](https://docs.python.org/3/library/stdtypes.html#bytearray) | [memoryview](https://docs.python.org/3/library/stdtypes.html#memoryview)

Convert the object `obj` to escaped representation.

* **Parameters:**
  **obj** – the object to convert.

This method only makes sense for text dumpers; the result of calling
it on a binary dumper is undefined. It might scratch your car, or burn
your cake. Don’t tell me I didn’t warn you.

#### oid *: [int](https://docs.python.org/3/library/functions.html#int)*

The oid to pass to the server, if known; 0 otherwise (class attribute).

If the OID is not specified, PostgreSQL will try to infer the type
from the context, but this may fail in some contexts and may require a
cast (e.g. specifying `%s::*type*` for its placeholder).

You can use the [`psycopg.adapters`](module.md#psycopg.adapters)`.`[`types`](adapt.md#psycopg.adapt.AdaptersMap.types) registry to find the OID of builtin
types, and you can use [`TypeInfo`](types.md#psycopg.types.TypeInfo) to extend the
registry to custom types.

#### get_key(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any), format: [PyFormat](adapt.md#psycopg.adapt.PyFormat)) → [type](https://docs.python.org/3/library/functions.html#type) | [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[DumperKey, ...]

Return an alternative key to upgrade the dumper to represent `obj`.

* **Parameters:**
  * **obj** – The object to convert
  * **format** – The format to convert to

Normally the type of the object is all it takes to define how to dump
the object to the database. For instance, a Python [`date`](https://docs.python.org/3/library/datetime.html#datetime.date) can
be simply converted into a PostgreSQL `date`.

In a few cases, just the type is not enough. For example:

- A Python [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) could be represented as a
  `timestamptz` or a `timestamp`, according to whether it
  specifies a `tzinfo` or not.
- A Python int could be stored as several Postgres types: int2, int4,
  int8, numeric. If a type too small is used, it may result in an
  overflow. If a type too large is used, PostgreSQL may not want to
  cast it to a smaller type.
- Python lists should be dumped according to the type they contain to
  convert them to e.g. array of strings, array of ints (and which
  size of int?…)

In these cases, a dumper can implement `get_key()` and return a new
class, or sequence of classes, that can be used to identify the same
dumper again. If the mechanism is not needed, the method should return
the same `cls` object passed in the constructor.

If a dumper implements [`get_key()`](#psycopg.abc.Dumper.get_key) it should also implement
[`upgrade()`](#psycopg.abc.Dumper.upgrade).

#### upgrade(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any), format: [PyFormat](adapt.md#psycopg.adapt.PyFormat)) → [Dumper](#psycopg.abc.Dumper)

Return a new dumper to manage `obj`.

* **Parameters:**
  * **obj** – The object to convert
  * **format** – The format to convert to

Once `Transformer.get_dumper()` has been notified by [`get_key()`](#psycopg.abc.Dumper.get_key) that
this Dumper class cannot handle `obj` itself, it will invoke
`upgrade()`, which should return a new [`Dumper`](#psycopg.abc.Dumper) instance, which will
be reused for every objects for which `get_key()` returns the same
result.

### *class* psycopg.abc.Loader(oid, context=None)

Convert PostgreSQL values with type OID `oid` to Python objects.

This class is a formal [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol). A partial implementation of this
protocol (implementing everything except the [`load()`](#psycopg.abc.Loader.load) method) is available
as [`psycopg.adapt.Loader`](adapt.md#psycopg.adapt.Loader).

* **Parameters:**
  * **oid** ([*int*](https://docs.python.org/3/library/functions.html#int)) – The type that will be managed by this dumper.
  * **context** ([`AdaptContext`](#psycopg.abc.AdaptContext) or None) – The context where the transformation is performed. If not
    specified the conversion might be inaccurate, for instance it will not
    be possible to know the connection encoding or the server date format.

#### format *: [Format](pq.md#psycopg.pq.Format)*

The format that this class [`load()`](#psycopg.abc.Loader.load) method can convert,
[`TEXT`](pq.md#psycopg.pq.Format.TEXT) or [`BINARY`](pq.md#psycopg.pq.Format.BINARY).

This is a class attribute.

#### load(data: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [bytearray](https://docs.python.org/3/library/stdtypes.html#bytearray) | [memoryview](https://docs.python.org/3/library/stdtypes.html#memoryview)) → [Any](https://docs.python.org/3/library/typing.html#typing.Any)

Convert the data returned by the database into a Python object.

* **Parameters:**
  **data** – the data to convert.

### *class* psycopg.abc.AdaptContext(\*args, \*\*kwargs)

A context describing how types are adapted.

Example of `AdaptContext` are [`Connection`](connections.md#psycopg.Connection), [`Cursor`](cursors.md#psycopg.Cursor),
[`Transformer`](adapt.md#psycopg.adapt.Transformer), [`AdaptersMap`](adapt.md#psycopg.adapt.AdaptersMap).

Note that this is a [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol), so objects implementing
`AdaptContext` don’t need to explicitly inherit from this class.

#### SEE ALSO
[Data adaptation configuration](../advanced/adapt.md#adaptation) for an explanation about how contexts are
connected.

#### *property* adapters *: [AdaptersMap](adapt.md#psycopg.adapt.AdaptersMap)*

The adapters configuration that this object uses.

#### *property* connection *: BaseConnection[Any] | [None](https://docs.python.org/3/library/constants.html#None)*

The connection used by this object, if available.

* **Return type:**
  [`Connection`](connections.md#psycopg.Connection) or [`AsyncConnection`](connections.md#psycopg.AsyncConnection) or `None`

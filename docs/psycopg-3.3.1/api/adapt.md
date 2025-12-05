# `adapt` – Types adaptation

The `psycopg.adapt` module exposes a set of objects useful for the
configuration of *data adaptation*, which is the conversion of Python objects
to PostgreSQL data types and back.

These objects are useful if you need to configure data adaptation, i.e.
if you need to change the default way that Psycopg converts between types or
if you want to adapt custom data types and objects. You don’t need this object
in the normal use of Psycopg.

See [Data adaptation configuration](../advanced/adapt.md#adaptation) for an overview of the Psycopg adaptation system.

## Dumpers and loaders

### *class* psycopg.adapt.Dumper(cls, context=None)

Convert Python object of the type `cls` to PostgreSQL representation.

This is an [abstract base class](https://docs.python.org/glossary.html#term-abstract-base-class), partially implementing the
[`Dumper`](abc.md#psycopg.abc.Dumper) protocol. Subclasses *must* at least implement the
[`dump()`](#psycopg.adapt.Dumper.dump) method and optionally override other members.

#### *abstractmethod* dump(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any)) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [bytearray](https://docs.python.org/3/library/stdtypes.html#bytearray) | [memoryview](https://docs.python.org/3/library/stdtypes.html#memoryview) | [None](https://docs.python.org/3/library/constants.html#None)

Convert the object `obj` to PostgreSQL representation.

* **Parameters:**
  **obj** – the object to convert.

#### Versionchanged
Changed in version 3.2: `dump()` can also return `None`, to represent a `NULL` in
the database.

#### format *: [psycopg.pq.Format](pq.md#psycopg.pq.Format)* *= TEXT*

Class attribute. Set it to [`BINARY`](pq.md#psycopg.pq.Format.BINARY) if the class
[`dump()`](#psycopg.adapt.Dumper.dump) methods converts the object to binary format.

#### quote(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any)) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [bytearray](https://docs.python.org/3/library/stdtypes.html#bytearray) | [memoryview](https://docs.python.org/3/library/stdtypes.html#memoryview)

By default return the [`dump()`](#psycopg.adapt.Dumper.dump) value quoted and sanitised, so
that the result can be used to build a SQL string. This works well
for most types and you won’t likely have to implement this method in a
subclass.

#### get_key(obj: Any, format: [PyFormat](#psycopg.adapt.PyFormat)) → abc.DumperKey

Implementation of the [`get_key()`](abc.md#psycopg.abc.Dumper.get_key) member of the
[`Dumper`](abc.md#psycopg.abc.Dumper) protocol. Look at its definition for details.

This implementation returns the `cls` passed in the constructor.
Subclasses needing to specialise the PostgreSQL type according to the
*value* of the object dumped (not only according to to its type)
should override this class.

#### upgrade(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any), format: [PyFormat](#psycopg.adapt.PyFormat)) → [Dumper](#psycopg.adapt.Dumper)

Implementation of the [`upgrade()`](abc.md#psycopg.abc.Dumper.upgrade) member of the
[`Dumper`](abc.md#psycopg.abc.Dumper) protocol. Look at its definition for details.

This implementation just returns `self`. If a subclass implements
[`get_key()`](#psycopg.adapt.Dumper.get_key) it should probably override `upgrade()` too.

### *class* psycopg.adapt.Loader(oid, context=None)

Convert PostgreSQL values with type OID `oid` to Python objects.

This is an [abstract base class](https://docs.python.org/glossary.html#term-abstract-base-class), partially implementing the
[`Loader`](abc.md#psycopg.abc.Loader) protocol. Subclasses *must* at least implement the
[`load()`](#psycopg.adapt.Loader.load) method and optionally override other members.

#### *abstractmethod* load(data: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [bytearray](https://docs.python.org/3/library/stdtypes.html#bytearray) | [memoryview](https://docs.python.org/3/library/stdtypes.html#memoryview)) → [Any](https://docs.python.org/3/library/typing.html#typing.Any)

Convert a PostgreSQL value to a Python object.

#### format *: [psycopg.pq.Format](pq.md#psycopg.pq.Format)* *= TEXT*

Class attribute. Set it to [`BINARY`](pq.md#psycopg.pq.Format.BINARY) if the class
[`load()`](#psycopg.adapt.Loader.load) methods converts the object from binary format.

## Other objects used in adaptations

### *class* psycopg.adapt.PyFormat(\*values)

Enum representing the format wanted for a query argument.

The value [`AUTO`](#psycopg.adapt.PyFormat.AUTO) allows psycopg to choose the best format for a certain
parameter.

#### AUTO *= 's'*

#### TEXT *= 't'*

#### BINARY *= 'b'*

### *class* psycopg.adapt.AdaptersMap(template: [AdaptersMap](#psycopg.adapt.AdaptersMap) | [None](https://docs.python.org/3/library/constants.html#None) = None, types: [TypesRegistry](types.md#psycopg.types.TypesRegistry) | [None](https://docs.python.org/3/library/constants.html#None) = None)

Establish how types should be converted between Python and PostgreSQL in
an [`AdaptContext`](abc.md#psycopg.abc.AdaptContext).

`AdaptersMap` maps Python types to [`Dumper`](#psycopg.adapt.Dumper) classes to
define how Python types are converted to PostgreSQL, and maps OIDs to
[`Loader`](#psycopg.adapt.Loader) classes to establish how query results are
converted to Python.

Every `AdaptContext` object has an underlying `AdaptersMap` defining how
types are converted in that context, exposed as the
[`adapters`](abc.md#psycopg.abc.AdaptContext.adapters) attribute: changing such map allows
to customise adaptation in a context without changing separated contexts.

When a context is created from another context (for instance when a
[`Cursor`](cursors.md#psycopg.Cursor) is created from a [`Connection`](connections.md#psycopg.Connection)), the parent’s
`adapters` are used as template for the child’s `adapters`, so that every
cursor created from the same connection use the connection’s types
configuration, but separate connections have independent mappings.

Once created, `AdaptersMap` are independent. This means that objects
already created are not affected if a wider scope (e.g. the global one) is
changed.

The connections adapters are initialised using a global `AdptersMap`
template, exposed as [`psycopg.adapters`](module.md#psycopg.adapters): changing such mapping allows to
customise the type mapping for every connections created afterwards.

The object can start empty or copy from another object of the same class.
Copies are copy-on-write: if the maps are updated make a copy. This way
extending e.g. global map by a connection or a connection map from a cursor
is cheap: a copy is only made on customisation.

#### SEE ALSO
[Data adaptation configuration](../advanced/adapt.md#adaptation) for an explanation about how contexts are
connected.

#### register_dumper(cls: [type](https://docs.python.org/3/library/functions.html#type) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None), dumper: [type](https://docs.python.org/3/library/functions.html#type)[[Dumper](abc.md#psycopg.abc.Dumper)]) → [None](https://docs.python.org/3/library/constants.html#None)

Configure the context to use `dumper` to convert objects of type `cls`.

If two dumpers with different [`format`](#psycopg.adapt.Dumper.format) are registered for the
same type, the last one registered will be chosen when the query
doesn’t specify a format (i.e. when the value is used with a `%s`
“[`AUTO`](#psycopg.adapt.PyFormat.AUTO)” placeholder).

* **Parameters:**
  * **cls** – The type to manage.
  * **dumper** – The dumper to register for `cls`.

If `cls` is specified as string it will be lazy-loaded, so that it
will be possible to register it without importing it before. In this
case it should be the fully qualified name of the object (e.g.
`"uuid.UUID"`).

If `cls` is None, only use the dumper when looking up using
[`get_dumper_by_oid()`](#psycopg.adapt.AdaptersMap.get_dumper_by_oid), which happens when we know the Postgres type to
adapt to, but not the Python type that will be adapted (e.g. in COPY
after using [`set_types()`](copy.md#psycopg.Copy.set_types)).

#### register_loader(oid: [int](https://docs.python.org/3/library/functions.html#int) | [str](https://docs.python.org/3/library/stdtypes.html#str), loader: [type](https://docs.python.org/3/library/functions.html#type)[[Loader](abc.md#psycopg.abc.Loader)]) → [None](https://docs.python.org/3/library/constants.html#None)

Configure the context to use `loader` to convert data of oid `oid`.

* **Parameters:**
  * **oid** – The PostgreSQL OID or type name to manage.
  * **loader** – The loar to register for `oid`.

If `oid` is specified as string, it refers to a type name, which is
looked up in the [`types`](#psycopg.adapt.AdaptersMap.types) registry.

#### types

The object where to look up for types information (such as the mapping
between type names and oids in the specified context).

* **Type:**
  [`TypesRegistry`](types.md#psycopg.types.TypesRegistry)

#### get_dumper(cls: [type](https://docs.python.org/3/library/functions.html#type), format: [PyFormat](#psycopg.adapt.PyFormat)) → [type](https://docs.python.org/3/library/functions.html#type)[[Dumper](abc.md#psycopg.abc.Dumper)]

Return the dumper class for the given type and format.

Raise [`ProgrammingError`](errors.md#psycopg.ProgrammingError) if a class is not available.

* **Parameters:**
  * **cls** – The class to adapt.
  * **format** – The format to dump to. If [`AUTO`](#psycopg.adapt.PyFormat.AUTO),
    use the last one of the dumpers registered on `cls`.

#### get_dumper_by_oid(oid: [int](https://docs.python.org/3/library/functions.html#int), format: [Format](pq.md#psycopg.pq.Format)) → [type](https://docs.python.org/3/library/functions.html#type)[[Dumper](abc.md#psycopg.abc.Dumper)]

Return the dumper class for the given oid and format.

Raise [`ProgrammingError`](errors.md#psycopg.ProgrammingError) if a class is not available.

* **Parameters:**
  * **oid** – The oid of the type to dump to.
  * **format** – The format to dump to.

#### get_loader(oid: [int](https://docs.python.org/3/library/functions.html#int), format: [Format](pq.md#psycopg.pq.Format)) → [type](https://docs.python.org/3/library/functions.html#type)[[Loader](abc.md#psycopg.abc.Loader)] | [None](https://docs.python.org/3/library/constants.html#None)

Return the loader class for the given oid and format.

Return `None` if not found.

* **Parameters:**
  * **oid** – The oid of the type to load.
  * **format** – The format to load from.

### *class* psycopg.adapt.Transformer(context=None)

An object that can adapt efficiently between Python and PostgreSQL.

The life cycle of the object is the query, so it is assumed that attributes
such as the server version or the connection encoding will not change. The
object have its state so adapting several values of the same type can be
optimised.

* **Parameters:**
  **context** ([`AdaptContext`](abc.md#psycopg.abc.AdaptContext)) – The context where the transformer should operate.

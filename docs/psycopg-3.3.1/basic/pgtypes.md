<a id="index-0"></a>

<a id="extra-adaptation"></a>

# Adapting other PostgreSQL types

PostgreSQL offers other data types which don’t map to native Python types.
Psycopg offers wrappers and conversion functions to allow their use.

<a id="index-1"></a>

<a id="adapt-composite"></a>

## Composite types adaptation

Psycopg can adapt PostgreSQL composite types (either created with the [`CREATE TYPE`](https://www.postgresql.org/docs/current/static/sql-createtype.html) command or implicitly defined after a table row type) to and from
Python tuples, [`namedtuple`](https://docs.python.org/3/library/collections.html#collections.namedtuple), or any suitably configured object.

Before using a composite type it is necessary to get information about it
using the [`CompositeInfo`](#psycopg.types.composite.CompositeInfo) class and to register it
using [`register_composite()`](#psycopg.types.composite.register_composite).

### *class* psycopg.types.composite.CompositeInfo(name: [str](https://docs.python.org/3/library/stdtypes.html#str), oid: [int](https://docs.python.org/3/library/functions.html#int), array_oid: [int](https://docs.python.org/3/library/functions.html#int), , regtype: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', field_names: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[str](https://docs.python.org/3/library/stdtypes.html#str)], field_types: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[int](https://docs.python.org/3/library/functions.html#int)])

Manage information about a composite type.

`CompositeInfo` is a [`TypeInfo`](../api/types.md#psycopg.types.TypeInfo) subclass: check its
documentation for the general usage, especially the
[`fetch()`](../api/types.md#psycopg.types.TypeInfo.fetch) method.

#### field_names *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

Tuple containing the field names of the composite type.

#### field_types *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[int](https://docs.python.org/3/library/functions.html#int), ...]*

Tuple containing the field OIDs of the composite type.

#### python_type *: Callable | [None](https://docs.python.org/3/library/constants.html#None)*

After [`register_composite()`](#psycopg.types.composite.register_composite) is called, it will contain the Python type
adapting the registered composite.

### psycopg.types.composite.register_composite(info: [CompositeInfo](#psycopg.types.composite.CompositeInfo), context: [AdaptContext](../api/abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None, factory: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[...], T] | [None](https://docs.python.org/3/library/constants.html#None) = None, , make_object: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)], [CompositeInfo](#psycopg.types.composite.CompositeInfo)], T] | [None](https://docs.python.org/3/library/constants.html#None) = None, make_sequence: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[T, [CompositeInfo](#psycopg.types.composite.CompositeInfo)], [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)]] | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Register the adapters to load and dump a composite type.

* **Parameters:**
  * **info** ([`CompositeInfo`](#psycopg.types.composite.CompositeInfo)) – The object with the information about the composite to register.
  * **context** ([`AdaptContext`](../api/abc.md#psycopg.abc.AdaptContext) | `None`) – The context where to register the adapters. If `None`,
    register it globally.
  * **factory** (`Callable[..., T]` | `None`) – Callable to create a Python object from the sequence of
    attributes read from the composite.
  * **make_object** (`Callable[[Sequence[Any], CompositeInfo], T]` | `None`) – optional function that will be used when loading a
    composite type from the database if the Python type is not a sequence
    compatible with the composite fields
  * **make_sequence** (`Callable[[T, CompositeInfo], Sequence[Any]]` | `None`) – optional function that will be used when dumping an
    object to the database if the object is not a sequence compatible
    with the composite fields

#### NOTE
Registering the adapters doesn’t affect objects already created, even
if they are children of the registered context. For instance,
registering the adapter globally doesn’t affect already existing
connections.

After registering the [`CompositeInfo`](#psycopg.types.composite.CompositeInfo), fetching data of the registered
composite type will invoke `factory` to create corresponding Python
objects. If no factory is specified, Psycopg will generate a
`namedtuple` with the same fields of the composite type, and
use it to return fetched data. The factory will be made available on
`info.`[`python_type`](#psycopg.types.composite.CompositeInfo.python_type).

If the `factory` is a type (and not a generic callable) then dumpers for
such type are created and registered too, so that passing objects of that
type to a query will adapt them to the registered composite type. This
assumes that the `factory` type is a sequence; if this is not the case you
can specify the `make_sequence` parameter: a function taking the object to
dump and the composite info and returning a sequence of values. See
[Example: non-sequence Python object](#composite-non-sequence).

The `factory` callable will be called with the sequence of value from the
composite. If passing the sequence of positional arguments is not suitable
for the `factory` type you can specify the `make_object` parameter: a
function taking the sequence of composite values and the type info, and
which should return a new instance of the object to load. See
[Example: non-sequence Python object](#composite-non-sequence).

#### Versionadded
Added in version 3.3: the `make_object` and `make_sequence` parameters.

<a id="composite-sequence"></a>

### Example: Python sequence

Registering a composite without `factory` information will create a
type on the fly, stored in `CompositeInfo.python_type`.

```default
>>> from psycopg.types.composite import CompositeInfo, register_composite

>>> conn.execute("CREATE TYPE card AS (value int, suit text)")

>>> info = CompositeInfo.fetch(conn, "card")
>>> register_composite(info, conn)

>>> my_card = info.python_type(8, "hearts")
>>> my_card
card(value=8, suit='hearts')

>>> conn.execute(
...     "SELECT pg_typeof(%(card)s), (%(card)s).suit", {"card": my_card}
...     ).fetchone()
('card', 'hearts')

>>> conn.execute("SELECT (%s, %s)::card", [1, "spades"]).fetchone()[0]
card(value=1, suit='spades')
```

Nested composite types are handled as expected, provided that the type of the
composite components are registered as well:

```default
>>> conn.execute("CREATE TYPE card_back AS (face card, back text)")

>>> info2 = CompositeInfo.fetch(conn, "card_back")
>>> register_composite(info2, conn)

>>> conn.execute("SELECT ((8, 'hearts'), 'blue')::card_back").fetchone()[0]
card_back(face=card(value=8, suit='hearts'), back='blue')
```

<a id="composite-non-sequence"></a>

### Example: non-sequence Python object

#### Versionadded
Added in version 3.3.

If your Python type takes keyword arguments, or if the sequence of value
coming from the PostgreSQL type is not suitable for it, it is possible to
specify a `make_object(*values*, *info*)` function to adapt the values
from the composite to the Python object to create, eventually making use of
the information in the type [`CompositeInfo`](#psycopg.types.composite.CompositeInfo), for example:

```default
>>> from dataclasses import dataclass
>>> from typing import Any, Sequence

>>> @dataclass
... class Card:
...     suit: str
...     value: int

>>> def card_from_db(values: Sequence[Any], info: CompositeInfo) -> Card:
...     return Card(**dict(zip(info.field_names, values)))

>>> register_composite(info, conn, make_object=card_from_db)
>>> conn.execute("select '(1,spades)'::card").fetchone()[0]
Card(suit='spades', value=1)
```

The previous example only configures loaders to convert data from PostgreSQL
to Python. If we are also interested in dumping Python `Card` objects we need
to specify `Card` as the factory (to declare which object we want to dump)
and, because `Card` is not a sequence, we need to specify a
`make_sequence(*object*, *info*)` function to convert objects attributes
into a sequence matching the composite fields:

```default
>>> def card_to_db(card: Card, info: CompositeInfo) -> Sequence[Any]:
...     return [getattr(card, name) for name in info.field_names]

>>> register_composite(
...     info, conn, factory=Card,
...     make_object=card_from_db, make_sequence=card_to_db)

>>> conn.execute(
...     "select %(card)s.value + 1, %(card)s.suit",
...     {"card": Card(suit="hearts", value=8)},
...     ).fetchone()
(9, 'hearts')
```

<a id="index-2"></a>

<a id="adapt-range"></a>

## Range adaptation

PostgreSQL [range types](https://www.postgresql.org/docs/current/rangetypes.html) are a family of data types representing a range of
values between two elements. The type of the element is called the range
*subtype*. PostgreSQL offers a few built-in range types and allows the
definition of custom ones.

All the PostgreSQL range types are loaded as the [`Range`](#psycopg.types.range.Range)
Python type, which is a [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic) type and can hold bounds of
different types.

### *class* psycopg.types.range.Range(lower: T | [None](https://docs.python.org/3/library/constants.html#None) = None, upper: T | [None](https://docs.python.org/3/library/constants.html#None) = None, bounds: [str](https://docs.python.org/3/library/stdtypes.html#str) = '[)', empty: [bool](https://docs.python.org/3/library/functions.html#bool) = False)

Python representation for a PostgreSQL range type.

* **Parameters:**
  * **lower** – lower bound for the range. `None` means unbound
  * **upper** – upper bound for the range. `None` means unbound
  * **bounds** – one of the literal strings `()`, `[)`, `(]`, `[]`,
    representing whether the lower or upper bounds are included
  * **empty** – if `True`, the range is empty

This Python type is only used to pass and retrieve range values to and
from PostgreSQL and doesn’t attempt to replicate the PostgreSQL range
features: it doesn’t perform normalization and doesn’t implement all the
[operators](https://www.postgresql.org/docs/current/static/functions-range.html#RANGE-OPERATORS-TABLE) supported by the database.

PostgreSQL will perform normalisation on `Range` objects used as query
parameters, so, when they are fetched back, they will be found in the
normal form (for instance ranges on integers will have `[)` bounds).

`Range` objects are immutable, hashable, and support the `in` operator
(checking if an element is within the range). They can be tested for
equivalence. Empty ranges evaluate to `False` in a boolean context,
nonempty ones evaluate to `True`.

`Range` objects have the following attributes:

#### isempty

`True` if the range is empty.

#### lower

The lower bound of the range. `None` if empty or unbound.

#### upper

The upper bound of the range. `None` if empty or unbound.

#### lower_inc

`True` if the lower bound is included in the range.

#### upper_inc

`True` if the upper bound is included in the range.

#### lower_inf

`True` if the range doesn’t have a lower bound.

#### upper_inf

`True` if the range doesn’t have an upper bound.

The built-in range objects are adapted automatically: if a `Range` objects
contains [`date`](https://docs.python.org/3/library/datetime.html#datetime.date) bounds, it is dumped using the `daterange` OID,
and of course `daterange` values are loaded back as `Range[date]`.

If you create your own range type you can use [`RangeInfo`](#psycopg.types.range.RangeInfo)
and [`register_range()`](#psycopg.types.range.register_range) to associate the range type with
its subtype and make it work like the builtin ones.

### *class* psycopg.types.range.RangeInfo(name: [str](https://docs.python.org/3/library/stdtypes.html#str), oid: [int](https://docs.python.org/3/library/functions.html#int), array_oid: [int](https://docs.python.org/3/library/functions.html#int), , regtype: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', subtype_oid: [int](https://docs.python.org/3/library/functions.html#int))

Manage information about a range type.

`RangeInfo` is a [`TypeInfo`](../api/types.md#psycopg.types.TypeInfo) subclass: check its
documentation for generic details, especially the
[`fetch()`](../api/types.md#psycopg.types.TypeInfo.fetch) method.

### psycopg.types.range.register_range(info: [RangeInfo](#psycopg.types.range.RangeInfo), context: [AdaptContext](../api/abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Register the adapters to load and dump a range type.

* **Parameters:**
  * **info** – The object with the information about the range to register.
  * **context** – The context where to register the adapters. If `None`,
    register it globally.

Register loaders so that loading data of this type will result in a [`Range`](#psycopg.types.range.Range)
with bounds parsed as the right subtype.

#### NOTE
Registering the adapters doesn’t affect objects already created, even
if they are children of the registered context. For instance,
registering the adapter globally doesn’t affect already existing
connections.

Example:

```default
>>> from psycopg.types.range import Range, RangeInfo, register_range

>>> conn.execute("CREATE TYPE strrange AS RANGE (SUBTYPE = text)")
>>> info = RangeInfo.fetch(conn, "strrange")
>>> register_range(info, conn)

>>> conn.execute("SELECT pg_typeof(%s)", [Range("a", "z")]).fetchone()[0]
'strrange'

>>> conn.execute("SELECT '[a,z]'::strrange").fetchone()[0]
Range('a', 'z', '[]')
```

<a id="index-3"></a>

<a id="adapt-multirange"></a>

## Multirange adaptation

Since PostgreSQL 14, every range type is associated with a [multirange](https://www.postgresql.org/docs/current/rangetypes.html), a
type representing a disjoint set of ranges. A multirange is
automatically available for every range, built-in and user-defined.

All the PostgreSQL range types are loaded as the
[`Multirange`](#psycopg.types.multirange.Multirange) Python type, which is a mutable
sequence of [`Range`](#psycopg.types.range.Range) elements.

### *class* psycopg.types.multirange.Multirange(items: [Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[Range](#psycopg.types.range.Range)[T]] = ())

Python representation for a PostgreSQL multirange type.

* **Parameters:**
  **items** – Sequence of ranges to initialise the object.

This Python type is only used to pass and retrieve multirange values to
and from PostgreSQL and doesn’t attempt to replicate the PostgreSQL
multirange features: overlapping items are not merged, empty ranges are
not discarded, the items are not ordered, the behaviour of [multirange
operators](https://www.postgresql.org/docs/current/static/functions-range.html#MULTIRANGE-OPERATORS-TABLE) is not replicated in Python.

PostgreSQL will perform normalisation on `Multirange` objects used as
query parameters, so, when they are fetched back, they will be found
ordered, with overlapping ranges merged, etc.

`Multirange` objects are a [`MutableSequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence) and are
totally ordered: they behave pretty much like a list of `Range`. Like
Range, they are [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic) on the subtype of their range, so you
can declare a variable to be `Multirange[date]` and mypy will complain if
you try to add it a `Range[Decimal]`.

Like for [`Range`](#psycopg.types.range.Range), built-in multirange objects are adapted
automatically: if a `Multirange` object contains `Range` with
[`date`](https://docs.python.org/3/library/datetime.html#datetime.date) bounds, it is dumped using the `datemultirange` OID, and
`datemultirange` values are loaded back as `Multirange[date]`.

If you have created your own range type you can use
[`MultirangeInfo`](#psycopg.types.multirange.MultirangeInfo) and
[`register_multirange()`](#psycopg.types.multirange.register_multirange) to associate the resulting
multirange type with its subtype and make it work like the builtin ones.

### *class* psycopg.types.multirange.MultirangeInfo(name: [str](https://docs.python.org/3/library/stdtypes.html#str), oid: [int](https://docs.python.org/3/library/functions.html#int), array_oid: [int](https://docs.python.org/3/library/functions.html#int), , regtype: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', range_oid: [int](https://docs.python.org/3/library/functions.html#int), subtype_oid: [int](https://docs.python.org/3/library/functions.html#int))

Manage information about a multirange type.

`MultirangeInfo` is a [`TypeInfo`](../api/types.md#psycopg.types.TypeInfo) subclass: check its
documentation for general details, especially the
[`fetch()`](../api/types.md#psycopg.types.TypeInfo.fetch) method.

### psycopg.types.multirange.register_multirange(info: [MultirangeInfo](#psycopg.types.multirange.MultirangeInfo), context: [AdaptContext](../api/abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Register the adapters to load and dump a multirange type.

* **Parameters:**
  * **info** – The object with the information about the range to register.
  * **context** – The context where to register the adapters. If `None`,
    register it globally.

Register loaders so that loading data of this type will result in a `Range`
with bounds parsed as the right subtype.

#### NOTE
Registering the adapters doesn’t affect objects already created, even
if they are children of the registered context. For instance,
registering the adapter globally doesn’t affect already existing
connections.

Example:

```default
>>> from psycopg.types.multirange import \
...     Multirange, MultirangeInfo, register_multirange
>>> from psycopg.types.range import Range

>>> conn.execute("CREATE TYPE strrange AS RANGE (SUBTYPE = text)")
>>> info = MultirangeInfo.fetch(conn, "strmultirange")
>>> register_multirange(info, conn)

>>> rec = conn.execute(
...     "SELECT pg_typeof(%(mr)s), %(mr)s",
...     {"mr": Multirange([Range("a", "q"), Range("l", "z")])}).fetchone()

>>> rec[0]
'strmultirange'
>>> rec[1]
Multirange([Range('a', 'z', '[)')])
```

<a id="index-4"></a>

<a id="adapt-hstore"></a>

## Hstore adaptation

The [`hstore`](https://www.postgresql.org/docs/current/static/hstore.html) data type is a key-value store embedded in PostgreSQL. It
supports GiST or GIN indexes allowing search by keys or key/value pairs as
well as regular BTree indexes for equality, uniqueness etc.

Psycopg can convert Python `dict` objects to and from `hstore` structures.
Only dictionaries with string keys and values are supported. `None` is also
allowed as value but not as a key.

In order to use the `hstore` data type it is necessary to load it in a
database using:

```none
=# CREATE EXTENSION hstore;
```

Because `hstore` is distributed as a contrib module, its oid is not well
known, so it is necessary to use `TypeInfo`.[`fetch()`](../api/types.md#psycopg.types.TypeInfo.fetch) to query the database and get its oid. The
resulting object can be passed to
[`register_hstore()`](#psycopg.types.hstore.register_hstore) to configure dumping `dict` to
`hstore` and parsing `hstore` back to `dict`, in the context where the
adapter is registered.

### psycopg.types.hstore.register_hstore(info: [TypeInfo](../api/types.md#psycopg.types.TypeInfo), context: [AdaptContext](../api/abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Register the adapters to load and dump hstore.

* **Parameters:**
  * **info** – The object with the information about the hstore type.
  * **context** – The context where to register the adapters. If `None`,
    register it globally.

#### NOTE
Registering the adapters doesn’t affect objects already created, even
if they are children of the registered context. For instance,
registering the adapter globally doesn’t affect already existing
connections.

Example:

```default
>>> from psycopg.types import TypeInfo
>>> from psycopg.types.hstore import register_hstore

>>> info = TypeInfo.fetch(conn, "hstore")
>>> register_hstore(info, conn)

>>> conn.execute("SELECT pg_typeof(%s)", [{"a": "b"}]).fetchone()[0]
'hstore'

>>> conn.execute("SELECT 'foo => bar'::hstore").fetchone()[0]
{'foo': 'bar'}
```

<a id="index-5"></a>

<a id="adapt-shapely"></a>

## Geometry adaptation using Shapely

When using the [PostGIS](https://postgis.net/) extension, it can be useful to retrieve [geometry](https://postgis.net/docs/geometry.html)
values and have them automatically converted to [Shapely](https://github.com/Toblerity/Shapely) instances. Likewise,
you may want to store such instances in the database and have the conversion
happen automatically.

#### WARNING
Psycopg doesn’t have a dependency on the `shapely` package: you should
install the library as an additional dependency of your project.

#### WARNING
This module is experimental and might be changed in the future according
to users’ feedback.

Since PostgGIS is an extension, the `geometry` type oid is not well
known, so it is necessary to use `TypeInfo`.[`fetch()`](../api/types.md#psycopg.types.TypeInfo.fetch) to query the database and find it. The
resulting object can be passed to [`register_shapely()`](#psycopg.psycopg.types.shapely.register_shapely)
to configure dumping [shape](https://shapely.readthedocs.io/en/stable/manual.html#shapely.geometry.shape) instances to `geometry` columns and parsing
`geometry` data back to `shape` instances, in the context where the
adapters are registered.

#### psycopg.types.shapely.register_shapely()

Register Shapely dumper and loaders.

After invoking this function on an adapter, the queries retrieving
PostGIS geometry objects will return Shapely’s shape object instances
both in text and binary mode.

Similarly, shape objects can be sent to the database.

This requires the Shapely library to be installed.

* **Parameters:**
  * **info** – The object with the information about the geometry type.
  * **context** – The context where to register the adapters. If `None`,
    register it globally.

#### NOTE
Registering the adapters doesn’t affect objects already created, even
if they are children of the registered context. For instance,
registering the adapter globally doesn’t affect already existing
connections.

Example:

```default
>>> from psycopg.types import TypeInfo
>>> from psycopg.types.shapely import register_shapely
>>> from shapely.geometry import Point

>>> info = TypeInfo.fetch(conn, "geometry")
>>> register_shapely(info, conn)

>>> conn.execute("SELECT pg_typeof(%s)", [Point(1.2, 3.4)]).fetchone()[0]
'geometry'

>>> conn.execute("""
... SELECT ST_GeomFromGeoJSON('{
...     "type":"Point",
...     "coordinates":[-48.23456,20.12345]}')
... """).fetchone()[0]
<shapely.geometry.multipolygon.MultiPolygon object at 0x7fb131f3cd90>
```

Notice that, if the geometry adapters are registered on a specific object (a
connection or cursor), other connections and cursors will be unaffected:

```default
>>> conn2 = psycopg.connect(CONN_STR)
>>> conn2.execute("""
... SELECT ST_GeomFromGeoJSON('{
...     "type":"Point",
...     "coordinates":[-48.23456,20.12345]}')
... """).fetchone()[0]
'0101000020E61000009279E40F061E48C0F2B0506B9A1F3440'
```

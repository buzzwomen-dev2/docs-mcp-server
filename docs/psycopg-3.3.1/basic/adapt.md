<a id="index-0"></a>

<a id="types-adaptation"></a>

# Adapting basic Python types

Many standard Python types are adapted into SQL and returned as Python
objects when a query is executed.

Converting the following data types between Python and PostgreSQL works
out-of-the-box and doesn’t require any configuration. In case you need to
customise the conversion you should take a look at [Data adaptation configuration](../advanced/adapt.md#adaptation).

<a id="index-1"></a>

<a id="adapt-bool"></a>

## Booleans adaptation

Python [`bool`](https://docs.python.org/3/library/functions.html#bool) values `True` and `False` are converted to the equivalent
[PostgreSQL boolean type](https://www.postgresql.org/docs/current/datatype-boolean.html):

```default
>>> cur.execute("SELECT %s, %s", (True, False))
# equivalent to "SELECT true, false"
```

#### Versionchanged
Changed in version 3.2: [`numpy.bool_`](https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.bool_) values can be dumped too.

<a id="index-2"></a>

<a id="adapt-numbers"></a>

## Numbers adaptation

#### SEE ALSO
- [PostgreSQL numeric types](https://www.postgresql.org/docs/current/static/datatype-numeric.html)

- Python [`int`](https://docs.python.org/3/library/functions.html#int) values can be converted to PostgreSQL `smallint`,
  `integer`, `bigint`, or `numeric`, according to their numeric
  value. Psycopg will choose the smallest data type available, because
  PostgreSQL can automatically cast a type up (e.g. passing a `smallint` where
  PostgreSQL expect an `integer` is gladly accepted) but will not cast down
  automatically (e.g. if a function has an `integer` argument, passing it
  a `bigint` value will fail, even if the value is 1).
- Python [`float`](https://docs.python.org/3/library/functions.html#float) values are converted to PostgreSQL `float8`.
- Python [`Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal) values are converted to PostgreSQL `numeric`.

On the way back, smaller types (`int2`, `int4`, `float4`) are
promoted to the larger Python counterpart.

#### NOTE
Sometimes you may prefer to receive `numeric` data as `float`
instead, for performance reason or ease of manipulation: you can configure
an adapter to [cast PostgreSQL numeric to Python float](../advanced/adapt.md#adapt-example-float). This of course may imply a loss of precision.

#### Versionchanged
Changed in version 3.2: NumPy [integer](https://numpy.org/doc/stable/reference/arrays.scalars.html#integer-types) and [floating point](https://numpy.org/doc/stable/reference/arrays.scalars.html#floating-point-types) values can be dumped too.

<a id="index-3"></a>

<a id="adapt-string"></a>

## Strings adaptation

#### SEE ALSO
- [PostgreSQL character types](https://www.postgresql.org/docs/current/datatype-character.html)

Python [`str`](https://docs.python.org/3/library/stdtypes.html#str) are converted to PostgreSQL string syntax, and PostgreSQL types
such as `text` and `varchar` are converted back to Python `str`:

```python
conn = psycopg.connect()
conn.execute(
    "INSERT INTO menu (id, entry) VALUES (%s, %s)",
    (1, "Crème Brûlée at 4.99€"))
conn.execute("SELECT entry FROM menu WHERE id = 1").fetchone()[0]
'Crème Brûlée at 4.99€'
```

PostgreSQL databases [have an encoding](https://www.postgresql.org/docs/current/sql-createdatabase.html), and [the session has an encoding](https://www.postgresql.org/docs/current/multibyte.html)
too, exposed in the `Connection.info.`[`encoding`](../api/objects.md#psycopg.ConnectionInfo.encoding)
attribute. If your database and connection are in UTF-8 encoding you will
likely have no problem, otherwise you will have to make sure that your
application only deals with the non-ASCII chars that the database can handle;
failing to do so may result in encoding/decoding errors:

```python
# The encoding is set at connection time according to the db configuration
conn.info.encoding
'utf-8'

# The Latin-9 encoding can manage some European accented letters
# and the Euro symbol
conn.execute("SET client_encoding TO LATIN9")
conn.execute("SELECT entry FROM menu WHERE id = 1").fetchone()[0]
'Crème Brûlée at 4.99€'

# The Latin-1 encoding doesn't have a representation for the Euro symbol
conn.execute("SET client_encoding TO LATIN1")
conn.execute("SELECT entry FROM menu WHERE id = 1").fetchone()[0]
# Traceback (most recent call last)
# ...
# UntranslatableCharacter: character with byte sequence 0xe2 0x82 0xac
# in encoding "UTF8" has no equivalent in encoding "LATIN1"
```

In rare cases you may have strings with unexpected encodings in the database.
Using the `SQL_ASCII` client encoding  will disable decoding of the data
coming from the database, which will be returned as [`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes):

```python
conn.execute("SET client_encoding TO SQL_ASCII")
conn.execute("SELECT entry FROM menu WHERE id = 1").fetchone()[0]
b'Cr\xc3\xa8me Br\xc3\xbbl\xc3\xa9e at 4.99\xe2\x82\xac'
```

Alternatively you can cast the unknown encoding data to `bytea` to
retrieve it as bytes, leaving other strings unaltered: see [Binary adaptation](#adapt-binary)

Note that PostgreSQL text cannot contain the `0x00` byte. If you need to
store Python strings that may contain binary zeros you should use a
`bytea` field.

<a id="index-4"></a>

<a id="adapt-binary"></a>

## Binary adaptation

Python types representing binary objects ([`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes), [`bytearray`](https://docs.python.org/3/library/stdtypes.html#bytearray), [`memoryview`](https://docs.python.org/3/library/stdtypes.html#memoryview))
are converted by default to `bytea` fields. By default data received is
returned as `bytes`.

If you are storing large binary data in bytea fields (such as binary documents
or images) you should probably use the binary format to pass and return
values, otherwise binary data will undergo [ASCII escaping](https://www.postgresql.org/docs/current/datatype-binary.html), taking some CPU
time and more bandwidth. See [Binary parameters and results](params.md#binary-data) for details.

<a id="adapt-date"></a>

## Date/time types adaptation

#### SEE ALSO
- [PostgreSQL date/time types](https://www.postgresql.org/docs/current/datatype-datetime.html)

- Python [`date`](https://docs.python.org/3/library/datetime.html#datetime.date) objects are converted to PostgreSQL `date`.
- Python [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) objects are converted to PostgreSQL
  `timestamp` (if they don’t have a `tzinfo` set) or `timestamptz`
  (if they do).
- Python [`time`](https://docs.python.org/3/library/datetime.html#datetime.time) objects are converted to PostgreSQL `time`
  (if they don’t have a `tzinfo` set) or `timetz` (if they do).
- Python [`timedelta`](https://docs.python.org/3/library/datetime.html#datetime.timedelta) objects are converted to PostgreSQL
  `interval`.

PostgreSQL `timestamptz` values are returned with a timezone set to the
[connection TimeZone setting](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-TIMEZONE), which is available as a Python
[`ZoneInfo`](https://docs.python.org/3/library/zoneinfo.html#zoneinfo.ZoneInfo) object in the `Connection.info`.[`timezone`](../api/objects.md#psycopg.ConnectionInfo.timezone)
attribute:

```default
>>> conn.info.timezone
zoneinfo.ZoneInfo(key='Europe/London')

>>> conn.execute("select '2048-07-08 12:00'::timestamptz").fetchone()[0]
datetime.datetime(2048, 7, 8, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='Europe/London'))
```

#### NOTE
PostgreSQL `timestamptz` doesn’t store “a timestamp with a timezone
attached”: it stores a timestamp always in UTC, which is converted, on
output, to the connection TimeZone setting:

```default
>>> conn.execute("SET TIMEZONE to 'Europe/Rome'")  # UTC+2 in summer

>>> conn.execute("SELECT '2042-07-01 12:00Z'::timestamptz").fetchone()[0]  # UTC input
datetime.datetime(2042, 7, 1, 14, 0, tzinfo=zoneinfo.ZoneInfo(key='Europe/Rome'))
```

Check out the [PostgreSQL documentation about timezones](https://www.postgresql.org/docs/current/datatype-datetime.html#DATATYPE-TIMEZONES) for all the
details.

#### WARNING
Times with timezone are silly objects, because you cannot know the offset
of a timezone with daylight saving time rules without knowing the date
too.

Although silly, times with timezone are supported both by Python and by
PostgreSQL. However they are only supported with fixed offset timezones:
Postgres `timetz` values loaded from the database will result in
Python `time` objects with `tzinfo` attributes specified as fixed
offset, for instance by a [`timezone`](https://docs.python.org/3/library/datetime.html#datetime.timezone) value:

```default
>>> conn.execute("SET TIMEZONE to 'Europe/Rome'")

# UTC+1 in winter
>>> conn.execute("SELECT '2042-01-01 12:00Z'::timestamptz::timetz").fetchone()[0]
datetime.time(13, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))

# UTC+2 in summer
>>> conn.execute("SELECT '2042-07-01 12:00Z'::timestamptz::timetz").fetchone()[0]
datetime.time(14, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)))
```

Dumping Python `time` objects is only supported with fixed offset
`tzinfo`, such as the ones returned by Postgres, or by whatever
[`tzinfo`](https://docs.python.org/3/library/datetime.html#datetime.tzinfo) implementation resulting in the time’s
[`utcoffset`](https://docs.python.org/3/library/datetime.html#datetime.time.utcoffset) returning a value.

<a id="date-time-limits"></a>

### Dates and times limits in Python

PostgreSQL date and time objects can represent values that cannot be
represented by the Python [`datetime`](https://docs.python.org/3/library/datetime.html#module-datetime) objects:

- dates and timestamps after the year 9999, the special value “infinity”;
- dates and timestamps before the year 1, the special value “-infinity”;
- the time 24:00:00.

Loading these values will raise a [`DataError`](../api/errors.md#psycopg.DataError).

If you need to handle these values you can define your own mapping (for
instance mapping every value greater than [`datetime.date.max`](https://docs.python.org/3/library/datetime.html#datetime.date.max) to `date.max`,
or the time 24:00 to 00:00) and write a subclass of the default loaders
implementing the added capability; please see [this example](../advanced/adapt.md#adapt-example-inf-date) for a reference.

<a id="index-5"></a>

<a id="datestyle"></a>

### DateStyle and IntervalStyle limits

Loading `timestamp with time zone` in text format is only supported if
the connection [DateStyle](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-DATESTYLE) is set to `ISO` format; time and time zone
representation in other formats is ambiguous.

Furthermore, at the time of writing, the only supported value for
[IntervalStyle](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-INTERVALSTYLE) is `postgres`; loading `interval` data in text format
with a different setting is not supported.

If your server is configured with different settings by default, you can
obtain a connection in a supported style using the `options` connection
parameter; for example:

```default
>>> conn = psycopg.connect(options="-c datestyle=ISO,YMD")
>>> conn.execute("show datestyle").fetchone()[0]
# 'ISO, YMD'
```

These GUC parameters only affects loading in text format; loading timestamps
or intervals in [binary format](params.md#binary-data) is not affected by
DateStyle or IntervalStyle.

<a id="adapt-json"></a>

## JSON adaptation

Psycopg can map between Python objects and PostgreSQL [json/jsonb
types](https://www.postgresql.org/docs/current/datatype-json.html), allowing to customise the load and dump function used.

Because several Python objects could be considered JSON (dicts, lists,
scalars, even date/time if using a dumps function customised to use them),
Psycopg requires you to wrap the object to dump as JSON into a wrapper:
either [`psycopg.types.json.Json`](../api/types.md#psycopg.types.json.Json) or [`Jsonb`](../api/types.md#psycopg.types.json.Jsonb).

```python
from psycopg.types.json import Jsonb

thing = {"foo": ["bar", 42]}
conn.execute("INSERT INTO mytable VALUES (%s)", [Jsonb(thing)])
```

By default Psycopg uses the standard library [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps) and [`json.loads`](https://docs.python.org/3/library/json.html#json.loads)
functions to serialize and de-serialize Python objects to JSON. If you want to
customise how serialization happens, for instance changing serialization
parameters or using a different JSON library, you can specify your own
functions using the [`psycopg.types.json.set_json_dumps()`](../api/types.md#psycopg.types.json.set_json_dumps) and
[`set_json_loads()`](../api/types.md#psycopg.types.json.set_json_loads) functions, to apply either globally or
to a specific context (connection or cursor).

```python
from functools import partial
from psycopg.types.json import Jsonb, set_json_dumps, set_json_loads
import ujson

# Use a faster dump function
set_json_dumps(ujson.dumps)

# Return floating point values as Decimal, just in one connection
set_json_loads(partial(json.loads, parse_float=Decimal), conn)

conn.execute("SELECT %s", [Jsonb({"value": 123.45})]).fetchone()[0]
# {'value': Decimal('123.45')}
```

If you need an even more specific dump customisation only for certain objects
(including different configurations in the same query) you can specify a
`dumps` parameter in the
[`Json`](../api/types.md#psycopg.types.json.Json)/[`Jsonb`](../api/types.md#psycopg.types.json.Jsonb) wrapper, which will
take precedence over what is specified by `set_json_dumps()`.

```python
from uuid import UUID, uuid4

class UUIDEncoder(json.JSONEncoder):
    """A JSON encoder which can dump UUID."""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

uuid_dumps = partial(json.dumps, cls=UUIDEncoder)
obj = {"uuid": uuid4()}
cnn.execute("INSERT INTO objs VALUES %s", [Json(obj, dumps=uuid_dumps)])
# will insert: {'uuid': '0a40799d-3980-4c65-8315-2956b18ab0e1'}
```

<a id="adapt-list"></a>

## Lists adaptation

Python [`list`](https://docs.python.org/3/library/stdtypes.html#list) objects are adapted to [PostgreSQL arrays](https://www.postgresql.org/docs/current/arrays.html) and back. Only
lists containing objects of the same type can be dumped to PostgreSQL (but the
list may contain `None` elements).

#### NOTE
If you have a list of values which you want to use with the `IN`
operator… don’t. It won’t work (neither with a list nor with a tuple):

```default
>>> conn.execute("SELECT * FROM mytable WHERE id IN %s", [[10,20,30]])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
psycopg.errors.SyntaxError: syntax error at or near "$1"
LINE 1: SELECT * FROM mytable WHERE id IN $1
                                          ^
```

What you want to do instead is to use the [‘= ANY()’ expression](https://www.postgresql.org/docs/current/functions-comparisons.html#id-1.5.8.30.16) and pass
the values as a list (not a tuple).

```pycon
>>> conn.execute("SELECT * FROM mytable WHERE id = ANY(%s)", [[10,20,30]])
```

This has also the advantage of working with an empty list, whereas `IN
()` is not valid SQL.

<a id="adapt-uuid"></a>

## UUID adaptation

Python [`uuid.UUID`](https://docs.python.org/3/library/uuid.html#uuid.UUID) objects are adapted to PostgreSQL [UUID type](https://www.postgresql.org/docs/current/datatype-uuid.html) and back:

```default
>>> conn.execute("select gen_random_uuid()").fetchone()[0]
UUID('97f0dd62-3bd2-459e-89b8-a5e36ea3c16c')

>>> from uuid import uuid4
>>> conn.execute("select gen_random_uuid() = %s", [uuid4()]).fetchone()[0]
False  # long shot
```

<a id="adapt-network"></a>

## Network data types adaptation

Objects from the [`ipaddress`](https://docs.python.org/3/library/ipaddress.html#module-ipaddress) module are converted to PostgreSQL [network
address types](https://www.postgresql.org/docs/current/datatype-net-types.html#DATATYPE-CIDR):

- [`IPv4Address`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address), [`IPv4Interface`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Interface) objects are converted
  to the PostgreSQL `inet` type. On the way back, `inet` values
  indicating a single address are converted to `IPv4Address`, otherwise they
  are converted to `IPv4Interface`
- [`IPv4Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network) objects are converted to the `cidr` type and
  back.
- [`IPv6Address`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Address), [`IPv6Interface`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Interface),
  [`IPv6Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network) objects follow the same rules, with IPv6
  `inet` and `cidr` values.

```python
>>> conn.execute("select '192.168.0.1'::inet, '192.168.0.1/24'::inet").fetchone()
(IPv4Address('192.168.0.1'), IPv4Interface('192.168.0.1/24'))

>>> conn.execute("select '::ffff:1.2.3.0/120'::cidr").fetchone()[0]
IPv6Network('::ffff:102:300/120')
```

<a id="adapt-enum"></a>

## Enum adaptation

#### Versionadded
Added in version 3.1.

Psycopg can adapt Python [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) subclasses into PostgreSQL enum types
(created with the [`CREATE TYPE ... AS ENUM (...)`](https://www.postgresql.org/docs/current/static/datatype-enum.html) command).

In order to set up a bidirectional enum mapping, you should get information
about the PostgreSQL enum using the [`EnumInfo`](#psycopg.types.enum.EnumInfo) class and
register it using [`register_enum()`](#psycopg.types.enum.register_enum). The behaviour of unregistered
and registered enums is different.

- If the enum is not registered with `register_enum()`:
  - Pure `Enum` classes are dumped as normal strings, using their member
    names as value. The unknown oid is used, so PostgreSQL should be able to
    use this string in most contexts (such as an enum or a text field).

    #### Versionchanged
    Changed in version 3.1: In previous version dumping pure enums is not supported and raise a
    “cannot adapt” error.
  - Mix-in enums are dumped according to their mix-in type (because a `class
    MyIntEnum(int, Enum)` is more specifically an `int` than an `Enum`, so
    it’s dumped by default according to `int` rules).
  - PostgreSQL enums are loaded as Python strings. If you want to load arrays
    of such enums you will have to find their OIDs using [`types.TypeInfo.fetch()`](../api/types.md#psycopg.types.TypeInfo.fetch)
    and register them using [`register()`](../api/types.md#psycopg.types.TypeInfo.register).
- If the enum is registered (using [`EnumInfo`](#psycopg.types.enum.EnumInfo)`.fetch()` and
  [`register_enum()`](#psycopg.types.enum.register_enum)):
  - Enums classes, both pure and mixed-in, are dumped by name.
  - The registered PostgreSQL enum is loaded back as the registered Python
    enum members.

### *class* psycopg.types.enum.EnumInfo(name: [str](https://docs.python.org/3/library/stdtypes.html#str), oid: [int](https://docs.python.org/3/library/functions.html#int), array_oid: [int](https://docs.python.org/3/library/functions.html#int), labels: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[str](https://docs.python.org/3/library/stdtypes.html#str)])

Manage information about an enum type.

`EnumInfo` is a subclass of [`TypeInfo`](../api/types.md#psycopg.types.TypeInfo): refer to the
latter’s documentation for generic usage, especially the
[`fetch()`](../api/types.md#psycopg.types.TypeInfo.fetch) method.

#### labels

After [`fetch()`](../api/types.md#psycopg.types.TypeInfo.fetch), it contains the labels defined
in the PostgreSQL enum type.

#### enum

After [`register_enum()`](#psycopg.types.enum.register_enum) is called, it will contain the Python type
mapping to the registered enum.

### psycopg.types.enum.register_enum(info: [EnumInfo](#psycopg.types.enum.EnumInfo), context: [AdaptContext](../api/abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None, enum: [type](https://docs.python.org/3/library/functions.html#type)[E] | [None](https://docs.python.org/3/library/constants.html#None) = None, , mapping: [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[E, [str](https://docs.python.org/3/library/stdtypes.html#str)] | [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[E, [str](https://docs.python.org/3/library/stdtypes.html#str)]] | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Register the adapters to load and dump a enum type.

* **Parameters:**
  * **info** – The object with the information about the enum to register.
  * **context** – The context where to register the adapters. If `None`,
    register it globally.
  * **enum** – Python enum type matching to the PostgreSQL one. If `None`,
    a new enum will be generated and exposed as [`EnumInfo.enum`](#psycopg.types.enum.EnumInfo.enum).
  * **mapping** – Override the mapping between `enum` members and `info`
    labels.

After registering, fetching data of the registered enum will cast
PostgreSQL enum labels into corresponding Python enum members.

If no `enum` is specified, a new `Enum` is created based on
PostgreSQL enum labels.

Example:

```default
>>> from enum import Enum, auto
>>> from psycopg.types.enum import EnumInfo, register_enum

>>> class UserRole(Enum):
...     ADMIN = auto()
...     EDITOR = auto()
...     GUEST = auto()

>>> conn.execute("CREATE TYPE user_role AS ENUM ('ADMIN', 'EDITOR', 'GUEST')")

>>> info = EnumInfo.fetch(conn, "user_role")
>>> register_enum(info, conn, UserRole)

>>> some_editor = info.enum.EDITOR
>>> some_editor
<UserRole.EDITOR: 2>

>>> conn.execute(
...     "SELECT pg_typeof(%(editor)s), %(editor)s",
...     {"editor": some_editor}
... ).fetchone()
('user_role', <UserRole.EDITOR: 2>)

>>> conn.execute(
...     "SELECT ARRAY[%s, %s]",
...     [UserRole.ADMIN, UserRole.GUEST]
... ).fetchone()
[<UserRole.ADMIN: 1>, <UserRole.GUEST: 3>]
```

If the Python and the PostgreSQL enum don’t match 1:1 (for instance if members
have a different name, or if more than one Python enum should map to the same
PostgreSQL enum, or vice versa), you can specify the exceptions using the
`mapping` parameter.

`mapping` should be a dictionary with Python enum members as keys and the
matching PostgreSQL enum labels as values, or a list of `(member, label)`
pairs with the same meaning (useful when some members are repeated). Order
matters: if an element on either side is specified more than once, the last
pair in the sequence will take precedence:

```default
# Legacy roles, defined in medieval times.
>>> conn.execute(
...     "CREATE TYPE abbey_role AS ENUM ('ABBOT', 'SCRIBE', 'MONK', 'GUEST')")

>>> info = EnumInfo.fetch(conn, "abbey_role")
>>> register_enum(info, conn, UserRole, mapping=[
...     (UserRole.ADMIN, "ABBOT"),
...     (UserRole.EDITOR, "SCRIBE"),
...     (UserRole.EDITOR, "MONK")])

>>> conn.execute("SELECT '{ABBOT,SCRIBE,MONK,GUEST}'::abbey_role[]").fetchone()[0]
[<UserRole.ADMIN: 1>,
 <UserRole.EDITOR: 2>,
 <UserRole.EDITOR: 2>,
 <UserRole.GUEST: 3>]

>>> conn.execute("SELECT %s::text[]", [list(UserRole)]).fetchone()[0]
['ABBOT', 'MONK', 'GUEST']
```

A particularly useful case is when the PostgreSQL labels match the *values* of
a `str`-based Enum. In this case it is possible to use something like `{m:
m.value for m in enum}` as mapping:

```default
>>> class LowercaseRole(str, Enum):
...     ADMIN = "admin"
...     EDITOR = "editor"
...     GUEST = "guest"

>>> conn.execute(
...     "CREATE TYPE lowercase_role AS ENUM ('admin', 'editor', 'guest')")

>>> info = EnumInfo.fetch(conn, "lowercase_role")
>>> register_enum(
...     info, conn, LowercaseRole, mapping={m: m.value for m in LowercaseRole})

>>> conn.execute("SELECT 'editor'::lowercase_role").fetchone()[0]
<LowercaseRole.EDITOR: 'editor'>
```

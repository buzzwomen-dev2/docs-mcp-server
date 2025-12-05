# PostgreSQL specific model fields

All of these fields are available from the `django.contrib.postgres.fields`
module.

## Indexing these fields

[`Index`](../../models/indexes.md#django.db.models.Index) and [`Field.db_index`](../../models/fields.md#django.db.models.Field.db_index) both create a
B-tree index, which isn’t particularly helpful when querying complex data
types. Indexes such as [`GinIndex`](indexes.md#django.contrib.postgres.indexes.GinIndex) and
[`GistIndex`](indexes.md#django.contrib.postgres.indexes.GistIndex) are better suited, though
the index choice is dependent on the queries that you’re using. Generally, GiST
may be a good choice for the [range fields](#range-fields) and
[`HStoreField`](#django.contrib.postgres.fields.HStoreField), and GIN may be helpful for [`ArrayField`](#django.contrib.postgres.fields.ArrayField).

## `ArrayField`

### *class* ArrayField(base_field, size=None, \*\*options)

A field for storing lists of data. Most field types can be used, and you
pass another field instance as the [`base_field`](#django.contrib.postgres.fields.ArrayField.base_field). You may also specify a [`size`](#django.contrib.postgres.fields.ArrayField.size). `ArrayField` can be nested to store multi-dimensional
arrays.

If you give the field a [`default`](../../models/fields.md#django.db.models.Field.default), ensure
it’s a callable such as `list` (for an empty default) or a callable that
returns a list (such as a function). Incorrectly using `default=[]`
creates a mutable default that is shared between all instances of
`ArrayField`.

#### base_field

This is a required argument.

Specifies the underlying data type and behavior for the array. It
should be an instance of a subclass of
[`Field`](../../models/fields.md#django.db.models.Field). For example, it could be an
[`IntegerField`](../../models/fields.md#django.db.models.IntegerField) or a
[`CharField`](../../models/fields.md#django.db.models.CharField). Most field types are permitted,
with the exception of those handling relational data
([`ForeignKey`](../../models/fields.md#django.db.models.ForeignKey),
[`OneToOneField`](../../models/fields.md#django.db.models.OneToOneField) and
[`ManyToManyField`](../../models/fields.md#django.db.models.ManyToManyField)) and file fields
([`FileField`](../../models/fields.md#django.db.models.FileField) and
[`ImageField`](../../models/fields.md#django.db.models.ImageField)).

It is possible to nest array fields - you can specify an instance of
`ArrayField` as the `base_field`. For example:

```default
from django.contrib.postgres.fields import ArrayField
from django.db import models


class ChessBoard(models.Model):
    board = ArrayField(
        ArrayField(
            models.CharField(max_length=10, blank=True),
            size=8,
        ),
        size=8,
    )
```

Transformation of values between the database and the model, validation
of data and configuration, and serialization are all delegated to the
underlying base field.

#### size

This is an optional argument.

If passed, the array will have a maximum size as specified. This will
be passed to the database, although PostgreSQL at present does not
enforce the restriction.

#### NOTE
When nesting `ArrayField`, whether you use the `size` parameter or not,
PostgreSQL requires that the arrays are rectangular:

```default
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Board(models.Model):
    pieces = ArrayField(ArrayField(models.IntegerField()))


# Valid
Board(
    pieces=[
        [2, 3],
        [2, 1],
    ]
)

# Not valid
Board(
    pieces=[
        [2, 3],
        [2],
    ]
)
```

If irregular shapes are required, then the underlying field should be made
nullable and the values padded with `None`.

### Querying `ArrayField`

There are a number of custom lookups and transforms for [`ArrayField`](#django.contrib.postgres.fields.ArrayField).
We will use the following example model:

```default
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Post(models.Model):
    name = models.CharField(max_length=200)
    tags = ArrayField(models.CharField(max_length=200), blank=True)

    def __str__(self):
        return self.name
```

<a id="std-fieldlookup-arrayfield.contains"></a>

#### `contains`

The [`contains`](../../models/querysets.md#std-fieldlookup-contains) lookup is overridden on [`ArrayField`](#django.contrib.postgres.fields.ArrayField). The
returned objects will be those where the values passed are a subset of the
data. It uses the SQL operator `@>`. For example:

```pycon
>>> Post.objects.create(name="First post", tags=["thoughts", "django"])
>>> Post.objects.create(name="Second post", tags=["thoughts"])
>>> Post.objects.create(name="Third post", tags=["tutorial", "django"])

>>> Post.objects.filter(tags__contains=["thoughts"])
<QuerySet [<Post: First post>, <Post: Second post>]>

>>> Post.objects.filter(tags__contains=["django"])
<QuerySet [<Post: First post>, <Post: Third post>]>

>>> Post.objects.filter(tags__contains=["django", "thoughts"])
<QuerySet [<Post: First post>]>
```

<a id="std-fieldlookup-arrayfield.contained_by"></a>

#### `contained_by`

This is the inverse of the [`contains`](#std-fieldlookup-arrayfield.contains) lookup -
the objects returned will be those where the data is a subset of the values
passed. It uses the SQL operator `<@`. For example:

```pycon
>>> Post.objects.create(name="First post", tags=["thoughts", "django"])
>>> Post.objects.create(name="Second post", tags=["thoughts"])
>>> Post.objects.create(name="Third post", tags=["tutorial", "django"])

>>> Post.objects.filter(tags__contained_by=["thoughts", "django"])
<QuerySet [<Post: First post>, <Post: Second post>]>

>>> Post.objects.filter(tags__contained_by=["thoughts", "django", "tutorial"])
<QuerySet [<Post: First post>, <Post: Second post>, <Post: Third post>]>
```

<a id="std-fieldlookup-arrayfield.overlap"></a>

#### `overlap`

Returns objects where the data shares any results with the values passed. Uses
the SQL operator `&&`. For example:

```pycon
>>> Post.objects.create(name="First post", tags=["thoughts", "django"])
>>> Post.objects.create(name="Second post", tags=["thoughts", "tutorial"])
>>> Post.objects.create(name="Third post", tags=["tutorial", "django"])

>>> Post.objects.filter(tags__overlap=["thoughts"])
<QuerySet [<Post: First post>, <Post: Second post>]>

>>> Post.objects.filter(tags__overlap=["thoughts", "tutorial"])
<QuerySet [<Post: First post>, <Post: Second post>, <Post: Third post>]>

>>> Post.objects.filter(tags__overlap=Post.objects.values_list("tags"))
<QuerySet [<Post: First post>, <Post: Second post>, <Post: Third post>]>
```

<a id="std-fieldlookup-arrayfield.len"></a>

#### `len`

Returns the length of the array. The lookups available afterward are those
available for [`IntegerField`](../../models/fields.md#django.db.models.IntegerField). For example:

```pycon
>>> Post.objects.create(name="First post", tags=["thoughts", "django"])
>>> Post.objects.create(name="Second post", tags=["thoughts"])

>>> Post.objects.filter(tags__len=1)
<QuerySet [<Post: Second post>]>
```

<a id="std-fieldlookup-arrayfield.index"></a>

#### Index transforms

Index transforms index into the array. Any non-negative integer can be used.
There are no errors if it exceeds the [`size`](#django.contrib.postgres.fields.ArrayField.size) of the
array. The lookups available after the transform are those from the
[`base_field`](#django.contrib.postgres.fields.ArrayField.base_field). For example:

```pycon
>>> Post.objects.create(name="First post", tags=["thoughts", "django"])
>>> Post.objects.create(name="Second post", tags=["thoughts"])

>>> Post.objects.filter(tags__0="thoughts")
<QuerySet [<Post: First post>, <Post: Second post>]>

>>> Post.objects.filter(tags__1__iexact="Django")
<QuerySet [<Post: First post>]>

>>> Post.objects.filter(tags__276="javascript")
<QuerySet []>
```

#### NOTE
PostgreSQL uses 1-based indexing for array fields when writing raw SQL.
However these indexes and those used in [`slices`](#std-fieldlookup-arrayfield.slice)
use 0-based indexing to be consistent with Python.

<a id="std-fieldlookup-arrayfield.slice"></a>

#### Slice transforms

Slice transforms take a slice of the array. Any two non-negative integers can
be used, separated by a single underscore. The lookups available after the
transform do not change. For example:

```pycon
>>> Post.objects.create(name="First post", tags=["thoughts", "django"])
>>> Post.objects.create(name="Second post", tags=["thoughts"])
>>> Post.objects.create(name="Third post", tags=["django", "python", "thoughts"])

>>> Post.objects.filter(tags__0_1=["thoughts"])
<QuerySet [<Post: First post>, <Post: Second post>]>

>>> Post.objects.filter(tags__0_2__contains=["thoughts"])
<QuerySet [<Post: First post>, <Post: Second post>]>
```

#### NOTE
PostgreSQL uses 1-based indexing for array fields when writing raw SQL.
However these slices and those used in [`indexes`](#std-fieldlookup-arrayfield.index)
use 0-based indexing to be consistent with Python.

## `HStoreField`

### *class* HStoreField(\*\*options)

A field for storing key-value pairs. The Python data type used is a
`dict`. Keys must be strings, and values may be either strings or nulls
(`None` in Python).

To use this field, you’ll need to:

1. Add `'django.contrib.postgres'` in your [`INSTALLED_APPS`](../../settings.md#std-setting-INSTALLED_APPS).
2. [Set up the hstore extension](operations.md#create-postgresql-extensions) in
   PostgreSQL.

You’ll see an error like `can't adapt type 'dict'` if you skip the first
step, or `type "hstore" does not exist` if you skip the second.

#### NOTE
On occasions it may be useful to require or restrict the keys which are
valid for a given field. This can be done using the
[`KeysValidator`](validators.md#django.contrib.postgres.validators.KeysValidator).

### Querying `HStoreField`

In addition to the ability to query by key, there are a number of custom
lookups available for `HStoreField`.

We will use the following example model:

```default
from django.contrib.postgres.fields import HStoreField
from django.db import models


class Dog(models.Model):
    name = models.CharField(max_length=200)
    data = HStoreField()

    def __str__(self):
        return self.name
```

<a id="std-fieldlookup-hstorefield.key"></a>

#### Key lookups

To query based on a given key, you can use that key as the lookup name:

```pycon
>>> Dog.objects.create(name="Rufus", data={"breed": "labrador"})
>>> Dog.objects.create(name="Meg", data={"breed": "collie"})

>>> Dog.objects.filter(data__breed="collie")
<QuerySet [<Dog: Meg>]>
```

You can chain other lookups after key lookups:

```pycon
>>> Dog.objects.filter(data__breed__contains="l")
<QuerySet [<Dog: Rufus>, <Dog: Meg>]>
```

or use `F()` expressions to annotate a key value. For example:

```pycon
>>> from django.db.models import F
>>> rufus = Dog.objects.annotate(breed=F("data__breed"))[0]
>>> rufus.breed
'labrador'
```

If the key you wish to query by clashes with the name of another lookup, you
need to use the [`hstorefield.contains`](#std-fieldlookup-hstorefield.contains) lookup instead.

#### NOTE
Key transforms can also be chained with: [`contains`](../../models/querysets.md#std-fieldlookup-contains),
[`icontains`](../../models/querysets.md#std-fieldlookup-icontains), [`endswith`](../../models/querysets.md#std-fieldlookup-endswith), [`iendswith`](../../models/querysets.md#std-fieldlookup-iendswith),
[`iexact`](../../models/querysets.md#std-fieldlookup-iexact), [`regex`](../../models/querysets.md#std-fieldlookup-regex), [`iregex`](../../models/querysets.md#std-fieldlookup-iregex), [`startswith`](../../models/querysets.md#std-fieldlookup-startswith),
and [`istartswith`](../../models/querysets.md#std-fieldlookup-istartswith) lookups.

#### WARNING
Since any string could be a key in a hstore value, any lookup other than
those listed below will be interpreted as a key lookup. No errors are
raised. Be extra careful for typing mistakes, and always check your queries
work as you intend.

<a id="std-fieldlookup-hstorefield.contains"></a>

#### `contains`

The [`contains`](../../models/querysets.md#std-fieldlookup-contains) lookup is overridden on
[`HStoreField`](#django.contrib.postgres.fields.HStoreField). The returned objects are
those where the given `dict` of key-value pairs are all contained in the
field. It uses the SQL operator `@>`. For example:

```pycon
>>> Dog.objects.create(name="Rufus", data={"breed": "labrador", "owner": "Bob"})
>>> Dog.objects.create(name="Meg", data={"breed": "collie", "owner": "Bob"})
>>> Dog.objects.create(name="Fred", data={})

>>> Dog.objects.filter(data__contains={"owner": "Bob"})
<QuerySet [<Dog: Rufus>, <Dog: Meg>]>

>>> Dog.objects.filter(data__contains={"breed": "collie"})
<QuerySet [<Dog: Meg>]>
```

<a id="std-fieldlookup-hstorefield.contained_by"></a>

#### `contained_by`

This is the inverse of the [`contains`](#std-fieldlookup-hstorefield.contains) lookup -
the objects returned will be those where the key-value pairs on the object are
a subset of those in the value passed. It uses the SQL operator `<@`. For
example:

```pycon
>>> Dog.objects.create(name="Rufus", data={"breed": "labrador", "owner": "Bob"})
>>> Dog.objects.create(name="Meg", data={"breed": "collie", "owner": "Bob"})
>>> Dog.objects.create(name="Fred", data={})

>>> Dog.objects.filter(data__contained_by={"breed": "collie", "owner": "Bob"})
<QuerySet [<Dog: Meg>, <Dog: Fred>]>

>>> Dog.objects.filter(data__contained_by={"breed": "collie"})
<QuerySet [<Dog: Fred>]>
```

<a id="std-fieldlookup-hstorefield.has_key"></a>

#### `has_key`

Returns objects where the given key is in the data. Uses the SQL operator
`?`. For example:

```pycon
>>> Dog.objects.create(name="Rufus", data={"breed": "labrador"})
>>> Dog.objects.create(name="Meg", data={"breed": "collie", "owner": "Bob"})

>>> Dog.objects.filter(data__has_key="owner")
<QuerySet [<Dog: Meg>]>
```

<a id="std-fieldlookup-hstorefield.has_any_keys"></a>

#### `has_any_keys`

Returns objects where any of the given keys are in the data. Uses the SQL
operator `?|`. For example:

```pycon
>>> Dog.objects.create(name="Rufus", data={"breed": "labrador"})
>>> Dog.objects.create(name="Meg", data={"owner": "Bob"})
>>> Dog.objects.create(name="Fred", data={})

>>> Dog.objects.filter(data__has_any_keys=["owner", "breed"])
<QuerySet [<Dog: Rufus>, <Dog: Meg>]>
```

<a id="std-fieldlookup-hstorefield.has_keys"></a>

#### `has_keys`

Returns objects where all of the given keys are in the data. Uses the SQL
operator `?&`. For example:

```pycon
>>> Dog.objects.create(name="Rufus", data={})
>>> Dog.objects.create(name="Meg", data={"breed": "collie", "owner": "Bob"})

>>> Dog.objects.filter(data__has_keys=["breed", "owner"])
<QuerySet [<Dog: Meg>]>
```

<a id="std-fieldlookup-hstorefield.keys"></a>

#### `keys`

Returns objects where the array of keys is the given value. Note that the order
is not guaranteed to be reliable, so this transform is mainly useful for using
in conjunction with lookups on
[`ArrayField`](#django.contrib.postgres.fields.ArrayField). Uses the SQL function
`akeys()`. For example:

```pycon
>>> Dog.objects.create(name="Rufus", data={"toy": "bone"})
>>> Dog.objects.create(name="Meg", data={"breed": "collie", "owner": "Bob"})

>>> Dog.objects.filter(data__keys__overlap=["breed", "toy"])
<QuerySet [<Dog: Rufus>, <Dog: Meg>]>
```

<a id="std-fieldlookup-hstorefield.values"></a>

#### `values`

Returns objects where the array of values is the given value. Note that the
order is not guaranteed to be reliable, so this transform is mainly useful for
using in conjunction with lookups on
[`ArrayField`](#django.contrib.postgres.fields.ArrayField). Uses the SQL function
`avals()`. For example:

```pycon
>>> Dog.objects.create(name="Rufus", data={"breed": "labrador"})
>>> Dog.objects.create(name="Meg", data={"breed": "collie", "owner": "Bob"})

>>> Dog.objects.filter(data__values__contains=["collie"])
<QuerySet [<Dog: Meg>]>
```

<a id="range-fields"></a>

## Range Fields

There are five range field types, corresponding to the built-in range types in
PostgreSQL. These fields are used to store a range of values; for example the
start and end timestamps of an event, or the range of ages an activity is
suitable for.

All of the range fields translate to [psycopg Range objects](https://www.psycopg.org/psycopg3/docs/basic/pgtypes.html#adapt-range) in Python, but also accept tuples as input if no bounds
information is necessary. The default is lower bound included, upper bound
excluded, that is `[)` (see the PostgreSQL documentation for details about
[different bounds](https://www.postgresql.org/docs/current/rangetypes.html#RANGETYPES-IO)). The default bounds can be changed for non-discrete range
fields ([`DateTimeRangeField`](#django.contrib.postgres.fields.DateTimeRangeField) and [`DecimalRangeField`](#django.contrib.postgres.fields.DecimalRangeField)) by using
the `default_bounds` argument.

### `IntegerRangeField`

### *class* IntegerRangeField(\*\*options)

Stores a range of integers. Based on an
[`IntegerField`](../../models/fields.md#django.db.models.IntegerField). Represented by an `int4range` in
the database and a
`django.db.backends.postgresql.psycopg_any.NumericRange` in Python.

Regardless of the bounds specified when saving the data, PostgreSQL always
returns a range in a canonical form that includes the lower bound and
excludes the upper bound, that is `[)`.

### `BigIntegerRangeField`

### *class* BigIntegerRangeField(\*\*options)

Stores a range of large integers. Based on a
[`BigIntegerField`](../../models/fields.md#django.db.models.BigIntegerField). Represented by an `int8range`
in the database and a
`django.db.backends.postgresql.psycopg_any.NumericRange` in Python.

Regardless of the bounds specified when saving the data, PostgreSQL always
returns a range in a canonical form that includes the lower bound and
excludes the upper bound, that is `[)`.

### `DecimalRangeField`

### *class* DecimalRangeField(default_bounds='[)', \*\*options)

Stores a range of floating point values. Based on a
[`DecimalField`](../../models/fields.md#django.db.models.DecimalField). Represented by a `numrange` in
the database and a
`django.db.backends.postgresql.psycopg_any.NumericRange` in Python.

#### default_bounds

Optional. The value of `bounds` for list and tuple inputs. The
default is lower bound included, upper bound excluded, that is `[)`
(see the PostgreSQL documentation for details about
[different bounds](https://www.postgresql.org/docs/current/rangetypes.html#RANGETYPES-IO)). `default_bounds` is not used for
`django.db.backends.postgresql.psycopg_any.NumericRange` inputs.

### `DateTimeRangeField`

### *class* DateTimeRangeField(default_bounds='[)', \*\*options)

Stores a range of timestamps. Based on a
[`DateTimeField`](../../models/fields.md#django.db.models.DateTimeField). Represented by a `tstzrange` in
the database and a
`django.db.backends.postgresql.psycopg_any.DateTimeTZRange` in Python.

#### default_bounds

Optional. The value of `bounds` for list and tuple inputs. The
default is lower bound included, upper bound excluded, that is `[)`
(see the PostgreSQL documentation for details about
[different bounds](https://www.postgresql.org/docs/current/rangetypes.html#RANGETYPES-IO)). `default_bounds` is not used for
`django.db.backends.postgresql.psycopg_any.DateTimeTZRange` inputs.

### `DateRangeField`

### *class* DateRangeField(\*\*options)

Stores a range of dates. Based on a
[`DateField`](../../models/fields.md#django.db.models.DateField). Represented by a `daterange` in the
database and a `django.db.backends.postgresql.psycopg_any.DateRange` in
Python.

Regardless of the bounds specified when saving the data, PostgreSQL always
returns a range in a canonical form that includes the lower bound and
excludes the upper bound, that is `[)`.

### Querying Range Fields

There are a number of custom lookups and transforms for range fields. They are
available on all the above fields, but we will use the following example
model:

```default
from django.contrib.postgres.fields import IntegerRangeField
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=200)
    ages = IntegerRangeField()
    start = models.DateTimeField()

    def __str__(self):
        return self.name
```

We will also use the following example objects:

```pycon
>>> import datetime
>>> from django.utils import timezone
>>> now = timezone.now()
>>> Event.objects.create(name="Soft play", ages=(0, 10), start=now)
>>> Event.objects.create(
...     name="Pub trip", ages=(21, None), start=now - datetime.timedelta(days=1)
... )
```

and `NumericRange`:

```pycon
>>> from django.db.backends.postgresql.psycopg_any import NumericRange
```

#### Containment functions

As with other PostgreSQL fields, there are three standard containment
operators: `contains`, `contained_by` and `overlap`, using the SQL
operators `@>`, `<@`, and `&&` respectively.

<a id="std-fieldlookup-rangefield.contains"></a>

##### `contains`

```pycon
>>> Event.objects.filter(ages__contains=NumericRange(4, 5))
<QuerySet [<Event: Soft play>]>
```

<a id="std-fieldlookup-rangefield.contained_by"></a>

##### `contained_by`

```pycon
>>> Event.objects.filter(ages__contained_by=NumericRange(0, 15))
<QuerySet [<Event: Soft play>]>
```

The `contained_by` lookup is also available on the non-range field types:
[`SmallAutoField`](../../models/fields.md#django.db.models.SmallAutoField),
[`AutoField`](../../models/fields.md#django.db.models.AutoField), [`BigAutoField`](../../models/fields.md#django.db.models.BigAutoField),
[`SmallIntegerField`](../../models/fields.md#django.db.models.SmallIntegerField),
[`IntegerField`](../../models/fields.md#django.db.models.IntegerField),
[`BigIntegerField`](../../models/fields.md#django.db.models.BigIntegerField),
[`DecimalField`](../../models/fields.md#django.db.models.DecimalField), [`FloatField`](../../models/fields.md#django.db.models.FloatField),
[`DateField`](../../models/fields.md#django.db.models.DateField), and
[`DateTimeField`](../../models/fields.md#django.db.models.DateTimeField). For example:

```pycon
>>> from django.db.backends.postgresql.psycopg_any import DateTimeTZRange
>>> Event.objects.filter(
...     start__contained_by=DateTimeTZRange(
...         timezone.now() - datetime.timedelta(hours=1),
...         timezone.now() + datetime.timedelta(hours=1),
...     ),
... )
<QuerySet [<Event: Soft play>]>
```

<a id="std-fieldlookup-rangefield.overlap"></a>

##### `overlap`

```pycon
>>> Event.objects.filter(ages__overlap=NumericRange(8, 12))
<QuerySet [<Event: Soft play>]>
```

#### Comparison functions

Range fields support the standard lookups: [`lt`](../../models/querysets.md#std-fieldlookup-lt), [`gt`](../../models/querysets.md#std-fieldlookup-gt),
[`lte`](../../models/querysets.md#std-fieldlookup-lte) and [`gte`](../../models/querysets.md#std-fieldlookup-gte). These are not particularly helpful - they
compare the lower bounds first and then the upper bounds only if necessary.
This is also the strategy used to order by a range field. It is better to use
the specific range comparison operators.

<a id="std-fieldlookup-rangefield.fully_lt"></a>

##### `fully_lt`

The returned ranges are strictly less than the passed range. In other words,
all the points in the returned range are less than all those in the passed
range.

```pycon
>>> Event.objects.filter(ages__fully_lt=NumericRange(11, 15))
<QuerySet [<Event: Soft play>]>
```

<a id="std-fieldlookup-rangefield.fully_gt"></a>

##### `fully_gt`

The returned ranges are strictly greater than the passed range. In other words,
the all the points in the returned range are greater than all those in the
passed range.

```pycon
>>> Event.objects.filter(ages__fully_gt=NumericRange(11, 15))
<QuerySet [<Event: Pub trip>]>
```

<a id="std-fieldlookup-rangefield.not_lt"></a>

##### `not_lt`

The returned ranges do not contain any points less than the passed range, that
is the lower bound of the returned range is at least the lower bound of the
passed range.

```pycon
>>> Event.objects.filter(ages__not_lt=NumericRange(0, 15))
<QuerySet [<Event: Soft play>, <Event: Pub trip>]>
```

<a id="std-fieldlookup-rangefield.not_gt"></a>

##### `not_gt`

The returned ranges do not contain any points greater than the passed range,
that is the upper bound of the returned range is at most the upper bound of the
passed range.

```pycon
>>> Event.objects.filter(ages__not_gt=NumericRange(3, 10))
<QuerySet [<Event: Soft play>]>
```

<a id="std-fieldlookup-rangefield.adjacent_to"></a>

##### `adjacent_to`

The returned ranges share a bound with the passed range.

```pycon
>>> Event.objects.filter(ages__adjacent_to=NumericRange(10, 21))
<QuerySet [<Event: Soft play>, <Event: Pub trip>]>
```

#### Querying using the bounds

Range fields support several extra lookups.

<a id="std-fieldlookup-rangefield.startswith"></a>

##### `startswith`

Returned objects have the given lower bound. Can be chained to valid lookups
for the base field.

```pycon
>>> Event.objects.filter(ages__startswith=21)
<QuerySet [<Event: Pub trip>]>
```

<a id="std-fieldlookup-rangefield.endswith"></a>

##### `endswith`

Returned objects have the given upper bound. Can be chained to valid lookups
for the base field.

```pycon
>>> Event.objects.filter(ages__endswith=10)
<QuerySet [<Event: Soft play>]>
```

<a id="std-fieldlookup-rangefield.isempty"></a>

##### `isempty`

Returned objects are empty ranges. Can be chained to valid lookups for a
[`BooleanField`](../../models/fields.md#django.db.models.BooleanField).

```pycon
>>> Event.objects.filter(ages__isempty=True)
<QuerySet []>
```

<a id="std-fieldlookup-rangefield.lower_inc"></a>

##### `lower_inc`

Returns objects that have inclusive or exclusive lower bounds, depending on the
boolean value passed. Can be chained to valid lookups for a
[`BooleanField`](../../models/fields.md#django.db.models.BooleanField).

```pycon
>>> Event.objects.filter(ages__lower_inc=True)
<QuerySet [<Event: Soft play>, <Event: Pub trip>]>
```

<a id="std-fieldlookup-rangefield.lower_inf"></a>

##### `lower_inf`

Returns objects that have unbounded (infinite) or bounded lower bound,
depending on the boolean value passed. Can be chained to valid lookups for a
[`BooleanField`](../../models/fields.md#django.db.models.BooleanField).

```pycon
>>> Event.objects.filter(ages__lower_inf=True)
<QuerySet []>
```

<a id="std-fieldlookup-rangefield.upper_inc"></a>

##### `upper_inc`

Returns objects that have inclusive or exclusive upper bounds, depending on the
boolean value passed. Can be chained to valid lookups for a
[`BooleanField`](../../models/fields.md#django.db.models.BooleanField).

```pycon
>>> Event.objects.filter(ages__upper_inc=True)
<QuerySet []>
```

<a id="std-fieldlookup-rangefield.upper_inf"></a>

##### `upper_inf`

Returns objects that have unbounded (infinite) or bounded upper bound,
depending on the boolean value passed. Can be chained to valid lookups for a
[`BooleanField`](../../models/fields.md#django.db.models.BooleanField).

```pycon
>>> Event.objects.filter(ages__upper_inf=True)
<QuerySet [<Event: Pub trip>]>
```

### Defining your own range types

PostgreSQL allows the definition of custom range types. Django’s model and form
field implementations use base classes below, and `psycopg` provides a
[`register_range()`](https://www.psycopg.org/psycopg3/docs/basic/pgtypes.html#psycopg.types.range.register_range) to allow use of custom
range types.

### *class* RangeField(\*\*options)

Base class for model range fields.

#### base_field

The model field class to use.

#### range_type

The range type to use.

#### form_field

The form field class to use. Should be a subclass of
[`django.contrib.postgres.forms.BaseRangeField`](#django.contrib.postgres.fields.django.contrib.postgres.forms.BaseRangeField).

#### *class* django.contrib.postgres.forms.BaseRangeField

Base class for form range fields.

#### base_field

The form field to use.

#### range_type

The range type to use.

### Range operators

### *class* RangeOperators

PostgreSQL provides a set of SQL operators that can be used together with the
range data types (see [the PostgreSQL documentation for the full details of
range operators](https://www.postgresql.org/docs/current/functions-range.html#RANGE-OPERATORS-TABLE)). This class is meant as a
convenient method to avoid typos. The operator names overlap with the names of
corresponding lookups.

```python
class RangeOperators:
    EQUAL = "="
    NOT_EQUAL = "<>"
    CONTAINS = "@>"
    CONTAINED_BY = "<@"
    OVERLAPS = "&&"
    FULLY_LT = "<<"
    FULLY_GT = ">>"
    NOT_LT = "&>"
    NOT_GT = "&<"
    ADJACENT_TO = "-|-"
```

### RangeBoundary() expressions

### *class* RangeBoundary(inclusive_lower=True, inclusive_upper=False)

#### inclusive_lower

If `True` (default), the lower bound is inclusive `'['`, otherwise
it’s exclusive `'('`.

#### inclusive_upper

If `False` (default), the upper bound is exclusive `')'`, otherwise
it’s inclusive `']'`.

A `RangeBoundary()` expression represents the range boundaries. It can be
used with a custom range functions that expected boundaries, for example to
define [`ExclusionConstraint`](constraints.md#django.contrib.postgres.constraints.ExclusionConstraint). See
[the PostgreSQL documentation for the full details](https://www.postgresql.org/docs/current/rangetypes.html#RANGETYPES-INCLUSIVITY).

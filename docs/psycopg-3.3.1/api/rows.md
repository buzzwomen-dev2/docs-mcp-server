<a id="psycopg-rows"></a>

# `rows` – row factory implementations

The module exposes a few generic `RowFactory` implementation, which
can be used to retrieve data from the database in more complex structures than
the basic tuples.

Check out [Creating new row factories](../advanced/rows.md#row-factory-create) for information about how to use these objects.

### psycopg.rows.tuple_row(cursor: BaseCursor[Any, Any]) → [RowMaker](#psycopg.rows.RowMaker)[TupleRow]

Row factory to represent rows as simple tuples.

This is the default factory, used when [`connect()`](connections.md#psycopg.Connection.connect) or
[`cursor()`](connections.md#psycopg.Connection.cursor) are called without a `row_factory`
parameter.

Example:

```default
>>> cur = conn.cursor(row_factory=tuple_row)
>>> cur.execute("SELECT 10 AS foo, 'hello' AS bar").fetchone()
(10, 'hello')
```

### psycopg.rows.dict_row(cursor: BaseCursor[Any, Any]) → [RowMaker](#psycopg.rows.RowMaker)[DictRow]

Row factory to represent rows as dictionaries.

The dictionary keys are taken from the column names of the returned columns.

Example:

```default
>>> cur = conn.cursor(row_factory=dict_row)
>>> cur.execute("SELECT 10 AS foo, 'hello' AS bar").fetchone()
{'foo': 10, 'bar': 'hello'}
```

### psycopg.rows.namedtuple_row(cursor: BaseCursor[Any, Any]) → [RowMaker](#psycopg.rows.RowMaker)[NamedTuple]

Row factory to represent rows as [`namedtuple`](https://docs.python.org/3/library/collections.html#collections.namedtuple).

The field names are taken from the column names of the returned columns,
with some mangling to deal with invalid names.

Example:

```default
>>> cur = conn.cursor(row_factory=namedtuple_row)
>>> cur.execute("SELECT 10 AS foo, 'hello' AS bar").fetchone()
Row(foo=10, bar='hello')
```

### psycopg.rows.scalar_row(cursor: BaseCursor[Any, Any]) → [RowMaker](#psycopg.rows.RowMaker)[Any]

Generate a row factory returning the first column
as a scalar value.

Example:

```default
>>> cur = conn.cursor(row_factory=scalar_row)
>>> cur.execute("SELECT 10 AS foo, 'hello' AS bar").fetchone()
10
```

#### Versionadded
Added in version 3.2.

### psycopg.rows.class_row(cls: [type](https://docs.python.org/3/library/functions.html#type)[T]) → [BaseRowFactory](#psycopg.rows.BaseRowFactory)[T]

Generate a row factory to represent rows as instances of the class `cls`.

The class must support every output column name as a keyword parameter.

* **Parameters:**
  **cls** – The class to return for each row. It must support the fields
  returned by the query as keyword arguments.
* **Return type:**
  `Callable[[Cursor],` [`RowMaker`](#psycopg.rows.RowMaker)[~T]]

This is not a row factory, but rather a factory of row factories.
Specifying `row_factory=class_row(MyClass)` will create connections and
cursors returning `MyClass` objects on fetch.

Example:

```default
from dataclasses import dataclass
import psycopg
from psycopg.rows import class_row

@dataclass
class Person:
    first_name: str
    last_name: str
    age: int = None

conn = psycopg.connect()
cur = conn.cursor(row_factory=class_row(Person))

cur.execute("select 'John' as first_name, 'Smith' as last_name").fetchone()
# Person(first_name='John', last_name='Smith', age=None)
```

### psycopg.rows.args_row(func: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[...], T]) → [BaseRowFactory](#psycopg.rows.BaseRowFactory)[T]

Generate a row factory calling `func` with positional parameters for every row.

* **Parameters:**
  **func** – The function to call for each row. It must support the fields
  returned by the query as positional arguments.

### psycopg.rows.kwargs_row(func: [Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[...], T]) → [BaseRowFactory](#psycopg.rows.BaseRowFactory)[T]

Generate a row factory calling `func` with keyword parameters for every row.

* **Parameters:**
  **func** – The function to call for each row. It must support the fields
  returned by the query as keyword arguments.

## Formal rows protocols

These objects can be used to describe your own rows adapter for static typing
checks, such as [mypy](https://mypy.readthedocs.io/).

### *class* psycopg.rows.RowMaker

Callable protocol taking a sequence of value and returning an object.

The sequence of value is what is returned from a database query, already
adapted to the right Python types. The return value is the object that your
program would like to receive: by default ([`tuple_row()`](#psycopg.rows.tuple_row)) it is a simple
tuple, but it may be any type of object.

Typically, `RowMaker` functions are returned by [`RowFactory`](#psycopg.rows.RowFactory).

#### \_\_call_\_(values: Sequence[Any]) → Row

Convert a sequence of values from the database to a finished object.

### *class* psycopg.rows.RowFactory

Callable protocol taking a [`Cursor`](cursors.md#psycopg.Cursor) and returning a [`RowMaker`](#psycopg.rows.RowMaker).

A `RowFactory` is typically called when a `Cursor` receives a result.
This way it can inspect the cursor state (for instance the
[`description`](cursors.md#psycopg.Cursor.description) attribute) and help a `RowMaker` to create
a complete object.

For instance the [`dict_row()`](#psycopg.rows.dict_row) `RowFactory` uses the names of the column to
define the dictionary key and returns a `RowMaker` function which would
use the values to create a dictionary for each record.

#### \_\_call_\_(cursor: [Cursor](cursors.md#psycopg.Cursor)[Row]) → [RowMaker](#psycopg.rows.RowMaker)[Row]

Inspect the result on a cursor and return a [`RowMaker`](#psycopg.rows.RowMaker) to convert rows.

### *class* psycopg.rows.AsyncRowFactory

Like [`RowFactory`](#psycopg.rows.RowFactory), taking an async cursor as argument.

### *class* psycopg.rows.BaseRowFactory

Like [`RowFactory`](#psycopg.rows.RowFactory), taking either type of cursor as argument.

Note that it’s easy to implement an object implementing both `RowFactory` and
`AsyncRowFactory`: usually, everything you need to implement a row factory is
to access the cursor’s [`description`](cursors.md#psycopg.Cursor.description), which is provided by
both the cursor flavours.

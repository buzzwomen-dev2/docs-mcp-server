<a id="index-0"></a>

<a id="row-factories"></a>

# Row factories

Cursor’s `fetch*` methods, by default, return the records received from the
database as tuples. This can be changed to better suit the needs of the
programmer by using custom *row factories*.

The module [`psycopg.rows`](../api/rows.md#module-psycopg.rows) exposes several row factories ready to be used. For
instance, if you want to return your records as dictionaries, you can use
[`dict_row`](../api/rows.md#psycopg.rows.dict_row):

```default
>>> from psycopg.rows import dict_row

>>> conn = psycopg.connect(DSN, row_factory=dict_row)

>>> conn.execute("select 'John Doe' as name, 33 as age").fetchone()
{'name': 'John Doe', 'age': 33}
```

The `row_factory` parameter is supported by the [`connect()`](../api/connections.md#psycopg.Connection.connect)
method and the [`cursor()`](../api/connections.md#psycopg.Connection.cursor) method. Later usage of `row_factory`
overrides a previous one. It is also possible to change the
[`Connection.row_factory`](../api/connections.md#psycopg.Connection.row_factory) or [`Cursor.row_factory`](../api/cursors.md#psycopg.Cursor.row_factory) attributes to change what
they return:

```default
>>> cur = conn.cursor(row_factory=dict_row)
>>> cur.execute("select 'John Doe' as name, 33 as age").fetchone()
{'name': 'John Doe', 'age': 33}

>>> from psycopg.rows import namedtuple_row
>>> cur.row_factory = namedtuple_row
>>> cur.execute("select 'John Doe' as name, 33 as age").fetchone()
Row(name='John Doe', age=33)
```

If you want to return objects of your choice you can use a row factory
*generator*, for instance [`class_row`](../api/rows.md#psycopg.rows.class_row) or
[`args_row`](../api/rows.md#psycopg.rows.args_row), or you can [write your own row factory](#row-factory-create):

```default
>>> from dataclasses import dataclass

>>> @dataclass
... class Person:
...     name: str
...     age: int
...     weight: Optional[int] = None

>>> from psycopg.rows import class_row
>>> cur = conn.cursor(row_factory=class_row(Person))
>>> cur.execute("select 'John Doe' as name, 33 as age").fetchone()
Person(name='John Doe', age=33, weight=None)
```

#### NOTE
The choice of a `row_factory` in a `Connection` or a `Cursor`
constructor affects how the object is annotated for static type checking.

For instance, declaring a `row_factory=dict_row` will result in the
cursors’ `executeany()` annotated as returning `list[dict[str, Any]]`
instead of `list[tuple[Any, ...]]`.

Please check [Static Typing](typing.md#static-typing) for more details.

<a id="index-1"></a>

<a id="row-factory-create"></a>

## Creating new row factories

A *row factory* is a callable that accepts a [`Cursor`](../api/cursors.md#psycopg.Cursor) object and returns
another callable, a *row maker*, which takes raw data (as a sequence of
values) and returns the desired object.

The role of the row factory is to inspect a query result (it is called after a
query is executed and properties such as [`description`](../api/cursors.md#psycopg.Cursor.description) and
[`pgresult`](../api/cursors.md#psycopg.Cursor.pgresult) are available on the cursor) and to prepare a callable
which is efficient to call repeatedly (because, for instance, the names of the
columns are extracted, sanitised, and stored in local variables).

Formally, these objects are represented by the [`RowFactory`](../api/rows.md#psycopg.rows.RowFactory) and
[`RowMaker`](../api/rows.md#psycopg.rows.RowMaker) protocols.

`RowFactory` objects can be implemented as a class, for instance:

```python
from typing import Any, Sequence
from psycopg import Cursor

class DictRowFactory:
    def __init__(self, cursor: Cursor[Any]):
        self.fields = [c.name for c in cursor.description]

    def __call__(self, values: Sequence[Any]) -> dict[str, Any]:
        return dict(zip(self.fields, values))
```

or as nested functions:

```python
def dict_row_factory(cursor: Cursor[Any]) -> RowMaker[dict[str, Any]]:
    fields = [c.name for c in cursor.description]

    def make_row(values: Sequence[Any]) -> dict[str, Any]:
        return dict(zip(fields, values))

    return make_row
```

These can then be used by specifying a `row_factory` argument in
[`Connection.connect()`](../api/connections.md#psycopg.Connection.connect), [`Connection.cursor()`](../api/connections.md#psycopg.Connection.cursor), or by setting the
[`Connection.row_factory`](../api/connections.md#psycopg.Connection.row_factory) attribute.

```python
conn = psycopg.connect(row_factory=DictRowFactory)
cur = conn.execute("SELECT first_name, last_name, age FROM persons")
person = cur.fetchone()
print(f"{person['first_name']} {person['last_name']}")
```

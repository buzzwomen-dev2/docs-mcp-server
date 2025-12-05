# `sql` – SQL string composition

<a id="index-0"></a>

<a id="module-psycopg.sql"></a>

The module contains objects and functions useful to generate SQL dynamically,
in a convenient and safe way. SQL identifiers (e.g. names of tables and
fields) cannot be passed to the [`execute()`](cursors.md#psycopg.Cursor.execute) method like query
arguments:

```default
# This will not work
table_name = 'my_table'
cur.execute("INSERT INTO %s VALUES (%s, %s)", [table_name, 10, 20])
```

The SQL query should be composed before the arguments are merged, for
instance:

```default
# This works, but it is not optimal
table_name = 'my_table'
cur.execute(
    "INSERT INTO %s VALUES (%%s, %%s)" % table_name,
    [10, 20])
```

This sort of works, but it is an accident waiting to happen: the table name
may be an invalid SQL literal and need quoting; even more serious is the
security problem in case the table name comes from an untrusted source. The
name should be escaped using `escape_identifier()`:

```default
from psycopg.pq import Escaping

# This works, but it is not optimal
table_name = 'my_table'
cur.execute(
    "INSERT INTO %s VALUES (%%s, %%s)" % Escaping.escape_identifier(table_name),
    [10, 20])
```

This is now safe, but it somewhat ad-hoc. In case, for some reason, it is
necessary to include a value in the query string (as opposite as in a value)
the merging rule is still different. It is also still relatively dangerous: if
`escape_identifier()` is forgotten somewhere, the program will usually work,
but will eventually crash in the presence of a table or field name with
containing characters to escape, or will present a potentially exploitable
weakness.

The objects exposed by the `psycopg.sql` module allow generating SQL
statements on the fly, separating clearly the variable parts of the statement
from the query parameters:

```default
from psycopg import sql

cur.execute(
    sql.SQL("INSERT INTO {} VALUES (%s, %s)")
        .format(sql.Identifier('my_table')),
    [10, 20])
```

## Module usage

Usually you should express the template of your query as an [`SQL`](#psycopg.sql.SQL) instance
with `{}`-style placeholders and use [`format()`](#psycopg.sql.SQL.format) to merge the variable
parts into them, all of which must be [`Composable`](#psycopg.sql.Composable) subclasses. You can still
have `%s`-style placeholders in your query and pass values to
[`execute()`](cursors.md#psycopg.Cursor.execute): such value placeholders will be untouched by
`format()`:

```default
query = sql.SQL("SELECT {field} FROM {table} WHERE {pkey} = %s").format(
    field=sql.Identifier('my_name'),
    table=sql.Identifier('some_table'),
    pkey=sql.Identifier('id'))
```

The resulting object is meant to be passed directly to cursor methods such as
[`execute()`](cursors.md#psycopg.Cursor.execute), [`executemany()`](cursors.md#psycopg.Cursor.executemany),
[`copy()`](cursors.md#psycopg.Cursor.copy), but can also be used to compose a query as a Python
string, using the [`as_string()`](#psycopg.sql.Composable.as_string) method:

```default
cur.execute(query, (42,))
full_query = query.as_string(cur)
```

If part of your query is a variable sequence of arguments, such as a
comma-separated list of field names, you can use the [`SQL.join()`](#psycopg.sql.SQL.join) method to
pass them to the query:

```default
query = sql.SQL("SELECT {fields} FROM {table}").format(
    fields=sql.SQL(',').join([
        sql.Identifier('field1'),
        sql.Identifier('field2'),
        sql.Identifier('field3'),
    ]),
    table=sql.Identifier('some_table'))
```

## `sql` objects

The `sql` objects are in the following inheritance hierarchy:

[`Composable`](#psycopg.sql.Composable): the base class exposing the common interface
<br/>
`|__` [`SQL`](#psycopg.sql.SQL): a literal snippet of an SQL query
<br/>
`|__` [`Identifier`](#psycopg.sql.Identifier): a PostgreSQL identifier or dot-separated sequence of identifiers
<br/>
`|__` [`Literal`](#psycopg.sql.Literal): a value hardcoded into a query
<br/>
`|__` [`Placeholder`](#psycopg.sql.Placeholder): a `%s`-style placeholder whose value will be added later e.g. by [`execute()`](cursors.md#psycopg.Cursor.execute)
<br/>
`|__` [`Composed`](#psycopg.sql.Composed): a sequence of `Composable` instances.
<br/>

### *class* psycopg.sql.Composable

Abstract base class for objects that can be used to compose an SQL string.

`Composable` objects can be joined using the `+` operator: the result
will be a [`Composed`](#psycopg.sql.Composed) instance containing the objects joined. The operator
`*` is also supported with an integer argument: the result is a
`Composed` instance containing the left argument repeated as many times as
requested.

`SQL` and `Composed` objects can be passed directly to
[`execute()`](cursors.md#psycopg.Cursor.execute), [`executemany()`](cursors.md#psycopg.Cursor.executemany),
[`copy()`](cursors.md#psycopg.Cursor.copy) in place of the query string.

#### as_string(context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [str](https://docs.python.org/3/library/stdtypes.html#str)

Return the value of the object as string.

* **Parameters:**
  **context** ([`connection`](https://www.psycopg.org/docs/connection.html#connection) or [`cursor`](https://www.psycopg.org/docs/cursor.html#cursor)) – the context to evaluate the string into.

#### Versionchanged
Changed in version 3.2: The `context` parameter is optional.

#### WARNING
If a context is not specified, the results are “generic” and not
tailored for a specific target connection. Details such as the
connection encoding and escaping style will not be taken into
account.

#### *abstractmethod* as_bytes(context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)

Return the value of the object as bytes.

* **Parameters:**
  **context** ([`connection`](https://www.psycopg.org/docs/connection.html#connection) or [`cursor`](https://www.psycopg.org/docs/cursor.html#cursor)) – the context to evaluate the object into.

The method is automatically invoked by [`execute()`](cursors.md#psycopg.Cursor.execute),
[`executemany()`](cursors.md#psycopg.Cursor.executemany), [`copy()`](cursors.md#psycopg.Cursor.copy) if a
`Composable` is passed instead of the query string.

#### Versionchanged
Changed in version 3.2: The `context` parameter is optional. See [`as_string`](#psycopg.sql.as_string) for details.

### *class* psycopg.sql.SQL(obj: [LiteralString](https://docs.python.org/3/library/typing.html#typing.LiteralString))

A [`Composable`](#psycopg.sql.Composable) representing a snippet of SQL statement.

`SQL` exposes [`join()`](#psycopg.sql.SQL.join) and [`format()`](#psycopg.sql.SQL.format) methods useful to create a template
where to merge variable parts of a query (for instance field or table
names).

The `obj` string doesn’t undergo any form of escaping, so it is not
suitable to represent variable identifiers or values: you should only use
it to pass constant strings representing templates or snippets of SQL
statements; use other objects such as [`Identifier`](#psycopg.sql.Identifier) or [`Literal`](#psycopg.sql.Literal) to
represent variable parts.

`SQL` objects can be passed directly to [`execute()`](cursors.md#psycopg.Cursor.execute),
[`executemany()`](cursors.md#psycopg.Cursor.executemany), [`copy()`](cursors.md#psycopg.Cursor.copy) in place of the
query string.

Example:

```default
>>> query = sql.SQL("SELECT {0} FROM {1}").format(
...    sql.SQL(', ').join([sql.Identifier('foo'), sql.Identifier('bar')]),
...    sql.Identifier('table'))
>>> print(query.as_string(conn))
SELECT "foo", "bar" FROM "table"
```

#### Versionchanged
Changed in version 3.1: The input object should be a [`LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString). See [**PEP 675**](https://peps.python.org/pep-0675/)
for details.

#### format(\*args: [Any](https://docs.python.org/3/library/typing.html#typing.Any), \*\*kwargs: [Any](https://docs.python.org/3/library/typing.html#typing.Any)) → [Composed](#psycopg.sql.Composed)

Merge [`Composable`](#psycopg.sql.Composable) objects into a template.

* **Parameters:**
  * **args** – parameters to replace to numbered (`{0}`, `{1}`) or
    auto-numbered (`{}`) placeholders
  * **kwargs** – parameters to replace to named (`{name}`) placeholders
* **Returns:**
  the union of the `SQL` string with placeholders replaced
* **Return type:**
  [`Composed`](#psycopg.sql.Composed)

The method is similar to the Python `str.format()` method: the string
template supports auto-numbered (`{}`), numbered (`{0}`,
`{1}`…), and named placeholders (`{name}`), with positional
arguments replacing the numbered placeholders and keywords replacing
the named ones. However placeholder modifiers (`{0!r}`, `{0:<10}`)
are not supported.

If a `Composable` objects is passed to the template it will be merged
according to its [`as_string()`](#psycopg.sql.as_string) method. If any other Python object is
passed, it will be wrapped in a [`Literal`](#psycopg.sql.Literal) object and so escaped
according to SQL rules.

Example:

```default
>>> print(sql.SQL("SELECT * FROM {} WHERE {} = %s")
...     .format(sql.Identifier('people'), sql.Identifier('id'))
...     .as_string(conn))
SELECT * FROM "people" WHERE "id" = %s

>>> print(sql.SQL("SELECT * FROM {tbl} WHERE name = {name}")
...     .format(tbl=sql.Identifier('people'), name="O'Rourke"))
...     .as_string(conn))
SELECT * FROM "people" WHERE name = 'O''Rourke'
```

#### join(seq: [Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[Template]) → Template

#### join(seq: [Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)]) → [Composed](#psycopg.sql.Composed)

Join a sequence of [`Composable`](#psycopg.sql.Composable).

* **Parameters:**
  **seq** – the elements to join.

Use the `SQL` object’s string to separate the elements in `seq`.
Elements that are not [`Composable`](#psycopg.sql.Composable) will be considered [`Literal`](#psycopg.sql.Literal).

If the arguments are `Template` instance, return a `Template` joining
all the items. Note that arguments must either be all templates or
none should be.

Note that [`Composed`](#psycopg.sql.Composed) objects are iterable too, so they can be used as
argument for this method.

Example:

```default
>>> snip = sql.SQL(', ').join(
...     sql.Identifier(n) for n in ['foo', 'bar', 'baz'])
>>> print(snip.as_string(conn))
"foo", "bar", "baz"
```

#### Versionchanged
Changed in version 3.3: Added support for [`Template`](https://docs.python.org/3/library/string.templatelib.html#string.templatelib.Template) sequences.
See [nested template strings](../basic/tstrings.md#tstring-template-nested).

### *class* psycopg.sql.Identifier(\*strings: [str](https://docs.python.org/3/library/stdtypes.html#str))

A [`Composable`](#psycopg.sql.Composable) representing an SQL identifier or a dot-separated sequence.

Identifiers usually represent names of database objects, such as tables or
fields. PostgreSQL identifiers follow [different rules](https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS) than SQL string
literals for escaping (e.g. they use double quotes instead of single).

Example:

```default
>>> t1 = sql.Identifier("foo")
>>> t2 = sql.Identifier("ba'r")
>>> t3 = sql.Identifier('ba"z')
>>> print(sql.SQL(', ').join([t1, t2, t3]).as_string(conn))
"foo", "ba'r", "ba""z"
```

Multiple strings can be passed to the object to represent a qualified name,
i.e. a dot-separated sequence of identifiers.

Example:

```default
>>> query = sql.SQL("SELECT {} FROM {}").format(
...     sql.Identifier("table", "field"),
...     sql.Identifier("schema", "table"))
>>> print(query.as_string(conn))
SELECT "table"."field" FROM "schema"."table"
```

### *class* psycopg.sql.Literal(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any))

A [`Composable`](#psycopg.sql.Composable) representing an SQL value to include in a query.

Usually you will want to include placeholders in the query and pass values
as `execute()` arguments. If however you really really need to
include a literal value in the query you can use this object.

The string returned by `as_string()` follows the normal [adaptation
rules](../basic/adapt.md#types-adaptation) for Python objects.

Example:

```default
>>> s1 = sql.Literal("fo'o")
>>> s2 = sql.Literal(42)
>>> s3 = sql.Literal(date(2000, 1, 1))
>>> print(sql.SQL(', ').join([s1, s2, s3]).as_string(conn))
'fo''o', 42, '2000-01-01'::date
```

#### Versionchanged
Changed in version 3.1: Add a type cast to the representation if useful in ambiguous context
(e.g. `'2000-01-01'::date`)

### *class* psycopg.sql.Placeholder(name: [str](https://docs.python.org/3/library/stdtypes.html#str) = '', format: [str](https://docs.python.org/3/library/stdtypes.html#str) | [PyFormat](adapt.md#psycopg.adapt.PyFormat) = PyFormat.AUTO)

A [`Composable`](#psycopg.sql.Composable) representing a placeholder for query parameters.

If the name is specified, generate a named placeholder (e.g. `%(name)s`,
`%(name)b`), otherwise generate a positional placeholder (e.g. `%s`,
`%b`).

The object is useful to generate SQL queries with a variable number of
arguments.

Examples:

```default
>>> names = ['foo', 'bar', 'baz']

>>> q1 = sql.SQL("INSERT INTO my_table ({}) VALUES ({})").format(
...     sql.SQL(', ').join(map(sql.Identifier, names)),
...     sql.SQL(', ').join(sql.Placeholder() * len(names)))
>>> print(q1.as_string(conn))
INSERT INTO my_table ("foo", "bar", "baz") VALUES (%s, %s, %s)

>>> q2 = sql.SQL("INSERT INTO my_table ({}) VALUES ({})").format(
...     sql.SQL(', ').join(map(sql.Identifier, names)),
...     sql.SQL(', ').join(map(sql.Placeholder, names)))
>>> print(q2.as_string(conn))
INSERT INTO my_table ("foo", "bar", "baz") VALUES (%(foo)s, %(bar)s, %(baz)s)
```

### *class* psycopg.sql.Composed(seq: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)])

A [`Composable`](#psycopg.sql.Composable) object made of a sequence of `Composable`.

The object is usually created using `Composable` operators and methods
(such as the [`SQL.format()`](#psycopg.sql.SQL.format) method). `Composed` objects can be passed
directly to [`execute()`](cursors.md#psycopg.Cursor.execute), [`executemany()`](cursors.md#psycopg.Cursor.executemany),
[`copy()`](cursors.md#psycopg.Cursor.copy) in place of the query string.

It is also possible to create a `Composed` directly specifying a sequence
of objects as arguments: if they are not `Composable` they will be wrapped
in a [`Literal`](#psycopg.sql.Literal).

Example:

```default
>>> comp = sql.Composed(
...     [sql.SQL("INSERT INTO "), sql.Identifier("table")])
>>> print(comp.as_string(conn))
INSERT INTO "table"
```

`Composed` objects are iterable (so they can be used in [`SQL.join`](#psycopg.sql.SQL.join) for
instance).

#### join(joiner: [SQL](#psycopg.sql.SQL) | [LiteralString](https://docs.python.org/3/library/typing.html#typing.LiteralString)) → [Composed](#psycopg.sql.Composed)

Return a new `Composed` interposing the `joiner` with the `Composed` items.

The `joiner` must be a [`SQL`](#psycopg.sql.SQL) or a string which will be interpreted as
an [`SQL`](#psycopg.sql.SQL).

Example:

```default
>>> fields = sql.Identifier('foo') + sql.Identifier('bar')  # a Composed
>>> print(fields.join(', ').as_string(conn))
"foo", "bar"
```

## Utility functions

### psycopg.sql.as_string(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any), context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [str](https://docs.python.org/3/library/stdtypes.html#str)

Convert an object to a string according to SQL rules.

* **Parameters:**
  * **obj** – the object to convert
  * **context** ([`AdaptContext`](abc.md#psycopg.abc.AdaptContext) | `None`) – the context in which to convert the object

Adaptation happens according to the type of `obj`:

- [`Composable`](#psycopg.sql.Composable) objects are converted according to their
  [`as_string()`](#psycopg.sql.Composable.as_string) method;
- [`Template`](https://docs.python.org/3/library/string.templatelib.html#string.templatelib.Template) strings are converted according to the
  rules documented in [Template string queries](../basic/tstrings.md#template-strings);
- every other object is converted as it was [a parameter passed to a
  query](../basic/adapt.md#types-adaptation).

If `context` is specified then it is be used to customize the conversion.
for example using the encoding of a connection or the dumpers registered.

#### Versionadded
Added in version 3.3.

### psycopg.sql.as_bytes(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any), context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)

Convert an object to a bytes string according to SQL rules.

* **Parameters:**
  * **obj** – the object to convert
  * **context** ([`AdaptContext`](abc.md#psycopg.abc.AdaptContext) | `None`) – the context in which to convert the object

See [`as_string()`](#psycopg.sql.as_string) for details.

#### Versionadded
Added in version 3.3.

### psycopg.sql.NULL

### psycopg.sql.DEFAULT

`sql.SQL` objects often useful in queries.

### psycopg.sql.quote(obj: [Any](https://docs.python.org/3/library/typing.html#typing.Any), context: [AdaptContext](abc.md#psycopg.abc.AdaptContext) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [str](https://docs.python.org/3/library/stdtypes.html#str)

Adapt a Python object to a quoted SQL string.

Use this function only if you absolutely want to convert a Python string to
an SQL quoted literal to use e.g. to generate batch SQL and you won’t have
a connection available when you will need to use it.

This function is relatively inefficient, because it doesn’t cache the
adaptation rules. If you pass a `context` you can adapt the adaptation
rules used, otherwise only global rules are used.

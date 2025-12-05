# COPY-related objects

The main objects ([`Copy`](#psycopg.Copy), [`AsyncCopy`](#psycopg.AsyncCopy)) present the main interface to exchange
data during a COPY operations. These objects are normally obtained by the
methods [`Cursor.copy()`](cursors.md#psycopg.Cursor.copy) and [`AsyncCursor.copy()`](cursors.md#psycopg.AsyncCursor.copy); however, they can be also
created directly, for instance to write to a destination which is not a
database (e.g. using a [`FileWriter`](#psycopg.copy.FileWriter)).

See [Using COPY TO and COPY FROM](../basic/copy.md#copy) for details.

## Main Copy objects

### *class* psycopg.Copy

Manage an asynchronous `COPY` operation.

* **Parameters:**
  * **cursor** – the cursor where the operation is performed.
  * **binary** – if `True`, write binary format.
  * **writer** – the object to write to destination. If not specified, write
    to the `cursor` connection.

Choosing `binary` is not necessary if the cursor has executed a
`COPY` operation, because the operation result describes the format
too. The parameter is useful when a `Copy` object is created manually and
no operation is performed on the cursor, such as when using `writer=`[`FileWriter`](#psycopg.copy.FileWriter).

The object is normally returned by `with` [`Cursor.copy()`](cursors.md#psycopg.Cursor.copy).

#### write_row(row: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)]) → [None](https://docs.python.org/3/library/constants.html#None)

Write a record to a table after a `COPY FROM` operation.

The data in the tuple will be converted as configured on the cursor;
see [Data adaptation configuration](../advanced/adapt.md#adaptation) for details.

#### write(buffer: Buffer | [str](https://docs.python.org/3/library/stdtypes.html#str)) → [None](https://docs.python.org/3/library/constants.html#None)

Write a block of data to a table after a `COPY FROM` operation.

If the `COPY` is in binary format `buffer` must be `bytes`. In
text mode it can be either `bytes` or `str`.

#### read() → Buffer

Read an unparsed row after a `COPY TO` operation.

Return an empty string when the data is finished.

Instead of using `read()` you can iterate on the `Copy` object to
read its data row by row, using `for row in copy: ...`.

#### rows() → [Iterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[Any](https://docs.python.org/3/library/typing.html#typing.Any), ...]]

Iterate on the result of a `COPY TO` operation record by record.

Note that the records returned will be tuples of unparsed strings or
bytes, unless data types are specified using [`set_types()`](#psycopg.Copy.set_types).

Equivalent of iterating on [`read_row()`](#psycopg.Copy.read_row) until it returns `None`

#### read_row() → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[Any](https://docs.python.org/3/library/typing.html#typing.Any), ...] | [None](https://docs.python.org/3/library/constants.html#None)

Read a parsed row of data from a table after a `COPY TO` operation.

Return `None` when the data is finished.

Note that the records returned will be tuples of unparsed strings or
bytes, unless data types are specified using [`set_types()`](#psycopg.Copy.set_types).

#### set_types(types: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[int](https://docs.python.org/3/library/functions.html#int) | [str](https://docs.python.org/3/library/stdtypes.html#str)]) → [None](https://docs.python.org/3/library/constants.html#None)

Set the types expected in a COPY operation.

The types must be specified as a sequence of oid or PostgreSQL type
names (e.g. `int4`, `timestamptz[]`).

This operation overcomes the lack of metadata returned by PostgreSQL
when a COPY operation begins:

- On `COPY TO`, `set_types()` allows to specify what types the
  operation returns. If `set_types()` is not used, the data will be
  returned as unparsed strings or bytes instead of Python objects.
- On `COPY FROM`, `set_types()` allows to choose what type the
  database expects. This is especially useful in binary copy, because
  PostgreSQL will apply no cast rule.

### *class* psycopg.AsyncCopy

Manage an asynchronous `COPY` operation.

* **Parameters:**
  * **cursor** – the cursor where the operation is performed.
  * **binary** – if `True`, write binary format.
  * **writer** – the object to write to destination. If not specified, write
    to the `cursor` connection.

Choosing `binary` is not necessary if the cursor has executed a
`COPY` operation, because the operation result describes the format
too. The parameter is useful when a `Copy` object is created manually and
no operation is performed on the cursor, such as when using `writer=`[`FileWriter`](#psycopg.copy.FileWriter).

The object is normally returned by `async with` [`AsyncCursor.copy()`](cursors.md#psycopg.AsyncCursor.copy).
Its methods are similar to the ones of the [`Copy`](#psycopg.Copy) object but offering an
[`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio) interface (`await`, `async for`, `async with`).

#### *async* write_row(row: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)]) → [None](https://docs.python.org/3/library/constants.html#None)

Write a record to a table after a `COPY FROM` operation.

#### *async* write(buffer: Buffer | [str](https://docs.python.org/3/library/stdtypes.html#str)) → [None](https://docs.python.org/3/library/constants.html#None)

Write a block of data to a table after a `COPY FROM` operation.

If the `COPY` is in binary format `buffer` must be `bytes`. In
text mode it can be either `bytes` or `str`.

#### *async* read() → Buffer

Read an unparsed row after a `COPY TO` operation.

Return an empty string when the data is finished.

Instead of using `read()` you can iterate on the `AsyncCopy` object
to read its data row by row, using `async for row in copy: ...`.

#### *async* rows() → [AsyncIterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator)[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[Any](https://docs.python.org/3/library/typing.html#typing.Any), ...]]

Iterate on the result of a `COPY TO` operation record by record.

Note that the records returned will be tuples of unparsed strings or
bytes, unless data types are specified using `set_types()`.

Use it as `async for record in copy.rows():` …

#### *async* read_row() → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[Any](https://docs.python.org/3/library/typing.html#typing.Any), ...] | [None](https://docs.python.org/3/library/constants.html#None)

Read a parsed row of data from a table after a `COPY TO` operation.

Return `None` when the data is finished.

Note that the records returned will be tuples of unparsed strings or
bytes, unless data types are specified using `set_types()`.

<a id="copy-writers"></a>

## Writer objects

#### Versionadded
Added in version 3.1.

Copy writers are helper objects to specify where to write COPY-formatted data.
By default, data is written to the database (using the [`LibpqWriter`](#psycopg.copy.LibpqWriter)). It is
possible to write copy-data for offline use by using a [`FileWriter`](#psycopg.copy.FileWriter), or to
customize further writing by implementing your own [`Writer`](#psycopg.copy.Writer) or [`AsyncWriter`](#psycopg.copy.AsyncWriter)
subclass.

Writers instances can be used passing them to the cursor
[`copy()`](cursors.md#psycopg.Cursor.copy) method or to the [`Copy`](#psycopg.Copy) constructor, as the
`writer` argument.

### *class* psycopg.copy.Writer

A class to write copy data somewhere (for async connections).

This is an abstract base class: subclasses are required to implement their
[`write()`](#psycopg.copy.Writer.write) method.

#### *abstractmethod* write(data: Buffer) → [None](https://docs.python.org/3/library/constants.html#None)

Write some data to destination.

#### finish(exc: [BaseException](https://docs.python.org/3/library/exceptions.html#BaseException) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Called when write operations are finished.

If operations finished with an error, it will be passed to `exc`.

### *class* psycopg.copy.LibpqWriter(cursor: [Cursor](cursors.md#psycopg.Cursor)[Any])

An [`Writer`](#psycopg.copy.Writer) to write copy data to a Postgres database.

This is the writer used by default if none is specified.

### *class* psycopg.copy.FileWriter(file: [IO](https://docs.python.org/3/library/typing.html#typing.IO)[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes)])

A [`Writer`](#psycopg.copy.Writer) to write copy data to a file-like object.

* **Parameters:**
  **file** – the file where to write copy data. It must be open for writing
  in binary mode.

This writer should be used without executing a `COPY` operation on
the database. For example, if `records` is a list of tuples containing
data to save in COPY format to a file (e.g. for later import), it can be
used as:

```python
with open("target-file.pgcopy", "wb") as f:
    with Copy(cur, writer=FileWriter(f)) as copy:
        for record in records
            copy.write_row(record)
```

### *class* psycopg.copy.AsyncWriter

A class to write copy data somewhere (for async connections).

This class methods have the same semantics of the ones of [`Writer`](#psycopg.copy.Writer), but
offer an async interface.

#### *abstractmethod async* write(data: Buffer) → [None](https://docs.python.org/3/library/constants.html#None)

Write some data to destination.

#### *async* finish(exc: [BaseException](https://docs.python.org/3/library/exceptions.html#BaseException) | [None](https://docs.python.org/3/library/constants.html#None) = None) → [None](https://docs.python.org/3/library/constants.html#None)

Called when write operations are finished.

If operations finished with an error, it will be passed to `exc`.

### *class* psycopg.copy.AsyncLibpqWriter(cursor: [AsyncCursor](cursors.md#psycopg.AsyncCursor)[Any])

An [`AsyncWriter`](#psycopg.copy.AsyncWriter) to write copy data to a Postgres database.

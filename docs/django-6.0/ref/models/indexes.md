# Model index reference

Index classes ease creating database indexes. They can be added using the
[`Meta.indexes`](options.md#django.db.models.Options.indexes) option. This document
explains the API references of [`Index`](#django.db.models.Index) which includes the [index
options]().

## `Index` options

### *class* Index(\*expressions, fields=(), name=None, db_tablespace=None, opclasses=(), condition=None, include=None)

Creates an index (B-Tree) in the database.

### `expressions`

#### Index.expressions

Positional argument `*expressions` allows creating functional indexes on
expressions and database functions.

For example:

```default
Index(Lower("title").desc(), "pub_date", name="lower_title_date_idx")
```

creates an index on the lowercased value of the `title` field in descending
order and the `pub_date` field in the default ascending order.

Another example:

```default
Index(F("height") * F("weight"), Round("weight"), name="calc_idx")
```

creates an index on the result of multiplying fields `height` and `weight`
and the `weight` rounded to the nearest integer.

[`Index.name`](#django.db.models.Index.name) is required when using `*expressions`.

### `fields`

#### Index.fields

A list or tuple of the name of the fields on which the index is desired.

By default, indexes are created with an ascending order for each column. To
define an index with a descending order for a column, add a hyphen before the
field’s name.

For example `Index(fields=['headline', '-pub_date'])` would create SQL with
`(headline, pub_date DESC)`.

### `name`

#### Index.name

The name of the index. If `name` isn’t provided Django will auto-generate a
name. For compatibility with different databases, index names cannot be longer
than 30 characters and shouldn’t start with a number (0-9) or underscore (_).

### `db_tablespace`

#### Index.db_tablespace

The name of the [database tablespace](../../topics/db/tablespaces.md) to use for
this index. For single field indexes, if `db_tablespace` isn’t provided, the
index is created in the `db_tablespace` of the field.

If [`Field.db_tablespace`](fields.md#django.db.models.Field.db_tablespace) isn’t specified (or if the index uses multiple
fields), the index is created in tablespace specified in the
[`db_tablespace`](options.md#django.db.models.Options.db_tablespace) option inside the model’s
`class Meta`. If neither of those tablespaces are set, the index is created
in the same tablespace as the table.

#### SEE ALSO
For a list of PostgreSQL-specific indexes, see
[`django.contrib.postgres.indexes`](../contrib/postgres/indexes.md#module-django.contrib.postgres.indexes).

### `opclasses`

#### Index.opclasses

The names of the [PostgreSQL operator classes](https://www.postgresql.org/docs/current/indexes-opclass.html) to use for
this index. If you require a custom operator class, you must provide one for
each field in the index.

For example, `GinIndex(name='json_index', fields=['jsonfield'],
opclasses=['jsonb_path_ops'])` creates a gin index on `jsonfield` using
`jsonb_path_ops`.

`opclasses` are ignored for databases besides PostgreSQL.

[`Index.name`](#django.db.models.Index.name) is required when using `opclasses`.

### `condition`

#### Index.condition

If the table is very large and your queries mostly target a subset of rows,
it may be useful to restrict an index to that subset. Specify a condition as a
[`Q`](querysets.md#django.db.models.Q). For example, `condition=Q(pages__gt=400)`
indexes records with more than 400 pages.

[`Index.name`](#django.db.models.Index.name) is required when using `condition`.

### `include`

#### Index.include

A list or tuple of the names of the fields to be included in the covering index
as non-key columns. This allows index-only scans to be used for queries that
select only included fields ([`include`](#django.db.models.Index.include)) and filter only by indexed
fields ([`fields`](#django.db.models.Index.fields)).

For example:

```default
Index(name="covering_index", fields=["headline"], include=["pub_date"])
```

will allow filtering on `headline`, also selecting `pub_date`, while
fetching data only from the index.

Using `include` will produce a smaller index than using a multiple column
index but with the drawback that non-key columns can not be used for sorting or
filtering.

`include` is ignored for databases besides PostgreSQL.

[`Index.name`](#django.db.models.Index.name) is required when using `include`.

See the PostgreSQL documentation for more details about [covering indexes](https://www.postgresql.org/docs/current/indexes-index-only-scans.html).

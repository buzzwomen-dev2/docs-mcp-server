# PostgreSQL specific model indexes

The following are PostgreSQL specific [indexes](../../models/indexes.md)
available from the `django.contrib.postgres.indexes` module.

## `BloomIndex`

### *class* BloomIndex(\*expressions, length=None, columns=(), \*\*options)

Creates a [bloom](https://www.postgresql.org/docs/current/bloom.html) index.

To use this index access you need to activate the [bloom](https://www.postgresql.org/docs/current/bloom.html) extension on
PostgreSQL. You can install it using the
[`BloomExtension`](operations.md#django.contrib.postgres.operations.BloomExtension) migration
operation.

Provide an integer number of bits from 1 to 4096 to the `length`
parameter to specify the length of each index entry. PostgreSQL’s default
is 80.

The `columns` argument takes a tuple or list of up to 32 values that are
integer number of bits from 1 to 4095.

## `BrinIndex`

### *class* BrinIndex(\*expressions, autosummarize=None, pages_per_range=None, \*\*options)

Creates a [BRIN index](https://www.postgresql.org/docs/current/brin.html).

Set the `autosummarize` parameter to `True` to enable [automatic
summarization](https://www.postgresql.org/docs/current/brin.html#BRIN-OPERATION) to be performed by autovacuum.

The `pages_per_range` argument takes a positive integer.

## `BTreeIndex`

### *class* BTreeIndex(\*expressions, fillfactor=None, deduplicate_items=None, \*\*options)

Creates a B-Tree index.

Provide an integer value from 10 to 100 to the [fillfactor](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-STORAGE-PARAMETERS) parameter to
tune how packed the index pages will be. PostgreSQL’s default is 90.

Provide a boolean value to the [deduplicate_items](https://www.postgresql.org/docs/current/btree.html#BTREE-DEDUPLICATION) parameter to control
whether deduplication is enabled. PostgreSQL enables deduplication by
default.

## `GinIndex`

### *class* GinIndex(\*expressions, fastupdate=None, gin_pending_list_limit=None, \*\*options)

Creates a [gin index](https://www.postgresql.org/docs/current/gin.html).

To use this index on data types not in the [built-in operator classes](https://www.postgresql.org/docs/current/gin.html#GIN-BUILTIN-OPCLASSES),
you need to activate the [btree_gin extension](https://www.postgresql.org/docs/current/btree-gin.html) on
PostgreSQL. You can install it using the
[`BtreeGinExtension`](operations.md#django.contrib.postgres.operations.BtreeGinExtension) migration
operation.

Set the `fastupdate` parameter to `False` to disable the [GIN Fast
Update Technique](https://www.postgresql.org/docs/current/gin.html#GIN-FAST-UPDATE) that’s enabled by default in PostgreSQL.

Provide an integer number of kilobytes to the [gin_pending_list_limit](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-GIN-PENDING-LIST-LIMIT)
parameter to tune the maximum size of the GIN pending list which is used
when `fastupdate` is enabled.

## `GistIndex`

### *class* GistIndex(\*expressions, buffering=None, fillfactor=None, \*\*options)

Creates a [GiST index](https://www.postgresql.org/docs/current/gist.html). These indexes are
automatically created on spatial fields with [`spatial_index=True`](../gis/model-api.md#django.contrib.gis.db.models.BaseSpatialField.spatial_index). They’re
also useful on other types, such as
[`HStoreField`](fields.md#django.contrib.postgres.fields.HStoreField) or the [range
fields](fields.md#range-fields).

To use this index on data types not in the built-in [gist operator classes](https://www.postgresql.org/docs/current/gist.html#GIST-BUILTIN-OPCLASSES),
you need to activate the [btree_gist extension](https://www.postgresql.org/docs/current/btree-gist.html) on PostgreSQL.
You can install it using the
[`BtreeGistExtension`](operations.md#django.contrib.postgres.operations.BtreeGistExtension) migration
operation.

Set the `buffering` parameter to `True` or `False` to manually enable
or disable [buffering build](https://www.postgresql.org/docs/current/gist.html#GIST-BUFFERING-BUILD) of the index.

Provide an integer value from 10 to 100 to the [fillfactor](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-STORAGE-PARAMETERS) parameter to
tune how packed the index pages will be. PostgreSQL’s default is 90.

## `HashIndex`

### *class* HashIndex(\*expressions, fillfactor=None, \*\*options)

Creates a hash index.

Provide an integer value from 10 to 100 to the [fillfactor](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-STORAGE-PARAMETERS) parameter to
tune how packed the index pages will be. PostgreSQL’s default is 90.

## `SpGistIndex`

### *class* SpGistIndex(\*expressions, fillfactor=None, \*\*options)

Creates an [SP-GiST index](https://www.postgresql.org/docs/current/spgist.html).

Provide an integer value from 10 to 100 to the [fillfactor](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-STORAGE-PARAMETERS) parameter to
tune how packed the index pages will be. PostgreSQL’s default is 90.

## `OpClass()` expressions

### *class* OpClass(expression, name)

An `OpClass()` expression represents the `expression` with a custom
[operator class](https://www.postgresql.org/docs/current/indexes-opclass.html) that can be used to define functional indexes, functional
unique constraints, or exclusion constraints. To use it, you need to add
`'django.contrib.postgres'` in your [`INSTALLED_APPS`](../../settings.md#std-setting-INSTALLED_APPS). Set the
`name` parameter to the name of the [operator class](https://www.postgresql.org/docs/current/indexes-opclass.html).

For example:

```default
Index(
    OpClass(Lower("username"), name="varchar_pattern_ops"),
    name="lower_username_idx",
)
```

creates an index on `Lower('username')` using `varchar_pattern_ops`.

```default
UniqueConstraint(
    OpClass(Upper("description"), name="text_pattern_ops"),
    name="upper_description_unique",
)
```

creates a unique constraint on `Upper('description')` using
`text_pattern_ops`.

```default
ExclusionConstraint(
    name="exclude_overlapping_ops",
    expressions=[
        (OpClass("circle", name="circle_ops"), RangeOperators.OVERLAPS),
    ],
)
```

creates an exclusion constraint on `circle` using `circle_ops`.

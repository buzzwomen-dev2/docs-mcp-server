# Constraints reference

The classes defined in this module create database constraints. They are added
in the model [`Meta.constraints`](options.md#django.db.models.Options.constraints)
option.

## `BaseConstraint`

### *class* BaseConstraint(\*name, violation_error_code=None, violation_error_message=None)

Base class for all constraints. Subclasses must implement
`constraint_sql()`, `create_sql()`, `remove_sql()` and
`validate()` methods.

All constraints have the following parameters in common:

### `name`

#### BaseConstraint.name

The name of the constraint. You must always specify a unique name for the
constraint.

### `violation_error_code`

#### BaseConstraint.violation_error_code

The error code used when `ValidationError` is raised during
[model validation](instances.md#validating-objects). Defaults to `None`.

### `violation_error_message`

#### BaseConstraint.violation_error_message

The error message used when `ValidationError` is raised during
[model validation](instances.md#validating-objects). Defaults to
`"Constraint “%(name)s” is violated."`.

### `validate()`

#### BaseConstraint.validate(model, instance, exclude=None, using=DEFAULT_DB_ALIAS)

Validates that the constraint, defined on `model`, is respected on the
`instance`. This will do a query on the database to ensure that the
constraint is respected. If fields in the `exclude` list are needed to
validate the constraint, the constraint is ignored.

Raise a `ValidationError` if the constraint is violated.

This method must be implemented by a subclass.

## `CheckConstraint`

### *class* CheckConstraint(, condition, name, violation_error_code=None, violation_error_message=None)

Creates a check constraint in the database.

### `condition`

#### CheckConstraint.condition

A [`Q`](querysets.md#django.db.models.Q) object or boolean [`Expression`](expressions.md#django.db.models.Expression) that
specifies the conditional check you want the constraint to enforce.

For example:

```default
CheckConstraint(condition=Q(age__gte=18), name="age_gte_18")
```

ensures the age field is never less than 18.

## `UniqueConstraint`

### *class* UniqueConstraint(\*expressions, fields=(), name=None, condition=None, deferrable=None, include=None, opclasses=(), nulls_distinct=None, violation_error_code=None, violation_error_message=None)

Creates a unique constraint in the database.

### `expressions`

#### UniqueConstraint.expressions

Positional argument `*expressions` allows creating functional unique
constraints on expressions and database functions.

For example:

```default
UniqueConstraint(Lower("name").desc(), "category", name="unique_lower_name_category")
```

creates a unique constraint on the lowercased value of the `name` field in
descending order and the `category` field in the default ascending order.

Functional unique constraints have the same database restrictions as
[`Index.expressions`](indexes.md#django.db.models.Index.expressions).

### `fields`

#### UniqueConstraint.fields

A list of field names that specifies the unique set of columns you want the
constraint to enforce.

For example:

```default
UniqueConstraint(fields=["room", "date"], name="unique_booking")
```

ensures each room can only be booked once for each date.

### `condition`

#### UniqueConstraint.condition

A [`Q`](querysets.md#django.db.models.Q) object that specifies the condition you want the constraint to
enforce.

For example:

```default
UniqueConstraint(fields=["user"], condition=Q(status="DRAFT"), name="unique_draft_user")
```

ensures that each user only has one draft.

These conditions have the same database restrictions as
[`Index.condition`](indexes.md#django.db.models.Index.condition).

### `deferrable`

#### UniqueConstraint.deferrable

Set this parameter to create a deferrable unique constraint. Accepted values
are `Deferrable.DEFERRED` or `Deferrable.IMMEDIATE`. For example:

```default
from django.db.models import Deferrable, UniqueConstraint

UniqueConstraint(
    name="unique_order",
    fields=["order"],
    deferrable=Deferrable.DEFERRED,
)
```

By default constraints are not deferred. A deferred constraint will not be
enforced until the end of the transaction. An immediate constraint will be
enforced immediately after every command.

#### WARNING
Deferred unique constraints may lead to a [performance penalty](https://www.postgresql.org/docs/current/sql-createtable.html#id-1.9.3.85.9.4).

### `include`

#### UniqueConstraint.include

A list or tuple of the names of the fields to be included in the covering
unique index as non-key columns. This allows index-only scans to be used for
queries that select only included fields ([`include`](#django.db.models.UniqueConstraint.include))
and filter only by unique fields ([`fields`](#django.db.models.UniqueConstraint.fields)).

For example:

```default
UniqueConstraint(name="unique_booking", fields=["room", "date"], include=["full_name"])
```

will allow filtering on `room` and `date`, also selecting `full_name`,
while fetching data only from the index.

Unique constraints with non-key columns are ignored for databases besides
PostgreSQL.

Non-key columns have the same database restrictions as [`Index.include`](indexes.md#django.db.models.Index.include).

### `opclasses`

#### UniqueConstraint.opclasses

The names of the [PostgreSQL operator classes](https://www.postgresql.org/docs/current/indexes-opclass.html) to use for
this unique index. If you require a custom operator class, you must provide one
for each field in the index.

For example:

```default
UniqueConstraint(
    name="unique_username", fields=["username"], opclasses=["varchar_pattern_ops"]
)
```

creates a unique index on `username` using `varchar_pattern_ops`.

`opclasses` are ignored for databases besides PostgreSQL.

### `nulls_distinct`

#### UniqueConstraint.nulls_distinct

Whether rows containing `NULL` values covered by the unique constraint should
be considered distinct from each other. The default value is `None` which
uses the database default which is `True` on most backends.

For example:

```default
UniqueConstraint(name="ordering", fields=["ordering"], nulls_distinct=False)
```

creates a unique constraint that only allows one row to store a `NULL` value
in the `ordering` column.

Unique constraints with `nulls_distinct` are ignored for databases besides
PostgreSQL.

### `violation_error_code`

#### UniqueConstraint.violation_error_code

The error code used when a `ValidationError` is raised during
[model validation](instances.md#validating-objects).

Defaults to [`BaseConstraint.violation_error_code`](#django.db.models.BaseConstraint.violation_error_code), when either
[`UniqueConstraint.condition`](#django.db.models.UniqueConstraint.condition) is set or [`UniqueConstraint.fields`](#django.db.models.UniqueConstraint.fields)
is not set.

If [`UniqueConstraint.fields`](#django.db.models.UniqueConstraint.fields) is set without a
[`UniqueConstraint.condition`](#django.db.models.UniqueConstraint.condition), defaults to the
[`Meta.unique_together`](options.md#django.db.models.Options.unique_together) error
code when there are multiple fields, and to the [`Field.unique`](fields.md#django.db.models.Field.unique) error
code when there is a single field.

### `violation_error_message`

#### UniqueConstraint.violation_error_message

The error message used when a `ValidationError` is raised during
[model validation](instances.md#validating-objects).

Defaults to [`BaseConstraint.violation_error_message`](#django.db.models.BaseConstraint.violation_error_message), when either
[`UniqueConstraint.condition`](#django.db.models.UniqueConstraint.condition) is set or [`UniqueConstraint.fields`](#django.db.models.UniqueConstraint.fields)
is not set.

If [`UniqueConstraint.fields`](#django.db.models.UniqueConstraint.fields) is set without a
[`UniqueConstraint.condition`](#django.db.models.UniqueConstraint.condition), defaults to the
[`Meta.unique_together`](options.md#django.db.models.Options.unique_together) error
message when there are multiple fields, and to the [`Field.unique`](fields.md#django.db.models.Field.unique) error
message when there is a single field.

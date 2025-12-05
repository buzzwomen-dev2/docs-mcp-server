# Model `Meta` options

This document explains all the possible [metadata options](../../topics/db/models.md#meta-options) that you can give your model in its internal
`class Meta`.

## Available `Meta` options

### `abstract`

#### Options.abstract

If `abstract = True`, this model will be an
[abstract base class](../../topics/db/models.md#abstract-base-classes).

### `app_label`

#### Options.app_label

If a model is defined outside of an application in
[`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS), it must declare which app it belongs to:

```default
app_label = "myapp"
```

If you want to represent a model with the format `app_label.object_name`
or `app_label.model_name` you can use `model._meta.label`
or `model._meta.label_lower` respectively.

### `base_manager_name`

#### Options.base_manager_name

The attribute name of the manager, for example, `'objects'`, to use for
the model’s [`_base_manager`](../../topics/db/managers.md#django.db.models.Model._base_manager).

### `db_table`

#### Options.db_table

The name of the database table to use for the model:

```default
db_table = "music_album"
```

<a id="table-names"></a>

#### Table names

To save you time, Django automatically derives the name of the database table
from the name of your model class and the app that contains it. A model’s
database table name is constructed by joining the model’s “app label” – the
name you used in [`manage.py startapp`](../django-admin.md#django-admin-startapp) – to the model’s
class name, with an underscore between them.

For example, if you have an app `bookstore` (as created by
`manage.py startapp bookstore`), a model defined as `class Book` will have
a database table named `bookstore_book`.

To override the database table name, use the `db_table` parameter in
`class Meta`.

If your database table name is an SQL reserved word, or contains characters
that aren’t allowed in Python variable names – notably, the hyphen – that’s
OK. Django quotes column and table names behind the scenes.

### `db_table_comment`

#### Options.db_table_comment

The comment on the database table to use for this model. It is useful for
documenting database tables for individuals with direct database access who may
not be looking at your Django code. For example:

```default
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()

    class Meta:
        db_table_comment = "Question answers"
```

### `db_tablespace`

#### Options.db_tablespace

The name of the [database tablespace](../../topics/db/tablespaces.md) to use
for this model. The default is the project’s [`DEFAULT_TABLESPACE`](../settings.md#std-setting-DEFAULT_TABLESPACE)
setting, if set. If the backend doesn’t support tablespaces, this option is
ignored.

### `default_manager_name`

#### Options.default_manager_name

The name of the manager to use for the model’s
[`_default_manager`](../../topics/db/managers.md#django.db.models.Model._default_manager).

### `default_related_name`

#### Options.default_related_name

The name that will be used by default for the relation from a related
object back to this one. The default is `<model_name>_set`.

This option also sets [`related_query_name`](fields.md#django.db.models.ForeignKey.related_query_name).

As the reverse name for a field should be unique, be careful if you intend
to subclass your model. To work around name collisions, part of the name
should contain `'%(app_label)s'` and `'%(model_name)s'`, which are
replaced respectively by the name of the application the model is in,
and the name of the model, both lowercased. See the paragraph on
[related names for abstract models](../../topics/db/models.md#abstract-related-name).

### `get_latest_by`

#### Options.get_latest_by

The name of a field or a list of field names in the model, typically
[`DateField`](fields.md#django.db.models.DateField), [`DateTimeField`](fields.md#django.db.models.DateTimeField), or [`IntegerField`](fields.md#django.db.models.IntegerField). This
specifies the default field(s) to use in your model [`Manager`](../../topics/db/managers.md#django.db.models.Manager)’s
[`latest()`](querysets.md#django.db.models.query.QuerySet.latest) and
[`earliest()`](querysets.md#django.db.models.query.QuerySet.earliest) methods.

Example:

```default
# Latest by ascending order_date.
get_latest_by = "order_date"

# Latest by priority descending, order_date ascending.
get_latest_by = ["-priority", "order_date"]
```

See the [`latest()`](querysets.md#django.db.models.query.QuerySet.latest) docs for more.

### `managed`

#### Options.managed

Defaults to `True`, meaning Django will create the appropriate database
tables in [`migrate`](../django-admin.md#django-admin-migrate) or as part of migrations and remove them as
part of a [`flush`](../django-admin.md#django-admin-flush) management command. That is, Django
*manages* the database tables’ lifecycles.

If `False`, no database table creation, modification, or deletion
operations will be performed for this model. This is useful if the model
represents an existing table or a database view that has been created by
some other means. This is the *only* difference when `managed=False`. All
other aspects of model handling are exactly the same as normal. This
includes

1. Adding an automatic primary key field to the model if you don’t
   declare it. To avoid confusion for later code readers, it’s
   recommended to specify all the columns from the database table you
   are modeling when using unmanaged models.
2. If a model with `managed=False` contains a
   [`ManyToManyField`](fields.md#django.db.models.ManyToManyField) that points to another
   unmanaged model, then the intermediate table for the many-to-many
   join will also not be created. However, the intermediary table
   between one managed and one unmanaged model *will* be created.

   If you need to change this default behavior, create the intermediary
   table as an explicit model (with `managed` set as needed) and use
   the [`ManyToManyField.through`](fields.md#django.db.models.ManyToManyField.through) attribute to make the relation
   use your custom model.

For tests involving models with `managed=False`, it’s up to you to ensure
the correct tables are created as part of the test setup.

If you’re interested in changing the Python-level behavior of a model
class, you *could* use `managed=False` and create a copy of an existing
model. However, there’s a better approach for that situation:
[Proxy models](../../topics/db/models.md#proxy-models).

### `order_with_respect_to`

#### Options.order_with_respect_to

Makes this object orderable with respect to the given field, usually a
`ForeignKey`. This can be used to make related objects orderable with
respect to a parent object. For example, if an `Answer` relates to a
`Question` object, and a question has more than one answer, and the order
of answers matters, you’d do this:

```default
from django.db import models


class Question(models.Model):
    text = models.TextField()
    # ...


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # ...

    class Meta:
        order_with_respect_to = "question"
```

When `order_with_respect_to` is set, two additional methods are provided
to retrieve and to set the order of the related objects:
`get_RELATED_order()` and `set_RELATED_order()`, where `RELATED` is
the lowercased model name. For example, assuming that a `Question` object
has multiple related `Answer` objects, the list returned contains the
primary keys of the related `Answer` objects:

```pycon
>>> question = Question.objects.get(id=1)
>>> question.get_answer_order()
[1, 2, 3]
```

The order of a `Question` object’s related `Answer` objects can be set
by passing in a list of `Answer` primary keys:

```pycon
>>> question.set_answer_order([3, 1, 2])
```

The related objects also get two methods, `get_next_in_order()` and
`get_previous_in_order()`, which can be used to access those objects in
their proper order. Assuming the `Answer` objects are ordered by `id`:

```pycon
>>> answer = Answer.objects.get(id=2)
>>> answer.get_next_in_order()
<Answer: 3>
>>> answer.get_previous_in_order()
<Answer: 1>
```

### `ordering`

#### Options.ordering

The default ordering for the object, for use when obtaining lists of
objects:

```default
ordering = ["-order_date"]
```

This is a tuple or list of strings and/or query expressions. Each string is
a field name with an optional “-” prefix, which indicates descending order.
Fields without a leading “-” will be ordered ascending. Use the string “?”
to order randomly.

For example, to order by a `pub_date` field ascending, use this:

```default
ordering = ["pub_date"]
```

To order by `pub_date` descending, use this:

```default
ordering = ["-pub_date"]
```

To order by `pub_date` descending, then by `author` ascending, use
this:

```default
ordering = ["-pub_date", "author"]
```

You can also use [query expressions](expressions.md). To
order by `author` ascending and make null values sort last, use this:

```default
from django.db.models import F

ordering = [F("author").asc(nulls_last=True)]
```

#### WARNING
Ordering is not a free operation. Each field you add to the ordering
incurs a cost to your database. Each foreign key you add will
implicitly include all of its default orderings as well.

If a query doesn’t have an ordering specified, results are returned from
the database in an unspecified order. A particular ordering is guaranteed
only when ordering by a set of fields that uniquely identify each object in
the results. For example, if a `name` field isn’t unique, ordering by it
won’t guarantee objects with the same name always appear in the same order.

### `permissions`

#### Options.permissions

Extra permissions to enter into the permissions table when creating this
object. Add, change, delete, and view permissions are automatically created
for each model. This example specifies an extra permission,
`can_deliver_pizzas`:

```default
permissions = [("can_deliver_pizzas", "Can deliver pizzas")]
```

This is a list or tuple of 2-tuples in the format `(permission_code,
human_readable_permission_name)`.

### `default_permissions`

#### Options.default_permissions

Defaults to `('add', 'change', 'delete', 'view')`. You may customize this
list, for example, by setting this to an empty list if your app doesn’t
require any of the default permissions. It must be specified on the model
before the model is created by [`migrate`](../django-admin.md#django-admin-migrate) in order to prevent any
omitted permissions from being created.

### `proxy`

#### Options.proxy

If `proxy = True`, a model which subclasses another model will be treated
as a [proxy model](../../topics/db/models.md#proxy-models).

### `required_db_features`

#### Options.required_db_features

List of database features that the current connection should have so that
the model is considered during the migration phase. For example, if you set
this list to `['gis_enabled']`, the model will only be synchronized on
GIS-enabled databases. It’s also useful to skip some models when testing
with several database backends. Avoid relations between models that may or
may not be created as the ORM doesn’t handle this.

### `required_db_vendor`

#### Options.required_db_vendor

Name of a supported database vendor that this model is specific to. Current
built-in vendor names are: `sqlite`, `postgresql`, `mysql`,
`oracle`. If this attribute is not empty and the current connection
vendor doesn’t match it, the model will not be synchronized.

### `select_on_save`

#### Options.select_on_save

Determines if Django will use the pre-1.6
[`django.db.models.Model.save()`](instances.md#django.db.models.Model.save) algorithm. The old algorithm
uses `SELECT` to determine if there is an existing row to be updated.
The new algorithm tries an `UPDATE` directly. In some rare cases the
`UPDATE` of an existing row isn’t visible to Django. An example is the
PostgreSQL `ON UPDATE` trigger which returns `NULL`. In such cases the
new algorithm will end up doing an `INSERT` even when a row exists in
the database.

Usually there is no need to set this attribute. The default is
`False`.

See [`django.db.models.Model.save()`](instances.md#django.db.models.Model.save) for more about the old and
new saving algorithm.

### `indexes`

#### Options.indexes

A list of [indexes](indexes.md) that you want to define on
the model:

```default
from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["first_name"], name="first_name_idx"),
        ]
```

### `unique_together`

#### Options.unique_together

Sets of field names that, taken together, must be unique:

```default
unique_together = [["driver", "restaurant"]]
```

This is a list of lists that must be unique when considered together.
It’s used in the Django admin and is enforced at the database level (i.e.,
the appropriate `UNIQUE` statements are included in the `CREATE TABLE`
statement).

For convenience, `unique_together` can be a single list when dealing with
a single set of fields:

```default
unique_together = ["driver", "restaurant"]
```

A [`ManyToManyField`](fields.md#django.db.models.ManyToManyField) cannot be included in
`unique_together`. (It’s not clear what that would even mean!) If you
need to validate uniqueness related to a
[`ManyToManyField`](fields.md#django.db.models.ManyToManyField), try using a signal or
an explicit [`through`](fields.md#django.db.models.ManyToManyField.through) model.

The `ValidationError` raised during model validation when the constraint
is violated has the `unique_together` error code.

### `constraints`

#### Options.constraints

A list of [constraints](constraints.md) that you want to
define on the model:

```default
from django.db import models


class Customer(models.Model):
    age = models.IntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(age__gte=18), name="age_gte_18"),
        ]
```

### `verbose_name`

#### Options.verbose_name

A human-readable name for the object, singular:

```default
verbose_name = "pizza"
```

If this isn’t given, Django will use a munged version of the class name:
`CamelCase` becomes `camel case`.

### `verbose_name_plural`

#### Options.verbose_name_plural

The plural name for the object:

```default
verbose_name_plural = "stories"
```

If this isn’t given, Django will use [`verbose_name`](#django.db.models.Options.verbose_name) +
`"s"`.

## Read-only `Meta` attributes

### `label`

#### Options.label

Representation of the object, returns `app_label.object_name`, e.g.
`'polls.Question'`.

### `label_lower`

#### Options.label_lower

Representation of the model, returns `app_label.model_name`, e.g.
`'polls.question'`.

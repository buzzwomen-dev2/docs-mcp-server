# Model instance reference

This document describes the details of the `Model` API. It builds on the
material presented in the [model](../../topics/db/models.md) and [database
query](../../topics/db/queries.md) guides, so you’ll probably want to read and
understand those documents before reading this one.

Throughout this reference we’ll use the [example blog models](../../topics/db/queries.md#queryset-model-example) presented in the [database query guide](../../topics/db/queries.md).

## Creating objects

To create a new instance of a model, instantiate it like any other Python
class:

### *class* Model(\*\*kwargs)

The keyword arguments are the names of the fields you’ve defined on your model.
Note that instantiating a model in no way touches your database; for that, you
need to [`save()`](#django.db.models.Model.save).

#### NOTE
You may be tempted to customize the model by overriding the `__init__`
method. If you do so, however, take care not to change the calling
signature as any change may prevent the model instance from being saved.
Additionally, referring to model fields within `__init__` may potentially
result in infinite recursion errors in some circumstances. Rather than
overriding `__init__`, try using one of these approaches:

1. Add a classmethod on the model class:
   ```default
   from django.db import models


   class Book(models.Model):
       title = models.CharField(max_length=100)

       @classmethod
       def create(cls, title):
           book = cls(title=title)
           # do something with the book
           return book


   book = Book.create("Pride and Prejudice")
   ```
2. Add a method on a custom manager (usually preferred):
   ```default
   class BookManager(models.Manager):
       def create_book(self, title):
           book = self.create(title=title)
           # do something with the book
           return book


   class Book(models.Model):
       title = models.CharField(max_length=100)

       objects = BookManager()


   book = Book.objects.create_book("Pride and Prejudice")
   ```

### Customizing model loading

#### *classmethod* Model.from_db(db, field_names, values)

The `from_db()` method can be used to customize model instance creation
when loading from the database.

The `db` argument contains the database alias for the database the model
is loaded from, `field_names` contains the names of all loaded fields, and
`values` contains the loaded values for each field in `field_names`. The
`field_names` are in the same order as the `values`. If all of the model’s
fields are present, then `values` are guaranteed to be in the order
`__init__()` expects them. That is, the instance can be created by
`cls(*values)`. If any fields are deferred, they won’t appear in
`field_names`. In that case, assign a value of `django.db.models.DEFERRED`
to each of the missing fields.

In addition to creating the new model, the `from_db()` method must set the
`adding` and `db` flags in the new instance’s [`_state`](#django.db.models.Model._state)
attribute.

Below is an example showing how to record the initial values of fields that
are loaded from the database:

```default
from django.db.models import DEFERRED


@classmethod
def from_db(cls, db, field_names, values):
    # Default implementation of from_db() (subject to change and could
    # be replaced with super()).
    if len(values) != len(cls._meta.concrete_fields):
        values = list(values)
        values.reverse()
        values = [
            values.pop() if f.attname in field_names else DEFERRED
            for f in cls._meta.concrete_fields
        ]
    instance = cls(*values)
    instance._state.adding = False
    instance._state.db = db
    # customization to store the original field values on the instance
    instance._loaded_values = dict(
        zip(field_names, (value for value in values if value is not DEFERRED))
    )
    return instance


def save(self, **kwargs):
    # Check how the current values differ from ._loaded_values. For example,
    # prevent changing the creator_id of the model. (This example doesn't
    # support cases where 'creator_id' is deferred).
    if not self._state.adding and (
        self.creator_id != self._loaded_values["creator_id"]
    ):
        raise ValueError("Updating the value of creator isn't allowed")
    super().save(**kwargs)
```

The example above shows a full `from_db()` implementation to clarify how that
is done. In this case it would be possible to use a `super()` call in the
`from_db()` method.

## Refreshing objects from database

If you delete a field from a model instance, accessing it again reloads the
value from the database:

```pycon
>>> obj = MyModel.objects.first()
>>> del obj.field
>>> obj.field  # Loads the field from the database
```

#### Model.refresh_from_db(using=None, fields=None, from_queryset=None)

#### Model.arefresh_from_db(using=None, fields=None, from_queryset=None)

*Asynchronous version*: `arefresh_from_db()`

If you need to reload a model’s values from the database, you can use the
`refresh_from_db()` method. When this method is called without arguments the
following is done:

1. All non-deferred fields of the model are updated to the values currently
   present in the database.
2. Any cached relations are cleared from the reloaded instance.

Only fields of the model are reloaded from the database. Other
database-dependent values such as annotations aren’t reloaded. Any
[`@cached_property`](../utils.md#django.utils.functional.cached_property) attributes
aren’t cleared either.

The reloading happens from the database the instance was loaded from, or from
the default database if the instance wasn’t loaded from the database. The
`using` argument can be used to force the database used for reloading.

It is possible to force the set of fields to be loaded by using the `fields`
argument.

For example, to test that an `update()` call resulted in the expected
update, you could write a test similar to this:

```default
def test_update_result(self):
    obj = MyModel.objects.create(val=1)
    MyModel.objects.filter(pk=obj.pk).update(val=F("val") + 1)
    # At this point obj.val is still 1, but the value in the database
    # was updated to 2. The object's updated value needs to be reloaded
    # from the database.
    obj.refresh_from_db()
    self.assertEqual(obj.val, 2)
```

When a deferred field is loaded on-demand for a single model instance, the
loading happens through this method. Thus it is possible to customize the way
this loading happens. The example below shows how one can reload all of the
instance’s fields when a deferred field is loaded on-demand:

```default
class ExampleModel(models.Model):
    def refresh_from_db(self, using=None, fields=None, **kwargs):
        # fields contains the name of the deferred field to be
        # loaded.
        if fields is not None:
            fields = set(fields)
            deferred_fields = self.get_deferred_fields()
            # If any deferred field is going to be loaded
            if fields.intersection(deferred_fields):
                # then load all of them
                fields = fields.union(deferred_fields)
        super().refresh_from_db(using, fields, **kwargs)
```

The `from_queryset` argument allows using a different queryset than the one
created from [`_base_manager`](../../topics/db/managers.md#django.db.models.Model._base_manager). It gives you more
control over how the model is reloaded. For example, when your model uses soft
deletion you can make `refresh_from_db()` to take this into account:

```default
obj.refresh_from_db(from_queryset=MyModel.active_objects.all())
```

You can cache related objects that otherwise would be cleared from the reloaded
instance:

```default
obj.refresh_from_db(from_queryset=MyModel.objects.select_related("related_field"))
```

You can lock the row until the end of transaction before reloading a model’s
values:

```default
obj.refresh_from_db(from_queryset=MyModel.objects.select_for_update())
```

#### Model.get_deferred_fields()

A helper method that returns a set containing the attribute names of all those
fields that are currently deferred for this model.

<a id="validating-objects"></a>

## Validating objects

There are four steps involved in validating a model:

1. Validate the model fields - [`Model.clean_fields()`](#django.db.models.Model.clean_fields)
2. Validate the model as a whole - [`Model.clean()`](#django.db.models.Model.clean)
3. Validate the field uniqueness - [`Model.validate_unique()`](#django.db.models.Model.validate_unique)
4. Validate the constraints - [`Model.validate_constraints()`](#django.db.models.Model.validate_constraints)

All four steps are performed when you call a model’s [`full_clean()`](#django.db.models.Model.full_clean)
method.

When you use a [`ModelForm`](../../topics/forms/modelforms.md#django.forms.ModelForm), the call to
[`is_valid()`](../forms/api.md#django.forms.Form.is_valid) will perform these validation steps for
all the fields that are included on the form. See the [ModelForm
documentation](../../topics/forms/modelforms.md) for more information. You should only
need to call a model’s [`full_clean()`](#django.db.models.Model.full_clean) method if you plan to handle
validation errors yourself, or if you have excluded fields from the
[`ModelForm`](../../topics/forms/modelforms.md#django.forms.ModelForm) that require validation.

#### Model.full_clean(exclude=None, validate_unique=True, validate_constraints=True)

This method calls [`Model.clean_fields()`](#django.db.models.Model.clean_fields), [`Model.clean()`](#django.db.models.Model.clean),
[`Model.validate_unique()`](#django.db.models.Model.validate_unique) (if `validate_unique` is `True`),  and
[`Model.validate_constraints()`](#django.db.models.Model.validate_constraints) (if `validate_constraints` is `True`)
in that order and raises a [`ValidationError`](../exceptions.md#django.core.exceptions.ValidationError) that
has a `message_dict` attribute containing errors from all four stages.

The optional `exclude` argument can be used to provide a `set` of field
names that can be excluded from validation and cleaning.
[`ModelForm`](../../topics/forms/modelforms.md#django.forms.ModelForm) uses this argument to exclude fields that
aren’t present on your form from being validated since any errors raised could
not be corrected by the user.

Note that `full_clean()` will *not* be called automatically when you call
your model’s [`save()`](#django.db.models.Model.save) method. You’ll need to call it manually
when you want to run one-step model validation for your own manually created
models. For example:

```default
from django.core.exceptions import ValidationError

try:
    article.full_clean()
except ValidationError as e:
    # Do something based on the errors contained in e.message_dict.
    # Display them to a user, or handle them programmatically.
    pass
```

The first step `full_clean()` performs is to clean each individual field.

#### Model.clean_fields(exclude=None)

This method will validate all fields on your model. The optional `exclude`
argument lets you provide a `set` of field names to exclude from validation.
It will raise a [`ValidationError`](../exceptions.md#django.core.exceptions.ValidationError) if any fields
fail validation.

The second step `full_clean()` performs is to call [`Model.clean()`](#django.db.models.Model.clean).
This method should be overridden to perform custom validation on your model.

#### Model.clean()

This method should be used to provide custom model validation, and to modify
attributes on your model if desired. For instance, you could use it to
automatically provide a value for a field, or to do validation that requires
access to more than a single field:

```default
import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Article(models.Model):
    ...

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if self.status == "draft" and self.pub_date is not None:
            raise ValidationError(_("Draft entries may not have a publication date."))
        # Set the pub_date for published items if it hasn't been set already.
        if self.status == "published" and self.pub_date is None:
            self.pub_date = datetime.date.today()
```

Note, however, that like [`Model.full_clean()`](#django.db.models.Model.full_clean), a model’s `clean()`
method is not invoked when you call your model’s [`save()`](#django.db.models.Model.save) method.

In the above example, the [`ValidationError`](../exceptions.md#django.core.exceptions.ValidationError)
exception raised by `Model.clean()` was instantiated with a string, so it
will be stored in a special error dictionary key,
[`NON_FIELD_ERRORS`](../exceptions.md#django.core.exceptions.NON_FIELD_ERRORS). This key is used for errors
that are tied to the entire model instead of to a specific field:

```default
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

try:
    article.full_clean()
except ValidationError as e:
    non_field_errors = e.message_dict[NON_FIELD_ERRORS]
```

To assign exceptions to a specific field, instantiate the
[`ValidationError`](../exceptions.md#django.core.exceptions.ValidationError) with a dictionary, where the
keys are the field names. We could update the previous example to assign the
error to the `pub_date` field:

```default
class Article(models.Model):
    ...

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if self.status == "draft" and self.pub_date is not None:
            raise ValidationError(
                {"pub_date": _("Draft entries may not have a publication date.")}
            )
        ...
```

If you detect errors in multiple fields during `Model.clean()`, you can also
pass a dictionary mapping field names to errors:

```default
raise ValidationError(
    {
        "title": ValidationError(_("Missing title."), code="required"),
        "pub_date": ValidationError(_("Invalid date."), code="invalid"),
    }
)
```

Then, `full_clean()` will check unique constraints on your model.

#### Model.validate_unique(exclude=None)

This method is similar to [`clean_fields()`](#django.db.models.Model.clean_fields), but validates
uniqueness constraints defined via [`Field.unique`](fields.md#django.db.models.Field.unique),
[`Field.unique_for_date`](fields.md#django.db.models.Field.unique_for_date), [`Field.unique_for_month`](fields.md#django.db.models.Field.unique_for_month),
[`Field.unique_for_year`](fields.md#django.db.models.Field.unique_for_year), or [`Meta.unique_together`](options.md#django.db.models.Options.unique_together) on your model instead of individual
field values. The optional `exclude` argument allows you to provide a `set`
of field names to exclude from validation. It will raise a
[`ValidationError`](../exceptions.md#django.core.exceptions.ValidationError) if any fields fail validation.

[`UniqueConstraint`](constraints.md#django.db.models.UniqueConstraint)s defined in the
[`Meta.constraints`](options.md#django.db.models.Options.constraints) are validated
by [`Model.validate_constraints()`](#django.db.models.Model.validate_constraints).

Note that if you provide an `exclude` argument to `validate_unique()`, any
[`unique_together`](options.md#django.db.models.Options.unique_together) constraint involving one of
the fields you provided will not be checked.

Finally, `full_clean()` will check any other constraints on your model.

#### Model.validate_constraints(exclude=None)

This method validates all constraints defined in
[`Meta.constraints`](options.md#django.db.models.Options.constraints). The
optional `exclude` argument allows you to provide a `set` of field names to
exclude from validation. It will raise a
[`ValidationError`](../exceptions.md#django.core.exceptions.ValidationError) if any constraints fail
validation.

## Saving objects

To save an object back to the database, call `save()`:

#### Model.save(, force_insert=False, force_update=False, using=DEFAULT_DB_ALIAS, update_fields=None)

#### Model.asave(, force_insert=False, force_update=False, using=DEFAULT_DB_ALIAS, update_fields=None)

*Asynchronous version*: `asave()`

For details on using the `force_insert` and `force_update` arguments, see
[Forcing an INSERT or UPDATE](#ref-models-force-insert). Details about the `update_fields` argument
can be found in the [Specifying which fields to save](#ref-models-update-fields) section.

If you want customized saving behavior, you can override this `save()`
method. See [Overriding predefined model methods](../../topics/db/models.md#overriding-model-methods) for more details.

The model save process also has some subtleties; see the sections below.

### Auto-incrementing primary keys

If a model has an [`AutoField`](fields.md#django.db.models.AutoField) — an auto-incrementing
primary key — then that auto-incremented value will be calculated and saved as
an attribute on your object the first time you call `save()`:

```pycon
>>> b2 = Blog(name="Cheddar Talk", tagline="Thoughts on cheese.")
>>> b2.id  # Returns None, because b2 doesn't have an ID yet.
>>> b2.save()
>>> b2.id  # Returns the ID of your new object.
```

There’s no way to tell what the value of an ID will be before you call
`save()`, because that value is calculated by your database, not by Django.

For convenience, each model has an [`AutoField`](fields.md#django.db.models.AutoField) named
`id` by default unless you explicitly specify `primary_key=True` on a field
in your model. See the documentation for [`AutoField`](fields.md#django.db.models.AutoField)
for more details.

#### The `pk` property

#### Model.pk

Regardless of whether you define a primary key field yourself, or let Django
supply one for you, each model will have a property called `pk`. It behaves
like a normal attribute on the model, but is actually an alias for whichever
field or fields compose the primary key for the model. You can read and set
this value, just as you would for any other attribute, and it will update the
correct fields in the model.

#### Explicitly specifying auto-primary-key values

If a model has an [`AutoField`](fields.md#django.db.models.AutoField) but you want to define a
new object’s ID explicitly when saving, define it explicitly before saving,
rather than relying on the auto-assignment of the ID:

```pycon
>>> b3 = Blog(id=3, name="Cheddar Talk", tagline="Thoughts on cheese.")
>>> b3.id  # Returns 3.
>>> b3.save()
>>> b3.id  # Returns 3.
```

If you assign auto-primary-key values manually, make sure not to use an
already-existing primary-key value! If you create a new object with an explicit
primary-key value that already exists in the database, Django will assume
you’re changing the existing record rather than creating a new one.

Given the above `'Cheddar Talk'` blog example, this example would override
the previous record in the database:

```default
b4 = Blog(id=3, name="Not Cheddar", tagline="Anything but cheese.")
b4.save()  # Overrides the previous blog with ID=3!
```

See [How Django knows to UPDATE vs. INSERT](), below, for the reason this
happens.

Explicitly specifying auto-primary-key values is mostly useful for bulk-saving
objects, when you’re confident you won’t have primary-key collision.

If you’re using PostgreSQL, the sequence associated with the primary key might
need to be updated; see [Manually-specifying values of auto-incrementing primary keys](../databases.md#manually-specified-autoincrement-pk).

### What happens when you save?

When you save an object, Django performs the following steps:

1. **Emit a pre-save signal.** The [`pre_save`](../signals.md#django.db.models.signals.pre_save)
   signal is sent, allowing any functions listening for that signal to do
   something.
2. **Preprocess the data.** Each field’s
   [`pre_save()`](fields.md#django.db.models.Field.pre_save) method is called to perform any
   automated data modification that’s needed. For example, the date/time fields
   override `pre_save()` to implement
   [`auto_now_add`](fields.md#django.db.models.DateField.auto_now_add) and
   [`auto_now`](fields.md#django.db.models.DateField.auto_now).
3. **Prepare the data for the database.** Each field’s
   [`get_db_prep_save()`](fields.md#django.db.models.Field.get_db_prep_save) method is asked to provide
   its current value in a data type that can be written to the database.

   Most fields don’t require data preparation. Simple data types, such as
   integers and strings, are ‘ready to write’ as a Python object. However, more
   complex data types often require some modification.

   For example, [`DateField`](fields.md#django.db.models.DateField) fields use a Python
   `datetime` object to store data. Databases don’t store `datetime`
   objects, so the field value must be converted into an ISO-compliant date
   string for insertion into the database.
4. **Insert the data into the database.** The preprocessed, prepared data is
   composed into an SQL statement for insertion into the database.
5. **Emit a post-save signal.** The [`post_save`](../signals.md#django.db.models.signals.post_save)
   signal is sent, allowing any functions listening for that signal to do
   something.

### How Django knows to UPDATE vs. INSERT

You may have noticed Django database objects use the same `save()` method
for creating and changing objects. Django abstracts the need to use `INSERT`
or `UPDATE` SQL statements. Specifically, when you call `save()` and the
object’s primary key attribute does **not** define a
[`default`](fields.md#django.db.models.Field.default) or
[`db_default`](fields.md#django.db.models.Field.db_default), Django follows this algorithm:

* If the object’s primary key attribute is set to anything except `None`,
  Django executes an `UPDATE`.
* If the object’s primary key attribute is *not* set or if the `UPDATE`
  didn’t update anything (e.g. if primary key is set to a value that doesn’t
  exist in the database), Django executes an `INSERT`.

If the object’s primary key attribute defines a
[`default`](fields.md#django.db.models.Field.default) or
[`db_default`](fields.md#django.db.models.Field.db_default) then Django executes an `UPDATE`
if it is an existing model instance and primary key is set to a value that
exists in the database. Otherwise, Django executes an `INSERT`.

The one gotcha here is that you should be careful not to specify a primary-key
value explicitly when saving new objects, if you cannot guarantee the
primary-key value is unused. For more on this nuance, see [Explicitly
specifying auto-primary-key values]() above and [Forcing an INSERT or UPDATE]()
below.

In Django 1.5 and earlier, Django did a `SELECT` when the primary key
attribute was set. If the `SELECT` found a row, then Django did an
`UPDATE`, otherwise it did an `INSERT`. The old algorithm results in one
more query in the `UPDATE` case. There are some rare cases where the database
doesn’t report that a row was updated even if the database contains a row for
the object’s primary key value. An example is the PostgreSQL `ON UPDATE`
trigger which returns `NULL`. In such cases it is possible to revert to the
old algorithm by setting the [`select_on_save`](options.md#django.db.models.Options.select_on_save)
option to `True`.

<a id="ref-models-force-insert"></a>

#### Forcing an INSERT or UPDATE

In some rare circumstances, it’s necessary to be able to force the
[`save()`](#django.db.models.Model.save) method to perform an SQL `INSERT` and not fall back to
doing an `UPDATE`. Or vice-versa: update, if possible, but not insert a new
row. In these cases you can pass the `force_insert=True` or
`force_update=True` parameters to the [`save()`](#django.db.models.Model.save) method.
Passing both parameters is an error: you cannot both insert *and* update at the
same time!

When using [multi-table inheritance](../../topics/db/models.md#multi-table-inheritance), it’s also
possible to provide a tuple of parent classes to `force_insert` in order to
force `INSERT` statements for each base. For example:

```default
Restaurant(pk=1, name="Bob's Cafe").save(force_insert=(Place,))

Restaurant(pk=1, name="Bob's Cafe", rating=4).save(force_insert=(Place, Rating))
```

You can pass `force_insert=(models.Model,)` to force an `INSERT` statement
for all parents. By default, `force_insert=True` only forces the insertion of
a new row for the current model.

#### Versionchanged
When a forced update does not affect any rows a
[`NotUpdated`](class.md#django.db.models.Model.NotUpdated) exception is raised. On previous
versions a generic [`django.db.DatabaseError`](../exceptions.md#django.db.DatabaseError) was raised.

It should be very rare that you’ll need to use these parameters. Django will
almost always do the right thing and trying to override that will lead to
errors that are difficult to track down. This feature is for advanced use
only.

Using `update_fields` will force an update similarly to `force_update`.

<a id="ref-models-field-updates-using-f-expressions"></a>

### Updating attributes based on existing fields

Sometimes you’ll need to perform a simple arithmetic task on a field, such
as incrementing or decrementing the current value. One way of achieving this is
doing the arithmetic in Python like:

```pycon
>>> product = Product.objects.get(name="Venezuelan Beaver Cheese")
>>> product.number_sold += 1
>>> product.save()
```

If the old `number_sold` value retrieved from the database was 10, then
the value of 11 will be written back to the database.

The process can be made robust, [avoiding a race condition](expressions.md#avoiding-race-conditions-using-f), as well as slightly faster by expressing
the update relative to the original field value, rather than as an explicit
assignment of a new value. Django provides [F() expressions](expressions.md#f-expressions) for performing
this kind of relative update. Using [F() expressions](expressions.md#f-expressions), the previous example
is expressed as:

```pycon
>>> from django.db.models import F
>>> product = Product.objects.get(name="Venezuelan Beaver Cheese")
>>> product.number_sold = F("number_sold") + 1
>>> product.save()
```

For more details, see the documentation on [F() expressions](expressions.md#f-expressions) and their
[use in update queries](../../topics/db/queries.md#topics-db-queries-update).

<a id="ref-models-update-fields"></a>

### Specifying which fields to save

If `save()` is passed a list of field names in keyword argument
`update_fields`, only the fields named in that list will be updated.
This may be desirable if you want to update just one or a few fields on
an object. There will be a slight performance benefit from preventing
all of the model fields from being updated in the database. For example:

```default
product.name = "Name changed again"
product.save(update_fields=["name"])
```

The `update_fields` argument can be any iterable containing strings. An
empty `update_fields` iterable will skip the save. A value of `None` will
perform an update on all fields.

Specifying `update_fields` will force an update.

When saving a model fetched through deferred model loading
([`only()`](querysets.md#django.db.models.query.QuerySet.only) or
[`defer()`](querysets.md#django.db.models.query.QuerySet.defer)) only the fields loaded
from the DB will get updated. In effect there is an automatic
`update_fields` in this case. If you assign or change any deferred field
value, the field will be added to the updated fields.

## Deleting objects

#### Model.delete(using=DEFAULT_DB_ALIAS, keep_parents=False)

#### Model.adelete(using=DEFAULT_DB_ALIAS, keep_parents=False)

*Asynchronous version*: `adelete()`

Issues an SQL `DELETE` for the object. This only deletes the object in the
database; the Python instance will still exist and will still have data in
its fields, except for the primary key set to `None`. This method returns the
number of objects deleted and a dictionary with the number of deletions per
object type. The return value will count instances from related models if
Django is emulating cascade behavior via Python [`on_delete`](fields.md#django.db.models.ForeignKey.on_delete)
variants. Otherwise, for database variants such as
[`DB_CASCADE`](fields.md#django.db.models.DB_CASCADE), the return value will report only
instances of the [`QuerySet`](querysets.md#django.db.models.query.QuerySet)’s model.

For more details, including how to delete objects in bulk, see
[Deleting objects](../../topics/db/queries.md#topics-db-queries-delete).

If you want customized deletion behavior, you can override the `delete()`
method. See [Overriding predefined model methods](../../topics/db/models.md#overriding-model-methods) for more details.

Sometimes with [multi-table inheritance](../../topics/db/models.md#multi-table-inheritance) you may
want to delete only a child model’s data. Specifying `keep_parents=True` will
keep the parent model’s data.

#### Versionchanged
Support for the `DB_*` variants of `on_delete` attribute was added.

## Pickling objects

When you [`pickle`](https://docs.python.org/3/library/pickle.html#module-pickle) a model, its current state is pickled. When you unpickle
it, it’ll contain the model instance at the moment it was pickled, rather than
the data that’s currently in the database.

<a id="model-instance-methods"></a>

## Other model instance methods

A few object methods have special purposes.

### `__str__()`

#### Model.\_\_str_\_()

The `__str__()` method is called whenever you call `str()` on an object.
Django uses `str(obj)` in a number of places. Most notably, to display an
object in the Django admin site and as the value inserted into a template when
it displays an object. Thus, you should always return a nice, human-readable
representation of the model from the `__str__()` method.

For example:

```default
from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
```

### `__eq__()`

#### Model.\_\_eq_\_()

The equality method is defined such that instances with the same primary
key value and the same concrete class are considered equal, except that
instances with a primary key value of `None` aren’t equal to anything except
themselves. For proxy models, concrete class is defined as the model’s first
non-proxy parent; for all other models it’s simply the model’s class.

For example:

```default
from django.db import models


class MyModel(models.Model):
    id = models.AutoField(primary_key=True)


class MyProxyModel(MyModel):
    class Meta:
        proxy = True


class MultitableInherited(MyModel):
    pass


# Primary keys compared
MyModel(id=1) == MyModel(id=1)
MyModel(id=1) != MyModel(id=2)
# Primary keys are None
MyModel(id=None) != MyModel(id=None)
# Same instance
instance = MyModel(id=None)
instance == instance
# Proxy model
MyModel(id=1) == MyProxyModel(id=1)
# Multi-table inheritance
MyModel(id=1) != MultitableInherited(id=1)
```

### `__hash__()`

#### Model.\_\_hash_\_()

The `__hash__()` method is based on the instance’s primary key value. It
is effectively `hash(obj.pk)`. If the instance doesn’t have a primary key
value then a `TypeError` will be raised (otherwise the `__hash__()`
method would return different values before and after the instance is
saved, but changing the [`__hash__()`](https://docs.python.org/3/reference/datamodel.html#object.__hash__) value of an instance is
forbidden in Python.

### `get_absolute_url()`

#### Model.get_absolute_url()

Define a `get_absolute_url()` method to tell Django how to calculate the
canonical URL for an object. To callers, this method should appear to return a
string that can be used to refer to the object over HTTP.

For example:

```default
def get_absolute_url(self):
    return "/people/%i/" % self.id
```

While this code is correct and simple, it may not be the most portable way to
to write this kind of method. The [`reverse()`](../urlresolvers.md#django.urls.reverse) function is
usually the best approach.

For example:

```default
def get_absolute_url(self):
    from django.urls import reverse

    return reverse("people-detail", kwargs={"pk": self.pk})
```

One place Django uses `get_absolute_url()` is in the admin app. If an object
defines this method, the object-editing page will have a “View on site” link
that will jump you directly to the object’s public view, as given by
`get_absolute_url()`.

Similarly, a couple of other bits of Django, such as the [syndication feed
framework](../contrib/syndication.md), use `get_absolute_url()` when it is
defined. If it makes sense for your model’s instances to each have a unique
URL, you should define `get_absolute_url()`.

#### WARNING
You should avoid building the URL from unvalidated user input, in order to
reduce possibilities of link or redirect poisoning:

```default
def get_absolute_url(self):
    return "/%s/" % self.name
```

If `self.name` is `'/example.com'` this returns `'//example.com/'`
which, in turn, is a valid schema relative URL but not the expected
`'/%2Fexample.com/'`.

It’s good practice to use `get_absolute_url()` in templates, instead of
hardcoding your objects’ URLs. For example, this template code is bad:

```html+django
<!-- BAD template code. Avoid! -->
<a href="/people/{{ object.id }}/">{{ object.name }}</a>
```

This template code is much better:

```html+django
<a href="{{ object.get_absolute_url }}">{{ object.name }}</a>
```

The logic here is that if you change the URL structure of your objects, even
for something small like correcting a spelling error, you don’t want to have to
track down every place that the URL might be created. Specify it once, in
`get_absolute_url()` and have all your other code call that one place.

#### NOTE
The string you return from `get_absolute_url()` **must** contain only
ASCII characters (required by the URI specification, [**RFC 3986 Section 2**](https://datatracker.ietf.org/doc/html/rfc3986.html#section-2))
and be URL-encoded, if necessary.

Code and templates calling `get_absolute_url()` should be able to use the
result directly without any further processing. You may wish to use the
`django.utils.encoding.iri_to_uri()` function to help with this if you
are using strings containing characters outside the ASCII range.

## Extra instance methods

In addition to [`save()`](#django.db.models.Model.save), [`delete()`](#django.db.models.Model.delete), a model object
might have some of the following methods:

#### Model.get_FOO_display()

For every field that has [`choices`](fields.md#django.db.models.Field.choices) set, the
object will have a `get_FOO_display()` method, where `FOO` is the name of
the field. This method returns the “human-readable” value of the field.

For example:

```default
from django.db import models


class Person(models.Model):
    SHIRT_SIZES = {
        "S": "Small",
        "M": "Medium",
        "L": "Large",
    }
    name = models.CharField(max_length=60)
    shirt_size = models.CharField(max_length=2, choices=SHIRT_SIZES)
```

```pycon
>>> p = Person(name="Fred Flintstone", shirt_size="L")
>>> p.save()
>>> p.shirt_size
'L'
>>> p.get_shirt_size_display()
'Large'
```

#### Model.get_next_by_FOO(\*\*kwargs)

#### Model.get_previous_by_FOO(\*\*kwargs)

For every [`DateField`](fields.md#django.db.models.DateField) and
[`DateTimeField`](fields.md#django.db.models.DateTimeField) that does not have [`null=True`](fields.md#django.db.models.Field.null), the object will have `get_next_by_FOO()` and
`get_previous_by_FOO()` methods, where `FOO` is the name of the field. This
returns the next and previous object with respect to the date field, raising
a [`DoesNotExist`](class.md#django.db.models.Model.DoesNotExist) exception when appropriate.

Both of these methods will perform their queries using the default
manager for the model. If you need to emulate filtering used by a
custom manager, or want to perform one-off custom filtering, both
methods also accept optional keyword arguments, which should be in the
format described in [Field lookups](querysets.md#field-lookups).

Note that in the case of identical date values, these methods will use the
primary key as a tie-breaker. This guarantees that no records are skipped or
duplicated. That also means you cannot use those methods on unsaved objects.

## Other attributes

### `_state`

#### Model.\_state

The `_state` attribute refers to a `ModelState` object that tracks
the lifecycle of the model instance.

The `ModelState` object has two attributes: `adding`, a flag which is
`True` if the model has not been saved to the database yet, and `db`,
a string referring to the database alias the instance was loaded from or
saved to.

Newly instantiated instances have `adding=True` and `db=None`,
since they are yet to be saved. Instances fetched from a `QuerySet`
will have `adding=False` and `db` set to the alias of the associated
database.

### `_is_pk_set()`

#### Model.\_is_pk_set()

The `_is_pk_set()` method returns whether the model instance’s `pk` is set.
It abstracts the model’s primary key definition, ensuring consistent behavior
regardless of the specific `pk` configuration.

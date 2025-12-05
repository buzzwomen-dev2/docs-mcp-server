# Model class reference

This document covers features of the [`Model`](instances.md#django.db.models.Model) class.
For more information about models, see [the complete list of Model
reference guides](index.md).

## Attributes

### `DoesNotExist`

#### *exception* Model.DoesNotExist

This exception is raised by the ORM when an expected object is not found.
For example, [`QuerySet.get()`](querysets.md#django.db.models.query.QuerySet.get) will raise it when no object is found
for the given lookups.

Django provides a `DoesNotExist` exception as an attribute of each model
class to identify the class of object that could not be found, allowing you
to catch exceptions for a particular model class. The exception is a
subclass of [`django.core.exceptions.ObjectDoesNotExist`](../exceptions.md#django.core.exceptions.ObjectDoesNotExist).

### `MultipleObjectsReturned`

#### *exception* Model.MultipleObjectsReturned

This exception is raised by [`QuerySet.get()`](querysets.md#django.db.models.query.QuerySet.get) when multiple objects are
found for the given lookups.

Django provides a `MultipleObjectsReturned` exception as an attribute of
each model class to identify the class of object for which multiple objects
were found, allowing you to catch exceptions for a particular model class.
The exception is a subclass of
[`django.core.exceptions.MultipleObjectsReturned`](../exceptions.md#django.core.exceptions.MultipleObjectsReturned).

### `NotUpdated`

#### Versionadded

#### *exception* Model.NotUpdated

This exception is raised when [a forced update](instances.md#ref-models-force-insert) of a [`Model`](instances.md#django.db.models.Model) instance
does not affect any rows.

Django provides a `NotUpdated` exception as an attribute of each model
class to identify the class of object that could not be updated, allowing
you to catch exceptions for a particular model class. The exception is a
subclass of [`django.core.exceptions.ObjectNotUpdated`](../exceptions.md#django.core.exceptions.ObjectNotUpdated) and inherits
from [`django.db.DatabaseError`](../exceptions.md#django.db.DatabaseError) for backward compatibility reasons.

### `objects`

#### Model.objects

Each non-abstract [`Model`](instances.md#django.db.models.Model) class must have a
[`Manager`](../../topics/db/managers.md#django.db.models.Manager) instance added to it.
Django ensures that in your model class you have  at least a
default `Manager` specified. If you don’t add your own `Manager`,
Django will add an attribute `objects` containing default
[`Manager`](../../topics/db/managers.md#django.db.models.Manager) instance. If you add your own
[`Manager`](../../topics/db/managers.md#django.db.models.Manager) instance attribute, the default one does
not appear. Consider the following example:

```default
from django.db import models


class Person(models.Model):
    # Add manager with another name
    people = models.Manager()
```

For more details on model managers see [Managers](../../topics/db/managers.md) and [Retrieving objects](../../topics/db/queries.md#retrieving-objects).

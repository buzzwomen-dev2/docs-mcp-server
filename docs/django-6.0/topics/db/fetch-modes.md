# Fetch modes

#### Versionadded

<a id="module-django.db.models.fetch_modes"></a>

When accessing model fields that were not loaded as part of the original query,
Django will fetch that field’s data from the database. You can customize the
behavior of this fetching with a **fetch mode**, making it more efficient or
even blocking it.

Use [`QuerySet.fetch_mode()`](../../ref/models/querysets.md#django.db.models.query.QuerySet.fetch_mode) to set the fetch mode for model
instances fetched by a `QuerySet`:

```python
from django.db import models

books = Book.objects.fetch_mode(models.FETCH_PEERS)
```

Fetch modes apply to:

* [`ForeignKey`](../../ref/models/fields.md#django.db.models.ForeignKey) fields
* [`OneToOneField`](../../ref/models/fields.md#django.db.models.OneToOneField) fields and their reverse accessors
* Fields deferred with [`QuerySet.defer()`](../../ref/models/querysets.md#django.db.models.query.QuerySet.defer) or [`QuerySet.only()`](../../ref/models/querysets.md#django.db.models.query.QuerySet.only)
* [Generic relations](../../ref/contrib/contenttypes.md#generic-relations)

Django copies the fetch mode of an instance to any related objects it fetches,
so the mode applies to a whole tree of relationships, not just the top-level
model in the initial `QuerySet`. This copying is also done in related
managers, even though fetch modes don’t affect such managers’ queries.

## Available modes

Django provides three fetch modes. We’ll explain them below using these models:

```python
from django.db import models


class Author(models.Model): ...


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    ...
```

…and this loop:

```python
for book in books:
    print(book.author.name)
```

…where `books` is a `QuerySet` of `Book` instances using some fetch mode.

### FETCH_ONE

Fetches the missing field for the current instance only. This is the default
mode.

Using `FETCH_ONE` for the above example would use:

* 1 query to fetch `books`
* N queries, where N is the number of books, to fetch the missing `author`
  field

…for a total of 1+N queries. This query pattern is known as the “N+1 queries
problem” because it often leads to performance issues when N is large.

### FETCH_PEERS

Fetches the missing field for the current instance and its “peers”—instances
that came from the same initial `QuerySet`. The behavior of this mode is
based on the assumption that if you need a field for one instance, you probably
need it for all instances in the same batch, since you’ll likely process them
all identically.

Using `FETCH_PEERS` for the above example would use:

* 1 query to fetch `books`
* 1 query to fetch all missing `author` fields for the batch of books

…for a total of 2 queries. The batch query makes this mode a lot more efficient
than `FETCH_ONE` and is similar to an on-demand call to
[`QuerySet.prefetch_related()`](../../ref/models/querysets.md#django.db.models.query.QuerySet.prefetch_related) or
[`prefetch_related_objects()`](../../ref/models/querysets.md#django.db.models.prefetch_related_objects). Using `FETCH_PEERS` can
reduce most cases of the “N+1 queries problem” to two queries without
much effort.

The “peer” instances are tracked in a list of weak references, to avoid
memory leaks where some peer instances are discarded.

### RAISE

Raises a [`FieldFetchBlocked`](../../ref/exceptions.md#django.core.exceptions.FieldFetchBlocked) exception.

Using `RAISE` for the above example would raise an exception at the access of
`book.author` access, like:

```python
FieldFetchBlocked("Fetching of Primary.value blocked.")
```

This mode can prevent unintentional queries in performance-critical
sections of code.

<a id="fetch-modes-custom-manager"></a>

## Make a fetch mode the default for a model class

Set the default fetch mode for a model class with a
[custom manager](managers.md#custom-managers) that overrides `get_queryset()`:

```python
from django.db import models


class BookManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().fetch_mode(models.FETCH_PEERS)


class Book(models.Model):
    title = models.TextField()
    author = models.ForeignKey("Author", on_delete=models.CASCADE)

    objects = BookManager()
```

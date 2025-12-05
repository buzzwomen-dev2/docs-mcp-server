# PostgreSQL specific query expressions

These expressions are available from the
`django.contrib.postgres.expressions` module.

## `ArraySubquery()` expressions

### *class* ArraySubquery(queryset)

`ArraySubquery` is a [`Subquery`](../../models/expressions.md#django.db.models.Subquery) that uses the
PostgreSQL `ARRAY` constructor to build a list of values from the queryset,
which must use [`QuerySet.values()`](../../models/querysets.md#django.db.models.query.QuerySet.values) to return only a single column.

This class differs from [`ArrayAgg`](aggregates.md#django.contrib.postgres.aggregates.ArrayAgg)
in the way that it does not act as an aggregate function and does not require
an SQL `GROUP BY` clause to build the list of values.

For example, if you want to annotate all related books to an author as JSON
objects:

```pycon
>>> from django.db.models import OuterRef
>>> from django.db.models.functions import JSONObject
>>> from django.contrib.postgres.expressions import ArraySubquery
>>> books = Book.objects.filter(author=OuterRef("pk")).values(
...     json=JSONObject(title="title", pages="pages")
... )
>>> author = Author.objects.annotate(books=ArraySubquery(books)).first()
>>> author.books
[{'title': 'Solaris', 'pages': 204}, {'title': 'The Cyberiad', 'pages': 295}]
```

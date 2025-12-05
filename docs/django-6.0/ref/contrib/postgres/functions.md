# PostgreSQL specific database functions

All of these functions are available from the
`django.contrib.postgres.functions` module.

## `RandomUUID`

### *class* RandomUUID

Returns a version 4 UUID.

Usage example:

```pycon
>>> from django.contrib.postgres.functions import RandomUUID
>>> Article.objects.update(uuid=RandomUUID())
```

## `TransactionNow`

### *class* TransactionNow

Returns the date and time on the database server that the current transaction
started. If you are not in a transaction it will return the date and time of
the current statement. This is a complement to
[`django.db.models.functions.Now`](../../models/database-functions.md#django.db.models.functions.Now), which returns the date and time of the
current statement.

Note that only the outermost call to [`atomic()`](../../../topics/db/transactions.md#django.db.transaction.atomic)
sets up a transaction and thus sets the time that `TransactionNow()` will
return; nested calls create savepoints which do not affect the transaction
time.

Usage example:

```pycon
>>> from django.contrib.postgres.functions import TransactionNow
>>> Article.objects.filter(published__lte=TransactionNow())
<QuerySet [<Article: How to Django>]>
```

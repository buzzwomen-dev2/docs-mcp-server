# PostgreSQL specific lookups

## Trigram similarity

<a id="std-fieldlookup-trigram_similar"></a>

### `trigram_similar`

The `trigram_similar` lookup allows you to perform trigram lookups,
measuring the number of trigrams (three consecutive characters) shared, using a
dedicated PostgreSQL extension. A trigram lookup is given an expression and
returns results that have a similarity measurement greater than the current
similarity threshold.

To use it, add `'django.contrib.postgres'` in your [`INSTALLED_APPS`](../../settings.md#std-setting-INSTALLED_APPS)
and activate the [pg_trgm extension](https://www.postgresql.org/docs/current/pgtrgm.html) on PostgreSQL. You can install the
extension using the
[`TrigramExtension`](operations.md#django.contrib.postgres.operations.TrigramExtension) migration
operation.

The `trigram_similar` lookup can be used on
[`CharField`](../../models/fields.md#django.db.models.CharField) and [`TextField`](../../models/fields.md#django.db.models.TextField):

```pycon
>>> City.objects.filter(name__trigram_similar="Middlesborough")
['<City: Middlesbrough>']
```

<a id="std-fieldlookup-trigram_word_similar"></a>

### `trigram_word_similar`

The `trigram_word_similar` lookup allows you to perform trigram word
similarity lookups using a dedicated PostgreSQL extension. It can be
approximately understood as measuring the greatest number of trigrams shared
between the parameter and any substring of the field. A trigram word lookup is
given an expression and returns results that have a word similarity measurement
greater than the current similarity threshold.

To use it, add `'django.contrib.postgres'` in your [`INSTALLED_APPS`](../../settings.md#std-setting-INSTALLED_APPS)
and activate the [pg_trgm extension](https://www.postgresql.org/docs/current/pgtrgm.html) on PostgreSQL. You can install the
extension using the
[`TrigramExtension`](operations.md#django.contrib.postgres.operations.TrigramExtension) migration
operation.

The `trigram_word_similar` lookup can be used on
[`CharField`](../../models/fields.md#django.db.models.CharField) and [`TextField`](../../models/fields.md#django.db.models.TextField):

```pycon
>>> Sentence.objects.filter(name__trigram_word_similar="Middlesborough")
['<Sentence: Gumby rides on the path of Middlesbrough>']
```

<a id="std-fieldlookup-trigram_strict_word_similar"></a>

### `trigram_strict_word_similar`

Similar to [`trigram_word_similar`](#std-fieldlookup-trigram_word_similar), except that it forces extent
boundaries to match word boundaries.

To use it, add `'django.contrib.postgres'` in your [`INSTALLED_APPS`](../../settings.md#std-setting-INSTALLED_APPS)
and activate the [pg_trgm extension](https://www.postgresql.org/docs/current/pgtrgm.html) on PostgreSQL. You can install the
extension using the
[`TrigramExtension`](operations.md#django.contrib.postgres.operations.TrigramExtension) migration
operation.

The `trigram_strict_word_similar` lookup can be used on
[`CharField`](../../models/fields.md#django.db.models.CharField) and [`TextField`](../../models/fields.md#django.db.models.TextField).

## `Unaccent`

<a id="std-fieldlookup-unaccent"></a>

The `unaccent` lookup allows you to perform accent-insensitive lookups using
a dedicated PostgreSQL extension.

This lookup is implemented using [`Transform`](../../models/lookups.md#django.db.models.Transform), so it
can be chained with other lookup functions. To use it, you need to add
`'django.contrib.postgres'` in your [`INSTALLED_APPS`](../../settings.md#std-setting-INSTALLED_APPS) and activate
the [unaccent extension on PostgreSQL](https://www.postgresql.org/docs/current/unaccent.html). The
[`UnaccentExtension`](operations.md#django.contrib.postgres.operations.UnaccentExtension) migration
operation is available if you want to perform this activation using
migrations).

The `unaccent` lookup can be used on
[`CharField`](../../models/fields.md#django.db.models.CharField) and [`TextField`](../../models/fields.md#django.db.models.TextField):

```pycon
>>> City.objects.filter(name__unaccent="México")
['<City: Mexico>']

>>> User.objects.filter(first_name__unaccent__startswith="Jerem")
['<User: Jeremy>', '<User: Jérémy>', '<User: Jérémie>', '<User: Jeremie>']
```

#### WARNING
`unaccent` lookups should perform fine in most use cases. However,
queries using this filter will generally perform full table scans, which
can be slow on large tables. In those cases, using dedicated full text
indexing tools might be appropriate.

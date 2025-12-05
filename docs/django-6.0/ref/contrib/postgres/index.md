# `django.contrib.postgres`

PostgreSQL has a number of features which are not shared by the other databases
Django supports. This optional module contains model fields and form fields for
a number of PostgreSQL specific data types.

#### NOTE
Django is, and will continue to be, a database-agnostic web framework. We
would encourage those writing reusable applications for the Django
community to write database-agnostic code where practical. However, we
recognize that real world projects written using Django need not be
database-agnostic. In fact, once a project reaches a given size changing
the underlying data store is already a significant challenge and is likely
to require changing the code base in some ways to handle differences
between the data stores.

Django provides support for a number of data types which will
only work with PostgreSQL. There is no fundamental reason why (for example)
a `contrib.mysql` module does not exist, except that PostgreSQL has the
richest feature set of the supported databases so its users have the most
to gain.

* [PostgreSQL specific aggregation functions](aggregates.md)
  * [General-purpose aggregation functions](aggregates.md#general-purpose-aggregation-functions)
  * [Aggregate functions for statistics](aggregates.md#aggregate-functions-for-statistics)
  * [Usage examples](aggregates.md#usage-examples)
* [PostgreSQL specific database constraints](constraints.md)
  * [`ExclusionConstraint`](constraints.md#exclusionconstraint)
* [PostgreSQL specific query expressions](expressions.md)
  * [`ArraySubquery()` expressions](expressions.md#arraysubquery-expressions)
* [PostgreSQL specific model fields](fields.md)
  * [Indexing these fields](fields.md#indexing-these-fields)
  * [`ArrayField`](fields.md#arrayfield)
  * [`HStoreField`](fields.md#hstorefield)
  * [Range Fields](fields.md#range-fields)
* [PostgreSQL specific form fields and widgets](forms.md)
  * [Fields](forms.md#fields)
  * [Widgets](forms.md#widgets)
* [PostgreSQL specific database functions](functions.md)
  * [`RandomUUID`](functions.md#randomuuid)
  * [`TransactionNow`](functions.md#transactionnow)
* [PostgreSQL specific model indexes](indexes.md)
  * [`BloomIndex`](indexes.md#bloomindex)
  * [`BrinIndex`](indexes.md#brinindex)
  * [`BTreeIndex`](indexes.md#btreeindex)
  * [`GinIndex`](indexes.md#ginindex)
  * [`GistIndex`](indexes.md#gistindex)
  * [`HashIndex`](indexes.md#hashindex)
  * [`SpGistIndex`](indexes.md#spgistindex)
  * [`OpClass()` expressions](indexes.md#opclass-expressions)
* [PostgreSQL specific lookups](lookups.md)
  * [Trigram similarity](lookups.md#trigram-similarity)
  * [`Unaccent`](lookups.md#unaccent)
* [Database migration operations](operations.md)
  * [Creating extension using migrations](operations.md#creating-extension-using-migrations)
  * [`CreateExtension`](operations.md#createextension)
  * [`BloomExtension`](operations.md#bloomextension)
  * [`BtreeGinExtension`](operations.md#btreeginextension)
  * [`BtreeGistExtension`](operations.md#btreegistextension)
  * [`CITextExtension`](operations.md#citextextension)
  * [`CryptoExtension`](operations.md#cryptoextension)
  * [`HStoreExtension`](operations.md#hstoreextension)
  * [`TrigramExtension`](operations.md#trigramextension)
  * [`UnaccentExtension`](operations.md#unaccentextension)
  * [Managing collations using migrations](operations.md#managing-collations-using-migrations)
  * [Concurrent index operations](operations.md#concurrent-index-operations)
  * [Adding constraints without enforcing validation](operations.md#adding-constraints-without-enforcing-validation)
* [Full text search](search.md)
  * [The `search` lookup](search.md#the-search-lookup)
  * [`SearchVector`](search.md#searchvector)
  * [`SearchQuery`](search.md#searchquery)
  * [`SearchRank`](search.md#searchrank)
  * [`SearchHeadline`](search.md#searchheadline)
  * [Changing the search configuration](search.md#changing-the-search-configuration)
  * [Weighting queries](search.md#weighting-queries)
  * [`Lexeme`](search.md#lexeme)
  * [Performance](search.md#performance)
  * [Trigram similarity](search.md#trigram-similarity)
* [Validators](validators.md)
  * [`KeysValidator`](validators.md#keysvalidator)
  * [Range validators](validators.md#range-validators)

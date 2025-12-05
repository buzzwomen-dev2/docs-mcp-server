# `contrib` packages

Django aims to follow Python’s [“batteries included” philosophy](https://docs.python.org/3/tutorial/stdlib.html#tut-batteries-included). It ships with a variety of extra, optional tools
that solve common web development problems.

This code lives in [django/contrib](https://github.com/django/django/blob/main/django/contrib) in the Django distribution. This
document gives a rundown of the packages in `contrib`, along with any
dependencies those packages have.

* [The Django admin site](admin/index.md)
* [`django.contrib.auth`](auth.md)
* [The contenttypes framework](contenttypes.md)
* [The flatpages app](flatpages.md)
* [GeoDjango](gis/index.md)
* [`django.contrib.humanize`](humanize.md)
* [The messages framework](messages.md)
* [`django.contrib.postgres`](postgres/index.md)
* [The redirects app](redirects.md)
* [The sitemap framework](sitemaps.md)
* [The “sites” framework](sites.md)
* [The `staticfiles` app](staticfiles.md)
* [The syndication feed framework](syndication.md)

## `admin`

The automatic Django administrative interface. For more information, see
[Tutorial 2](../../intro/tutorial02.md) and the
[admin documentation](admin/index.md).

Requires the [auth]() and [contenttypes]() contrib packages to be installed.

## `auth`

Django’s authentication framework.

See [User authentication in Django](../../topics/auth/index.md).

## `contenttypes`

A light framework for hooking into “types” of content, where each installed
Django model is a separate content type.

See the [contenttypes documentation](contenttypes.md).

## `flatpages`

A framework for managing “flat” HTML content in a database.

See the [flatpages documentation](flatpages.md).

Requires the [sites]() contrib package to be installed as well.

## `gis`

A world-class geospatial framework built on top of Django, that enables
storage, manipulation and display of spatial data.

See the [GeoDjango](gis/index.md) documentation for more.

## `humanize`

A set of Django template filters useful for adding a “human touch” to data.

See the [humanize documentation](humanize.md).

## `messages`

A framework for storing and retrieving temporary cookie- or session-based
messages

See the [messages documentation](messages.md).

## `postgres`

A collection of PostgreSQL specific features.

See the [contrib.postgres documentation](postgres/index.md).

## `redirects`

A framework for managing redirects.

See the [redirects documentation](redirects.md).

## `sessions`

A framework for storing data in anonymous sessions.

See the [sessions documentation](../../topics/http/sessions.md).

## `sites`

A light framework that lets you operate multiple websites off of the same
database and Django installation. It gives you hooks for associating objects to
one or more sites.

See the [sites documentation](sites.md).

## `sitemaps`

A framework for generating Google sitemap XML files.

See the [sitemaps documentation](sitemaps.md).

## `syndication`

A framework for generating syndication feeds, in RSS and Atom, quite easily.

See the [syndication documentation](syndication.md).

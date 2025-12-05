# Settings

> * [Core Settings](#core-settings)
> * [Auth](#auth)
> * [Messages](#messages)
> * [Sessions](#sessions)
> * [Sites](#sites)
> * [Static Files](#static-files)
> * [Core Settings Topical Index](#core-settings-topical-index)

#### WARNING
Be careful when you override settings, especially when the default value
is a non-empty list or dictionary, such as [`STATICFILES_FINDERS`](#std-setting-STATICFILES_FINDERS).
Make sure you keep the components required by the features of Django you
wish to use.

## Core Settings

Here’s a list of settings available in Django core and their default values.
Settings provided by contrib apps are listed below, followed by a topical index
of the core settings. For introductory material, see the [settings topic
guide](../topics/settings.md).

<a id="std-setting-ABSOLUTE_URL_OVERRIDES"></a>

### `ABSOLUTE_URL_OVERRIDES`

Default: `{}` (Empty dictionary)

A dictionary mapping `"app_label.model_name"` strings to functions that take
a model object and return its URL. This is a way of inserting or overriding
`get_absolute_url()` methods on a per-installation basis. Example:

```default
ABSOLUTE_URL_OVERRIDES = {
    "blogs.blog": lambda o: "/blogs/%s/" % o.slug,
    "news.story": lambda o: "/stories/%s/%s/" % (o.pub_year, o.slug),
}
```

The model name used in this setting should be all lowercase, regardless of the
case of the actual model class name.

<a id="std-setting-ADMINS"></a>

### `ADMINS`

Default: `[]` (Empty list)

A list of all the people who get code error notifications. When
[`DEBUG=False`](#std-setting-DEBUG) and [`AdminEmailHandler`](logging.md#django.utils.log.AdminEmailHandler)
is configured in [`LOGGING`](#std-setting-LOGGING) (done by default), Django emails these
people the details of exceptions raised in the request/response cycle.

Each item in the list should be an email address string. Example:

```default
ADMINS = ["john@example.com", '"Ng, Mary" <mary@example.com>']
```

#### Versionchanged
In older versions, required a list of (name, address) tuples.

<a id="std-setting-ALLOWED_HOSTS"></a>

### `ALLOWED_HOSTS`

Default: `[]` (Empty list)

A list of strings representing the host/domain names that this Django site can
serve. This is a security measure to prevent [HTTP Host header attacks](../topics/security.md#host-headers-virtual-hosting), which are possible even under many
seemingly-safe web server configurations.

Values in this list can be fully qualified names (e.g. `'www.example.com'`),
in which case they will be matched against the request’s `Host` header
exactly (case-insensitive, not including port). A value beginning with a period
can be used as a subdomain wildcard: `'.example.com'` will match
`example.com`, `www.example.com`, and any other subdomain of
`example.com`. A value of `'*'` will match anything; in this case you are
responsible to provide your own validation of the `Host` header (perhaps in a
middleware; if so this middleware must be listed first in
[`MIDDLEWARE`](#std-setting-MIDDLEWARE)).

Django also allows the [fully qualified domain name (FQDN)](https://en.wikipedia.org/wiki/Fully_qualified_domain_name) of any entries.
Some browsers include a trailing dot in the `Host` header which Django
strips when performing host validation.

If the `Host` header (or `X-Forwarded-Host` if
[`USE_X_FORWARDED_HOST`](#std-setting-USE_X_FORWARDED_HOST) is enabled) does not match any value in this
list, the [`django.http.HttpRequest.get_host()`](request-response.md#django.http.HttpRequest.get_host) method will raise
[`SuspiciousOperation`](exceptions.md#django.core.exceptions.SuspiciousOperation).

When [`DEBUG`](#std-setting-DEBUG) is `True` and `ALLOWED_HOSTS` is empty, the host
is validated against `['.localhost', '127.0.0.1', '[::1]']`.

`ALLOWED_HOSTS` is also [checked when running tests](../topics/testing/advanced.md#topics-testing-advanced-multiple-hosts).

This validation only applies via [`get_host()`](request-response.md#django.http.HttpRequest.get_host);
if your code accesses the `Host` header directly from `request.META` you
are bypassing this security protection.

<a id="std-setting-APPEND_SLASH"></a>

### `APPEND_SLASH`

Default: `True`

When set to `True`, if the request URL does not match any of the patterns
in the URLconf and it doesn’t end in a slash, an HTTP redirect is issued to the
same URL with a slash appended. Note that the redirect may cause any data
submitted in a POST request to be lost.

The [`APPEND_SLASH`](#std-setting-APPEND_SLASH) setting is only used if
[`CommonMiddleware`](middleware.md#django.middleware.common.CommonMiddleware) is installed
(see [Middleware](../topics/http/middleware.md)). See also [`PREPEND_WWW`](#std-setting-PREPEND_WWW).

<a id="std-setting-CACHES"></a>

### `CACHES`

Default:

```default
{
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

A dictionary containing the settings for all caches to be used with
Django. It is a nested dictionary whose contents maps cache aliases
to a dictionary containing the options for an individual cache.

The [`CACHES`](#std-setting-CACHES) setting must configure a `default` cache;
any number of additional caches may also be specified. If you
are using a cache backend other than the local memory cache, or
you need to define multiple caches, other options will be required.
The following cache options are available.

<a id="std-setting-CACHES-BACKEND"></a>

#### `BACKEND`

Default: `''` (Empty string)

The cache backend to use. The built-in cache backends are:

* `'django.core.cache.backends.db.DatabaseCache'`
* `'django.core.cache.backends.dummy.DummyCache'`
* `'django.core.cache.backends.filebased.FileBasedCache'`
* `'django.core.cache.backends.locmem.LocMemCache'`
* `'django.core.cache.backends.memcached.PyMemcacheCache'`
* `'django.core.cache.backends.memcached.PyLibMCCache'`
* `'django.core.cache.backends.redis.RedisCache'`

You can use a cache backend that doesn’t ship with Django by setting
[`BACKEND`](#std-setting-CACHES-BACKEND) to a fully-qualified path of a cache
backend class (i.e. `mypackage.backends.whatever.WhateverCache`).

<a id="std-setting-CACHES-KEY_FUNCTION"></a>

#### `KEY_FUNCTION`

A string containing a dotted path to a function (or any callable) that defines
how to compose a prefix, version and key into a final cache key. The default
implementation is equivalent to the function:

```default
def make_key(key, key_prefix, version):
    return ":".join([key_prefix, str(version), key])
```

You may use any key function you want, as long as it has the same
argument signature.

See the [cache documentation](../topics/cache.md#cache-key-transformation) for more
information.

<a id="std-setting-CACHES-KEY_PREFIX"></a>

#### `KEY_PREFIX`

Default: `''` (Empty string)

A string that will be automatically included (prepended by default) to
all cache keys used by the Django server.

See the [cache documentation](../topics/cache.md#cache-key-prefixing) for more information.

<a id="std-setting-CACHES-LOCATION"></a>

#### `LOCATION`

Default: `''` (Empty string)

The location of the cache to use. This might be the directory for a
file system cache, a host and port for a memcache server, or an identifying
name for a local memory cache. e.g.:

```default
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/tmp/django_cache",
    }
}
```

<a id="std-setting-CACHES-OPTIONS"></a>

#### `OPTIONS`

Default: `None`

Extra parameters to pass to the cache backend. Available parameters
vary depending on your cache backend.

Some information on available parameters can be found in the
[cache arguments](../topics/cache.md#cache-arguments) documentation. For more information,
consult your backend module’s own documentation.

<a id="std-setting-CACHES-TIMEOUT"></a>

#### `TIMEOUT`

Default: `300`

The number of seconds before a cache entry is considered stale. If the value of
this setting is `None`, cache entries will not expire. A value of `0`
causes keys to immediately expire (effectively “don’t cache”).

<a id="std-setting-CACHES-VERSION"></a>

#### `VERSION`

Default: `1`

The default version number for cache keys generated by the Django server.

See the [cache documentation](../topics/cache.md#cache-versioning) for more information.

<a id="std-setting-CACHE_MIDDLEWARE_ALIAS"></a>

### `CACHE_MIDDLEWARE_ALIAS`

Default: `'default'`

The cache connection to use for the [cache middleware](../topics/cache.md#the-per-site-cache).

<a id="std-setting-CACHE_MIDDLEWARE_KEY_PREFIX"></a>

### `CACHE_MIDDLEWARE_KEY_PREFIX`

Default: `''` (Empty string)

A string which will be prefixed to the cache keys generated by the [cache
middleware](../topics/cache.md#the-per-site-cache). This prefix is combined with the
[`KEY_PREFIX`](#std-setting-CACHES-KEY_PREFIX) setting; it does not replace it.

See [Django’s cache framework](../topics/cache.md).

<a id="std-setting-CACHE_MIDDLEWARE_SECONDS"></a>

### `CACHE_MIDDLEWARE_SECONDS`

Default: `600`

The default integer number of seconds to cache a page for the
[cache middleware](../topics/cache.md#the-per-site-cache).

See [Django’s cache framework](../topics/cache.md).

<a id="settings-csrf"></a>

<a id="std-setting-CSRF_COOKIE_AGE"></a>

### `CSRF_COOKIE_AGE`

Default: `31449600` (approximately 1 year, in seconds)

The age of CSRF cookies, in seconds.

The reason for setting a long-lived expiration time is to avoid problems in
the case of a user closing a browser or bookmarking a page and then loading
that page from a browser cache. Without persistent cookies, the form submission
would fail in this case.

Some browsers (specifically Internet Explorer) can disallow the use of
persistent cookies or can have the indexes to the cookie jar corrupted on disk,
thereby causing CSRF protection checks to (sometimes intermittently) fail.
Change this setting to `None` to use session-based CSRF cookies, which
keep the cookies in-memory instead of on persistent storage.

<a id="std-setting-CSRF_COOKIE_DOMAIN"></a>

### `CSRF_COOKIE_DOMAIN`

Default: `None`

The domain to be used when setting the CSRF cookie. This can be useful for
easily allowing cross-subdomain requests to be excluded from the normal cross
site request forgery protection. It should be set to a string such as
`".example.com"` to allow a POST request from a form on one subdomain to be
accepted by a view served from another subdomain.

Please note that the presence of this setting does not imply that Django’s CSRF
protection is safe from cross-subdomain attacks by default - please see the
[CSRF limitations](csrf.md#csrf-limitations) section.

<a id="std-setting-CSRF_COOKIE_HTTPONLY"></a>

### `CSRF_COOKIE_HTTPONLY`

Default: `False`

Whether to use `HttpOnly` flag on the CSRF cookie. If this is set to
`True`, client-side JavaScript will not be able to access the CSRF cookie.

Designating the CSRF cookie as `HttpOnly` doesn’t offer any practical
protection because CSRF is only to protect against cross-domain attacks. If an
attacker can read the cookie via JavaScript, they’re already on the same domain
as far as the browser knows, so they can do anything they like anyway. (XSS is
a much bigger hole than CSRF.)

Although the setting offers little practical benefit, it’s sometimes required
by security auditors.

If you enable this and need to send the value of the CSRF token with an AJAX
request, your JavaScript must pull the value [from a hidden CSRF token
form input](../howto/csrf.md#acquiring-csrf-token-from-html) instead of [from the cookie](../howto/csrf.md#acquiring-csrf-token-from-cookie).

See [`SESSION_COOKIE_HTTPONLY`](#std-setting-SESSION_COOKIE_HTTPONLY) for details on `HttpOnly`.

<a id="std-setting-CSRF_COOKIE_NAME"></a>

### `CSRF_COOKIE_NAME`

Default: `'csrftoken'`

The name of the cookie to use for the CSRF authentication token. This can be
whatever you want (as long as it’s different from the other cookie names in
your application). See [Cross Site Request Forgery protection](csrf.md).

<a id="std-setting-CSRF_COOKIE_PATH"></a>

### `CSRF_COOKIE_PATH`

Default: `'/'`

The path set on the CSRF cookie. This should either match the URL path of your
Django installation or be a parent of that path.

This is useful if you have multiple Django instances running under the same
hostname. They can use different cookie paths, and each instance will only see
its own CSRF cookie.

<a id="std-setting-CSRF_COOKIE_SAMESITE"></a>

### `CSRF_COOKIE_SAMESITE`

Default: `'Lax'`

The value of the [SameSite](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value) flag on the CSRF cookie. This flag prevents the
cookie from being sent in cross-site requests.

See [`SESSION_COOKIE_SAMESITE`](#std-setting-SESSION_COOKIE_SAMESITE) for details about `SameSite`.

<a id="std-setting-CSRF_COOKIE_SECURE"></a>

### `CSRF_COOKIE_SECURE`

Default: `False`

Whether to use a secure cookie for the CSRF cookie. If this is set to `True`,
the cookie will be marked as “secure”, which means browsers may ensure that the
cookie is only sent with an HTTPS connection.

<a id="std-setting-CSRF_USE_SESSIONS"></a>

### `CSRF_USE_SESSIONS`

Default: `False`

Whether to store the CSRF token in the user’s session instead of in a cookie.
It requires the use of [`django.contrib.sessions`](../topics/http/sessions.md#module-django.contrib.sessions).

Storing the CSRF token in a cookie (Django’s default) is safe, but storing it
in the session is common practice in other web frameworks and therefore
sometimes demanded by security auditors.

Since the [default error views](views.md#error-views) require the CSRF token,
[`SessionMiddleware`](middleware.md#django.contrib.sessions.middleware.SessionMiddleware) must appear in
[`MIDDLEWARE`](#std-setting-MIDDLEWARE) before any middleware that may raise an exception to
trigger an error view (such as [`PermissionDenied`](exceptions.md#django.core.exceptions.PermissionDenied))
if you’re using `CSRF_USE_SESSIONS`. See [Middleware ordering](middleware.md#middleware-ordering).

<a id="std-setting-CSRF_FAILURE_VIEW"></a>

### `CSRF_FAILURE_VIEW`

Default: `'django.views.csrf.csrf_failure'`

A dotted path to the view function to be used when an incoming request is
rejected by the [CSRF protection](csrf.md). The function should have
this signature:

```default
def csrf_failure(request, reason=""): ...
```

where `reason` is a short message (intended for developers or logging, not
for end users) indicating the reason the request was rejected. It should return
an [`HttpResponseForbidden`](request-response.md#django.http.HttpResponseForbidden).

`django.views.csrf.csrf_failure()` accepts an additional `template_name`
parameter that defaults to `'403_csrf.html'`. If a template with that name
exists, it will be used to render the page.

<a id="std-setting-CSRF_HEADER_NAME"></a>

### `CSRF_HEADER_NAME`

Default: `'HTTP_X_CSRFTOKEN'`

The name of the request header used for CSRF authentication.

As with other HTTP headers in `request.META`, the header name received from
the server is normalized by converting all characters to uppercase, replacing
any hyphens with underscores, and adding an `'HTTP_'` prefix to the name.
For example, if your client sends a `'X-XSRF-TOKEN'` header, the setting
should be `'HTTP_X_XSRF_TOKEN'`.

<a id="std-setting-CSRF_TRUSTED_ORIGINS"></a>

### `CSRF_TRUSTED_ORIGINS`

Default: `[]` (Empty list)

A list of trusted origins for unsafe requests (e.g. `POST`).

For requests that include the `Origin` header, Django’s CSRF protection
requires that header match the origin present in the `Host` header.

For a secure (determined by [`is_secure()`](request-response.md#django.http.HttpRequest.is_secure)) unsafe
request that doesn’t include the `Origin` header, the request must include a
`Referer` header that matches the origin in the `Host` header.

These checks prevent, for example, a `POST` request from
`subdomain.example.com` from succeeding against `api.example.com`. If you
need cross-origin unsafe requests, continuing the example, add
`'https://subdomain.example.com'` to this list (and/or `http://...` if
requests originate from an insecure page).

The setting also supports subdomains, so you could add
`'https://*.example.com'`, for example, to allow access from all subdomains
of `example.com`.

<a id="std-setting-DATABASES"></a>

### `DATABASES`

Default: `{}` (Empty dictionary)

A dictionary containing the settings for all databases to be used with
Django. It is a nested dictionary whose contents map a database alias
to a dictionary containing the options for an individual database.

The [`DATABASES`](#std-setting-DATABASES) setting must configure a `default` database;
any number of additional databases may also be specified.

The simplest possible settings file is for a single-database setup using
SQLite. This can be configured using the following:

```default
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "mydatabase",
    }
}
```

When connecting to other database backends, such as MariaDB, MySQL, Oracle, or
PostgreSQL, additional connection parameters will be required. See
the [`ENGINE`](#std-setting-DATABASE-ENGINE) setting below on how to specify
other database types. This example is for PostgreSQL:

```default
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydatabase",
        "USER": "mydatabaseuser",
        "PASSWORD": "mypassword",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
```

The following inner options that may be required for more complex
configurations are available:

<a id="std-setting-DATABASE-ATOMIC_REQUESTS"></a>

#### `ATOMIC_REQUESTS`

Default: `False`

Set this to `True` to wrap each view in a transaction on this database. See
[Tying transactions to HTTP requests](../topics/db/transactions.md#tying-transactions-to-http-requests).

<a id="std-setting-DATABASE-AUTOCOMMIT"></a>

#### `AUTOCOMMIT`

Default: `True`

Set this to `False` if you want to [disable Django’s transaction
management](../topics/db/transactions.md#deactivate-transaction-management) and implement your own.

<a id="std-setting-DATABASE-ENGINE"></a>

#### `ENGINE`

Default: `''` (Empty string)

The database backend to use. The built-in database backends are:

* `'django.db.backends.postgresql'`
* `'django.db.backends.mysql'`
* `'django.db.backends.sqlite3'`
* `'django.db.backends.oracle'`

You can use a database backend that doesn’t ship with Django by setting
`ENGINE` to a fully-qualified path (i.e. `mypackage.backends.whatever`).

<a id="std-setting-HOST"></a>

#### `HOST`

Default: `''` (Empty string)

Which host to use when connecting to the database. An empty string means
localhost. Not used with SQLite.

If this value starts with a forward slash (`'/'`) and you’re using MySQL,
MySQL will connect via a Unix socket to the specified socket. For example:

```default
"HOST": "/var/run/mysql"
```

If you’re using MySQL and this value *doesn’t* start with a forward slash, then
this value is assumed to be the host.

If you’re using PostgreSQL, by default (empty [`HOST`](#std-setting-HOST)), the connection
to the database is done through UNIX domain sockets (‘local’ lines in
`pg_hba.conf`). If your UNIX domain socket is not in the standard location,
use the same value of `unix_socket_directory` from `postgresql.conf`.
If you want to connect through TCP sockets, set [`HOST`](#std-setting-HOST) to ‘localhost’
or ‘127.0.0.1’ (‘host’ lines in `pg_hba.conf`).
On Windows, you should always define [`HOST`](#std-setting-HOST), as UNIX domain sockets
are not available.

<a id="std-setting-NAME"></a>

#### `NAME`

Default: `''` (Empty string)

The name of the database to use. For SQLite, it’s the full path to the database
file. When specifying the path, always use forward slashes, even on Windows
(e.g. `C:/homes/user/mysite/sqlite3.db`).

<a id="std-setting-CONN_MAX_AGE"></a>

#### `CONN_MAX_AGE`

Default: `0`

The lifetime of a database connection, as an integer of seconds. Use `0` to
close database connections at the end of each request — Django’s historical
behavior — and `None` for unlimited [persistent database connections](databases.md#persistent-database-connections).

<a id="std-setting-CONN_HEALTH_CHECKS"></a>

#### `CONN_HEALTH_CHECKS`

Default: `False`

If set to `True`, existing [persistent database connections](databases.md#persistent-database-connections) will be health checked before they are
reused in each request performing database access. If the health check fails,
the connection will be reestablished without failing the request when the
connection is no longer usable but the database server is ready to accept and
serve new connections (e.g. after database server restart closing existing
connections).

<a id="std-setting-OPTIONS"></a>

#### `OPTIONS`

Default: `{}` (Empty dictionary)

Extra parameters to use when connecting to the database. Available parameters
vary depending on your database backend.

Some information on available parameters can be found in the
[Database Backends](databases.md) documentation. For more information,
consult your backend module’s own documentation.

<a id="std-setting-PASSWORD"></a>

#### `PASSWORD`

Default: `''` (Empty string)

The password to use when connecting to the database. Not used with SQLite.

<a id="std-setting-PORT"></a>

#### `PORT`

Default: `''` (Empty string)

The port to use when connecting to the database. An empty string means the
default port. Not used with SQLite.

<a id="std-setting-DATABASE-TIME_ZONE"></a>

#### `TIME_ZONE`

Default: `None`

A string representing the time zone for this database connection or `None`.
This inner option of the [`DATABASES`](#std-setting-DATABASES) setting accepts the same values
as the general [`TIME_ZONE`](#std-setting-TIME_ZONE) setting.

When [`USE_TZ`](#std-setting-USE_TZ) is `True`, reading datetimes from the database
returns aware datetimes with the timezone set to this option’s value if not
`None`, or to UTC otherwise.

When [`USE_TZ`](#std-setting-USE_TZ) is `False`, it is an error to set this option.

* If the database backend doesn’t support time zones (e.g. SQLite, MySQL,
  Oracle), Django reads and writes datetimes in local time according to this
  option if it is set and in UTC if it isn’t.

  Changing the connection time zone changes how datetimes are read from and
  written to the database.
  * If Django manages the database and you don’t have a strong reason to do
    otherwise, you should leave this option unset. It’s best to store datetimes
    in UTC because it avoids ambiguous or nonexistent datetimes during daylight
    saving time changes. Also, receiving datetimes in UTC keeps datetime
    arithmetic simple — there’s no need to consider potential offset changes
    over a DST transition.
  * If you’re connecting to a third-party database that stores datetimes in a
    local time rather than UTC, then you must set this option to the
    appropriate time zone. Likewise, if Django manages the database but
    third-party systems connect to the same database and expect to find
    datetimes in local time, then you must set this option.
* If the database backend supports time zones (e.g., PostgreSQL), then the
  database connection’s time zone is set to this value.

  Although setting the `TIME_ZONE` option is very rarely needed, there are
  situations where it becomes necessary. Specifically, it’s recommended to
  match the general [`TIME_ZONE`](#std-setting-TIME_ZONE) setting when dealing with raw queries
  involving date/time functions like PostgreSQL’s `date_trunc()` or
  `generate_series()`, especially when generating time-based series that
  transition daylight savings.

  This value can be changed at any time, the database will handle the
  conversion of datetimes to the configured time zone.

  However, this has a downside: receiving all datetimes in local time makes
  datetime arithmetic more tricky — you must account for possible offset
  changes over DST transitions.

  Consider converting to local time explicitly with `AT TIME ZONE` in raw SQL
  queries instead of setting the `TIME_ZONE` option.

<a id="std-setting-DATABASE-DISABLE_SERVER_SIDE_CURSORS"></a>

#### `DISABLE_SERVER_SIDE_CURSORS`

Default: `False`

Set this to `True` if you want to disable the use of server-side cursors with
[`QuerySet.iterator()`](models/querysets.md#django.db.models.query.QuerySet.iterator). [Transaction pooling and server-side cursors](databases.md#transaction-pooling-server-side-cursors)
describes the use case.

This is a PostgreSQL-specific setting.

<a id="std-setting-USER"></a>

#### `USER`

Default: `''` (Empty string)

The username to use when connecting to the database. Not used with SQLite.

<a id="std-setting-DATABASE-TEST"></a>

#### `TEST`

Default: `{}` (Empty dictionary)

A dictionary of settings for test databases; for more details about the
creation and use of test databases, see [The test database](../topics/testing/overview.md#the-test-database).

Here’s an example with a test database configuration:

```default
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": "mydatabaseuser",
        "NAME": "mydatabase",
        "TEST": {
            "NAME": "mytestdatabase",
        },
    },
}
```

The following keys in the `TEST` dictionary are available:

<a id="std-setting-TEST_CHARSET"></a>

##### `CHARSET`

Default: `None`

The character set encoding used to create the test database. The value of this
string is passed directly through to the database, so its format is
backend-specific.

Supported by the [PostgreSQL](https://www.postgresql.org/docs/current/multibyte.html) (`postgresql`) and [MySQL](https://dev.mysql.com/doc/refman/en/charset-charsets.html) (`mysql`) backends.

<a id="std-setting-TEST_COLLATION"></a>

##### `COLLATION`

Default: `None`

The collation order to use when creating the test database. This value is
passed directly to the backend, so its format is backend-specific.

Only supported for the `mysql` backend (see the [MySQL manual](https://dev.mysql.com/doc/refman/en/charset-charsets.html) for details).

<a id="std-setting-TEST_DEPENDENCIES"></a>

##### `DEPENDENCIES`

Default: `['default']`, for all databases other than `default`,
which has no dependencies.

The creation-order dependencies of the database. See the documentation
on [controlling the creation order of test databases](../topics/testing/advanced.md#topics-testing-creation-dependencies) for details.

<a id="std-setting-TEST_MIGRATE"></a>

##### `MIGRATE`

Default: `True`

When set to `False`, migrations won’t run when creating the test database.
This is similar to setting `None` as a value in [`MIGRATION_MODULES`](#std-setting-MIGRATION_MODULES),
but for all apps.

<a id="std-setting-TEST_MIRROR"></a>

##### `MIRROR`

Default: `None`

The alias of the database that this database should mirror during
testing. It depends on transactions and therefore must be used within
[`TransactionTestCase`](../topics/testing/tools.md#django.test.TransactionTestCase) instead of
[`TestCase`](../topics/testing/tools.md#django.test.TestCase).

This setting exists to allow for testing of primary/replica
(referred to as master/slave by some databases)
configurations of multiple databases. See the documentation on
[testing primary/replica configurations](../topics/testing/advanced.md#topics-testing-primaryreplica) for details.

<a id="std-setting-TEST_NAME"></a>

##### `NAME`

Default: `None`

The name of database to use when running the test suite.

If the default value (`None`) is used with the SQLite database engine, the
tests will use a memory resident database. For all other database engines the
test database will use the name `'test_' + DATABASE_NAME`.

See [The test database](../topics/testing/overview.md#the-test-database).

<a id="std-setting-TEST_TEMPLATE"></a>

##### `TEMPLATE`

This is a PostgreSQL-specific setting.

The name of a [template](https://www.postgresql.org/docs/current/sql-createdatabase.html) (e.g. `'template0'`) from which to create the test
database.

<a id="std-setting-TEST_CREATE"></a>

##### `CREATE_DB`

Default: `True`

This is an Oracle-specific setting.

If it is set to `False`, the test tablespaces won’t be automatically created
at the beginning of the tests or dropped at the end.

<a id="std-setting-TEST_USER_CREATE"></a>

##### `CREATE_USER`

Default: `True`

This is an Oracle-specific setting.

If it is set to `False`, the test user won’t be automatically created at the
beginning of the tests and dropped at the end.

<a id="std-setting-TEST_USER"></a>

##### `USER`

Default: `None`

This is an Oracle-specific setting.

The username to use when connecting to the Oracle database that will be used
when running tests. If not provided, Django will use `'test_' + USER`.

<a id="std-setting-TEST_PASSWD"></a>

##### `PASSWORD`

Default: `None`

This is an Oracle-specific setting.

The password to use when connecting to the Oracle database that will be used
when running tests. If not provided, Django will generate a random password.

<a id="std-setting-TEST_ORACLE_MANAGED_FILES"></a>

##### `ORACLE_MANAGED_FILES`

Default: `False`

This is an Oracle-specific setting.

If set to `True`, Oracle Managed Files (OMF) tablespaces will be used.
[`DATAFILE`](#std-setting-DATAFILE) and [`DATAFILE_TMP`](#std-setting-DATAFILE_TMP) will be ignored.

<a id="std-setting-TEST_TBLSPACE"></a>

##### `TBLSPACE`

Default: `None`

This is an Oracle-specific setting.

The name of the tablespace that will be used when running tests. If not
provided, Django will use `'test_' + USER`.

<a id="std-setting-TEST_TBLSPACE_TMP"></a>

##### `TBLSPACE_TMP`

Default: `None`

This is an Oracle-specific setting.

The name of the temporary tablespace that will be used when running tests. If
not provided, Django will use `'test_' + USER + '_temp'`.

<a id="std-setting-DATAFILE"></a>

##### `DATAFILE`

Default: `None`

This is an Oracle-specific setting.

The name of the datafile to use for the TBLSPACE. If not provided, Django will
use `TBLSPACE + '.dbf'`.

<a id="std-setting-DATAFILE_TMP"></a>

##### `DATAFILE_TMP`

Default: `None`

This is an Oracle-specific setting.

The name of the datafile to use for the TBLSPACE_TMP. If not provided, Django
will use `TBLSPACE_TMP + '.dbf'`.

<a id="std-setting-DATAFILE_MAXSIZE"></a>

##### `DATAFILE_MAXSIZE`

Default: `'500M'`

This is an Oracle-specific setting.

The maximum size that the DATAFILE is allowed to grow to.

<a id="std-setting-DATAFILE_TMP_MAXSIZE"></a>

##### `DATAFILE_TMP_MAXSIZE`

Default: `'500M'`

This is an Oracle-specific setting.

The maximum size that the DATAFILE_TMP is allowed to grow to.

<a id="std-setting-DATAFILE_SIZE"></a>

##### `DATAFILE_SIZE`

Default: `'50M'`

This is an Oracle-specific setting.

The initial size of the DATAFILE.

<a id="std-setting-DATAFILE_TMP_SIZE"></a>

##### `DATAFILE_TMP_SIZE`

Default: `'50M'`

This is an Oracle-specific setting.

The initial size of the DATAFILE_TMP.

<a id="std-setting-DATAFILE_EXTSIZE"></a>

##### `DATAFILE_EXTSIZE`

Default: `'25M'`

This is an Oracle-specific setting.

The amount by which the DATAFILE is extended when more space is required.

<a id="std-setting-DATAFILE_TMP_EXTSIZE"></a>

##### `DATAFILE_TMP_EXTSIZE`

Default: `'25M'`

This is an Oracle-specific setting.

The amount by which the DATAFILE_TMP is extended when more space is required.

<a id="std-setting-DATA_UPLOAD_MAX_MEMORY_SIZE"></a>

### `DATA_UPLOAD_MAX_MEMORY_SIZE`

Default: `2621440` (i.e. 2.5 MB).

The maximum size in bytes that a request body may be before a
[`SuspiciousOperation`](exceptions.md#django.core.exceptions.SuspiciousOperation) (`RequestDataTooBig`) is
raised. The check is done when accessing `request.body` or `request.POST`
and is calculated against the total request size excluding any file upload
data. You can set this to `None` to disable the check. Applications that are
expected to receive unusually large form posts should tune this setting.

The amount of request data is correlated to the amount of memory needed to
process the request and populate the GET and POST dictionaries. Large requests
could be used as a denial-of-service attack vector if left unchecked. Since web
servers don’t typically perform deep request inspection, it’s not possible to
perform a similar check at that level.

See also [`FILE_UPLOAD_MAX_MEMORY_SIZE`](#std-setting-FILE_UPLOAD_MAX_MEMORY_SIZE).

<a id="std-setting-DATA_UPLOAD_MAX_NUMBER_FIELDS"></a>

### `DATA_UPLOAD_MAX_NUMBER_FIELDS`

Default: `1000`

The maximum number of parameters that may be received via GET or POST before a
[`SuspiciousOperation`](exceptions.md#django.core.exceptions.SuspiciousOperation) (`TooManyFields`) is
raised. You can set this to `None` to disable the check. Applications that
are expected to receive an unusually large number of form fields should tune
this setting.

The number of request parameters is correlated to the amount of time needed to
process the request and populate the GET and POST dictionaries. Large requests
could be used as a denial-of-service attack vector if left unchecked. Since web
servers don’t typically perform deep request inspection, it’s not possible to
perform a similar check at that level.

<a id="std-setting-DATA_UPLOAD_MAX_NUMBER_FILES"></a>

### `DATA_UPLOAD_MAX_NUMBER_FILES`

Default: `100`

The maximum number of files that may be received via POST in a
`multipart/form-data` encoded request before a
[`SuspiciousOperation`](exceptions.md#django.core.exceptions.SuspiciousOperation) (`TooManyFiles`) is
raised. You can set this to `None` to disable the check. Applications that
are expected to receive an unusually large number of file fields should tune
this setting.

The number of accepted files is correlated to the amount of time and memory
needed to process the request. Large requests could be used as a
denial-of-service attack vector if left unchecked. Since web servers don’t
typically perform deep request inspection, it’s not possible to perform a
similar check at that level.

<a id="std-setting-DATABASE_ROUTERS"></a>

### `DATABASE_ROUTERS`

Default: `[]` (Empty list)

The list of routers that will be used to determine which database
to use when performing a database query.

See the documentation on [automatic database routing in multi
database configurations](../topics/db/multi-db.md#topics-db-multi-db-routing).

<a id="std-setting-DATE_FORMAT"></a>

### `DATE_FORMAT`

Default: `'N j, Y'` (e.g. `Feb. 4, 2003`)

The default formatting to use for displaying date fields in any part of the
system. Note that the locale-dictated format has higher precedence and will be
applied instead. See [`allowed date format strings`](templates/builtins.md#std-templatefilter-date).

See also [`DATETIME_FORMAT`](#std-setting-DATETIME_FORMAT), [`TIME_FORMAT`](#std-setting-TIME_FORMAT) and
[`SHORT_DATE_FORMAT`](#std-setting-SHORT_DATE_FORMAT).

<a id="std-setting-DATE_INPUT_FORMATS"></a>

### `DATE_INPUT_FORMATS`

Default:

```default
[
    "%Y-%m-%d",  # '2006-10-25'
    "%m/%d/%Y",  # '10/25/2006'
    "%m/%d/%y",  # '10/25/06'
    "%b %d %Y",  # 'Oct 25 2006'
    "%b %d, %Y",  # 'Oct 25, 2006'
    "%d %b %Y",  # '25 Oct 2006'
    "%d %b, %Y",  # '25 Oct, 2006'
    "%B %d %Y",  # 'October 25 2006'
    "%B %d, %Y",  # 'October 25, 2006'
    "%d %B %Y",  # '25 October 2006'
    "%d %B, %Y",  # '25 October, 2006'
]
```

A list of formats that will be accepted when inputting data on a date field.
Formats will be tried in order, using the first valid one. Note that these
format strings use Python’s [datetime module syntax](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior), not the format strings from the [`date`](templates/builtins.md#std-templatefilter-date)
template filter.

The locale-dictated format has higher precedence and will be applied instead.

See also [`DATETIME_INPUT_FORMATS`](#std-setting-DATETIME_INPUT_FORMATS) and [`TIME_INPUT_FORMATS`](#std-setting-TIME_INPUT_FORMATS).

<a id="std-setting-DATETIME_FORMAT"></a>

### `DATETIME_FORMAT`

Default: `'N j, Y, P'` (e.g. `Feb. 4, 2003, 4 p.m.`)

The default formatting to use for displaying datetime fields in any part of the
system. Note that the locale-dictated format has higher precedence and will be
applied instead. See [`allowed date format strings`](templates/builtins.md#std-templatefilter-date).

See also [`DATE_FORMAT`](#std-setting-DATE_FORMAT), [`TIME_FORMAT`](#std-setting-TIME_FORMAT) and
[`SHORT_DATETIME_FORMAT`](#std-setting-SHORT_DATETIME_FORMAT).

<a id="std-setting-DATETIME_INPUT_FORMATS"></a>

### `DATETIME_INPUT_FORMATS`

Default:

```default
[
    "%Y-%m-%d %H:%M:%S",  # '2006-10-25 14:30:59'
    "%Y-%m-%d %H:%M:%S.%f",  # '2006-10-25 14:30:59.000200'
    "%Y-%m-%d %H:%M",  # '2006-10-25 14:30'
    "%m/%d/%Y %H:%M:%S",  # '10/25/2006 14:30:59'
    "%m/%d/%Y %H:%M:%S.%f",  # '10/25/2006 14:30:59.000200'
    "%m/%d/%Y %H:%M",  # '10/25/2006 14:30'
    "%m/%d/%y %H:%M:%S",  # '10/25/06 14:30:59'
    "%m/%d/%y %H:%M:%S.%f",  # '10/25/06 14:30:59.000200'
    "%m/%d/%y %H:%M",  # '10/25/06 14:30'
]
```

A list of formats that will be accepted when inputting data on a datetime
field. Formats will be tried in order, using the first valid one. Note that
these format strings use Python’s [datetime module syntax](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior), not the format strings from the [`date`](templates/builtins.md#std-templatefilter-date)
template filter. Date-only formats are not included as datetime fields will
automatically try [`DATE_INPUT_FORMATS`](#std-setting-DATE_INPUT_FORMATS) in last resort.

The locale-dictated format has higher precedence and will be applied instead.

See also [`DATE_INPUT_FORMATS`](#std-setting-DATE_INPUT_FORMATS) and [`TIME_INPUT_FORMATS`](#std-setting-TIME_INPUT_FORMATS).

<a id="std-setting-DEBUG"></a>

### `DEBUG`

Default: `False`

A boolean that turns on/off debug mode.

Never deploy a site into production with [`DEBUG`](#std-setting-DEBUG) turned on.

One of the main features of debug mode is the display of detailed error pages.
If your app raises an exception when [`DEBUG`](#std-setting-DEBUG) is `True`, Django will
display a detailed traceback, including a lot of metadata about your
environment, such as all the currently defined Django settings (from
`settings.py`).

As a security measure, Django will *not* include settings that might be
sensitive, such as [`SECRET_KEY`](#std-setting-SECRET_KEY). Specifically, it will exclude any
setting whose name includes any of the following:

* `'API'`
* `'KEY'`
* `'PASS'`
* `'SECRET'`
* `'SIGNATURE'`
* `'TOKEN'`

Note that these are *partial* matches. `'PASS'` will also match PASSWORD,
just as `'TOKEN'` will also match TOKENIZED and so on.

Still, note that there are always going to be sections of your debug output
that are inappropriate for public consumption. File paths, configuration
options and the like all give attackers extra information about your server.

It is also important to remember that when running with [`DEBUG`](#std-setting-DEBUG)
turned on, Django will remember every SQL query it executes. This is useful
when you’re debugging, but it’ll rapidly consume memory on a production server.

Finally, if [`DEBUG`](#std-setting-DEBUG) is `False`, you also need to properly set
the [`ALLOWED_HOSTS`](#std-setting-ALLOWED_HOSTS) setting. Failing to do so will result in all
requests being returned as “Bad Request (400)”.

#### NOTE
The default `settings.py` file created by [`django-admin
startproject`](django-admin.md#django-admin-startproject) sets `DEBUG = True` for convenience.

<a id="std-setting-DEBUG_PROPAGATE_EXCEPTIONS"></a>

### `DEBUG_PROPAGATE_EXCEPTIONS`

Default: `False`

If set to `True`, Django’s exception handling of view functions
([`handler500`](urls.md#django.conf.urls.handler500), or the debug view if [`DEBUG`](#std-setting-DEBUG)
is `True`) and logging of 500 responses ([django.request](logging.md#django-request-logger)) is
skipped and exceptions propagate upward.

This can be useful for some test setups. It shouldn’t be used on a live site
unless you want your web server (instead of Django) to generate “Internal
Server Error” responses. In that case, make sure your server doesn’t show the
stack trace or other sensitive information in the response.

<a id="std-setting-DECIMAL_SEPARATOR"></a>

### `DECIMAL_SEPARATOR`

Default: `'.'` (Dot)

Default decimal separator used when formatting decimal numbers.

Note that the locale-dictated format has higher precedence and will be applied
instead.

See also [`NUMBER_GROUPING`](#std-setting-NUMBER_GROUPING), [`THOUSAND_SEPARATOR`](#std-setting-THOUSAND_SEPARATOR) and
[`USE_THOUSAND_SEPARATOR`](#std-setting-USE_THOUSAND_SEPARATOR).

<a id="std-setting-DEFAULT_AUTO_FIELD"></a>

### `DEFAULT_AUTO_FIELD`

Default: `'`[`django.db.models.BigAutoField`](models/fields.md#django.db.models.BigAutoField)`'`

Default primary key field type to use for models that don’t have a field with
[`primary_key=True`](models/fields.md#django.db.models.Field.primary_key).

#### Versionchanged
In older versions, the default value is
[`django.db.models.AutoField`](models/fields.md#django.db.models.AutoField).

<a id="std-setting-DEFAULT_CHARSET"></a>

### `DEFAULT_CHARSET`

Default: `'utf-8'`

Default charset to use for all `HttpResponse` objects, if a MIME type isn’t
manually specified. Used when constructing the `Content-Type` header.

<a id="std-setting-DEFAULT_EXCEPTION_REPORTER"></a>

### `DEFAULT_EXCEPTION_REPORTER`

Default: `'`[`django.views.debug.ExceptionReporter`](../howto/error-reporting.md#django.views.debug.ExceptionReporter)`'`

Default exception reporter class to be used if none has been assigned to the
[`HttpRequest`](request-response.md#django.http.HttpRequest) instance yet. See
[Custom error reports](../howto/error-reporting.md#custom-error-reports).

<a id="std-setting-DEFAULT_EXCEPTION_REPORTER_FILTER"></a>

### `DEFAULT_EXCEPTION_REPORTER_FILTER`

Default: `'`[`django.views.debug.SafeExceptionReporterFilter`](../howto/error-reporting.md#django.views.debug.SafeExceptionReporterFilter)`'`

Default exception reporter filter class to be used if none has been assigned to
the [`HttpRequest`](request-response.md#django.http.HttpRequest) instance yet.
See [Filtering error reports](../howto/error-reporting.md#filtering-error-reports).

<a id="std-setting-DEFAULT_FROM_EMAIL"></a>

### `DEFAULT_FROM_EMAIL`

Default: `'webmaster@localhost'`

Default email address for automated correspondence from the site manager(s).
This address is used in the `From:` header of outgoing emails and can take
any format valid in the chosen email sending protocol.

This doesn’t affect error messages sent to [`ADMINS`](#std-setting-ADMINS) and
[`MANAGERS`](#std-setting-MANAGERS). See [`SERVER_EMAIL`](#std-setting-SERVER_EMAIL) for that.

<a id="std-setting-DEFAULT_INDEX_TABLESPACE"></a>

### `DEFAULT_INDEX_TABLESPACE`

Default: `''` (Empty string)

Default tablespace to use for indexes on fields that don’t specify
one, if the backend supports it (see [Tablespaces](../topics/db/tablespaces.md)).

<a id="std-setting-DEFAULT_TABLESPACE"></a>

### `DEFAULT_TABLESPACE`

Default: `''` (Empty string)

Default tablespace to use for models that don’t specify one, if the
backend supports it (see [Tablespaces](../topics/db/tablespaces.md)).

<a id="std-setting-DISALLOWED_USER_AGENTS"></a>

### `DISALLOWED_USER_AGENTS`

Default: `[]` (Empty list)

List of compiled regular expression objects representing User-Agent strings
that are not allowed to visit any page, systemwide. Use this for bots/crawlers.
This is only used if `CommonMiddleware` is installed (see
[Middleware](../topics/http/middleware.md)).

<a id="std-setting-EMAIL_BACKEND"></a>

### `EMAIL_BACKEND`

Default: `'`[`django.core.mail.backends.smtp.EmailBackend`](../topics/email.md#django.core.mail.backends.smtp.EmailBackend)`'`

The backend to use for sending emails. For the list of available backends see
[Email backends](../topics/email.md#topic-email-backends).

<a id="std-setting-EMAIL_FILE_PATH"></a>

### `EMAIL_FILE_PATH`

Default: Not defined

The directory used by the [file email backend](../topics/email.md#topic-email-file-backend)
to store output files.

<a id="std-setting-EMAIL_HOST"></a>

### `EMAIL_HOST`

Default: `'localhost'`

The host to use for sending email.

See also [`EMAIL_PORT`](#std-setting-EMAIL_PORT).

<a id="std-setting-EMAIL_HOST_PASSWORD"></a>

### `EMAIL_HOST_PASSWORD`

Default: `''` (Empty string)

Password to use for the SMTP server defined in [`EMAIL_HOST`](#std-setting-EMAIL_HOST). This
setting is used in conjunction with [`EMAIL_HOST_USER`](#std-setting-EMAIL_HOST_USER) when
authenticating to the SMTP server. If either of these settings is empty,
Django won’t attempt authentication.

See also [`EMAIL_HOST_USER`](#std-setting-EMAIL_HOST_USER).

<a id="std-setting-EMAIL_HOST_USER"></a>

### `EMAIL_HOST_USER`

Default: `''` (Empty string)

Username to use for the SMTP server defined in [`EMAIL_HOST`](#std-setting-EMAIL_HOST).
If empty, Django won’t attempt authentication.

See also [`EMAIL_HOST_PASSWORD`](#std-setting-EMAIL_HOST_PASSWORD).

<a id="std-setting-EMAIL_PORT"></a>

### `EMAIL_PORT`

Default: `25`

Port to use for the SMTP server defined in [`EMAIL_HOST`](#std-setting-EMAIL_HOST).

<a id="std-setting-EMAIL_SUBJECT_PREFIX"></a>

### `EMAIL_SUBJECT_PREFIX`

Default: `'[Django] '`

Subject-line prefix for email messages sent with
`django.core.mail.mail_admins` or `django.core.mail.mail_managers`. You’ll
probably want to include the trailing space.

<a id="std-setting-EMAIL_USE_LOCALTIME"></a>

### `EMAIL_USE_LOCALTIME`

Default: `False`

Whether to send the SMTP `Date` header of email messages in the local time
zone (`True`) or in UTC (`False`).

<a id="std-setting-EMAIL_USE_TLS"></a>

### `EMAIL_USE_TLS`

Default: `False`

Whether to use a TLS (secure) connection when talking to the SMTP server.
This is used for explicit TLS connections, generally on port 587. If you are
experiencing hanging connections, see the implicit TLS setting
[`EMAIL_USE_SSL`](#std-setting-EMAIL_USE_SSL).

<a id="std-setting-EMAIL_USE_SSL"></a>

### `EMAIL_USE_SSL`

Default: `False`

Whether to use an implicit TLS (secure) connection when talking to the SMTP
server. In most email documentation this type of TLS connection is referred
to as SSL. It is generally used on port 465. If you are experiencing problems,
see the explicit TLS setting [`EMAIL_USE_TLS`](#std-setting-EMAIL_USE_TLS).

Note that [`EMAIL_USE_TLS`](#std-setting-EMAIL_USE_TLS)/[`EMAIL_USE_SSL`](#std-setting-EMAIL_USE_SSL) are mutually
exclusive, so only set one of those settings to `True`.

<a id="std-setting-EMAIL_SSL_CERTFILE"></a>

### `EMAIL_SSL_CERTFILE`

Default: `None`

If [`EMAIL_USE_SSL`](#std-setting-EMAIL_USE_SSL) or [`EMAIL_USE_TLS`](#std-setting-EMAIL_USE_TLS) is `True` and the
secure connection to the SMTP server requires client authentication, use this
setting to specify the path to a PEM-formatted certificate chain file, which
must be used in conjunction with [`EMAIL_SSL_KEYFILE`](#std-setting-EMAIL_SSL_KEYFILE).

`EMAIL_SSL_CERTFILE` should not be used with a self-signed server certificate
or a certificate from a private certificate authority (CA). In such cases, the
server’s certificate (or the root certificate of the private CA) should be
installed into the system’s CA bundle. This can be done by following
platform-specific instructions for installing a root CA certificate,
or by using OpenSSL’s `SSL_CERT_FILE` or `SSL_CERT_DIR` environment
variables to specify a custom certificate bundle (if modifying the system
bundle is not possible or desired).

For more complex scenarios, the SMTP
[`EmailBackend`](../topics/email.md#django.core.mail.backends.smtp.EmailBackend) can be subclassed to add
root certificates to its `ssl_context` using
[`ssl.SSLContext.load_verify_locations()`](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_verify_locations).

<a id="std-setting-EMAIL_SSL_KEYFILE"></a>

### `EMAIL_SSL_KEYFILE`

Default: `None`

If [`EMAIL_USE_SSL`](#std-setting-EMAIL_USE_SSL) or [`EMAIL_USE_TLS`](#std-setting-EMAIL_USE_TLS) is `True`, you can
optionally specify the path to a PEM-formatted private key file for client
authentication of the SSL connection along with [`EMAIL_SSL_CERTFILE`](#std-setting-EMAIL_SSL_CERTFILE).

Note that setting [`EMAIL_SSL_CERTFILE`](#std-setting-EMAIL_SSL_CERTFILE) and
[`EMAIL_SSL_KEYFILE`](#std-setting-EMAIL_SSL_KEYFILE) doesn’t result in any certificate checking.
They’re passed to the underlying SSL connection. Please refer to the
documentation of Python’s [`ssl.SSLContext.wrap_socket()`](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.wrap_socket) function
for details on how the certificate chain file and private key file are handled.

<a id="std-setting-EMAIL_TIMEOUT"></a>

### `EMAIL_TIMEOUT`

Default: `None`

Specifies a timeout in seconds for blocking operations like the connection
attempt.

<a id="std-setting-FILE_UPLOAD_HANDLERS"></a>

### `FILE_UPLOAD_HANDLERS`

Default:

```default
[
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]
```

A list of handlers to use for uploading. Changing this setting allows complete
customization – even replacement – of Django’s upload process.

See [Managing files](../topics/files.md) for details.

<a id="std-setting-FILE_UPLOAD_MAX_MEMORY_SIZE"></a>

### `FILE_UPLOAD_MAX_MEMORY_SIZE`

Default: `2621440` (i.e. 2.5 MB).

The maximum size (in bytes) that an upload will be before it gets streamed to
the file system. See [Managing files](../topics/files.md) for details.

See also [`DATA_UPLOAD_MAX_MEMORY_SIZE`](#std-setting-DATA_UPLOAD_MAX_MEMORY_SIZE).

<a id="std-setting-FILE_UPLOAD_DIRECTORY_PERMISSIONS"></a>

### `FILE_UPLOAD_DIRECTORY_PERMISSIONS`

Default: `None`

The numeric mode to apply to directories created in the process of uploading
files.

This setting also determines the default permissions for collected static
directories when using the [`collectstatic`](contrib/staticfiles.md#django-admin-collectstatic) management command. See
[`collectstatic`](contrib/staticfiles.md#django-admin-collectstatic) for details on overriding it.

This value mirrors the functionality and caveats of the
[`FILE_UPLOAD_PERMISSIONS`](#std-setting-FILE_UPLOAD_PERMISSIONS) setting.

<a id="std-setting-FILE_UPLOAD_PERMISSIONS"></a>

### `FILE_UPLOAD_PERMISSIONS`

Default: `0o644`

The numeric mode (i.e. `0o644`) to set newly uploaded files to. For
more information about what these modes mean, see the documentation for
[`os.chmod()`](https://docs.python.org/3/library/os.html#os.chmod).

If `None`, you’ll get operating-system dependent behavior. On most platforms,
temporary files will have a mode of `0o600`, and files saved from memory will
be saved using the system’s standard umask.

For security reasons, these permissions aren’t applied to the temporary files
that are stored in [`FILE_UPLOAD_TEMP_DIR`](#std-setting-FILE_UPLOAD_TEMP_DIR).

This setting also determines the default permissions for collected static files
when using the [`collectstatic`](contrib/staticfiles.md#django-admin-collectstatic) management command. See
[`collectstatic`](contrib/staticfiles.md#django-admin-collectstatic) for details on overriding it.

#### WARNING
**Always prefix the mode with** `0o` **.**

If you’re not familiar with file modes, please note that the `0o` prefix
is very important: it indicates an octal number, which is the way that
modes must be specified. If you try to use `644`, you’ll get totally
incorrect behavior.

<a id="std-setting-FILE_UPLOAD_TEMP_DIR"></a>

### `FILE_UPLOAD_TEMP_DIR`

Default: `None`

The directory to store data to (typically files larger than
[`FILE_UPLOAD_MAX_MEMORY_SIZE`](#std-setting-FILE_UPLOAD_MAX_MEMORY_SIZE)) temporarily while uploading files.
If `None`, Django will use the standard temporary directory for the operating
system. For example, this will default to `/tmp` on \*nix-style operating
systems.

See [Managing files](../topics/files.md) for details.

<a id="std-setting-FIRST_DAY_OF_WEEK"></a>

### `FIRST_DAY_OF_WEEK`

Default: `0` (Sunday)

A number representing the first day of the week. This is especially useful
when displaying a calendar. This value is only used when not using
format internationalization, or when a format cannot be found for the
current locale.

The value must be an integer from 0 to 6, where 0 means Sunday, 1 means
Monday and so on.

<a id="std-setting-FIXTURE_DIRS"></a>

### `FIXTURE_DIRS`

Default: `[]` (Empty list)

List of directories searched for [fixture](../topics/db/fixtures.md#fixtures-explanation) files,
in addition to the `fixtures` directory of each application, in search order.

Note that these paths should use Unix-style forward slashes, even on Windows.

See [Provide data with fixtures](../howto/initial-data.md#initial-data-via-fixtures) and [Fixture loading](../topics/testing/tools.md#topics-testing-fixtures).

<a id="std-setting-FORCE_SCRIPT_NAME"></a>

### `FORCE_SCRIPT_NAME`

Default: `None`

If not `None`, this will be used as the value of the `SCRIPT_NAME`
environment variable in any HTTP request. This setting can be used to override
the server-provided value of `SCRIPT_NAME`, which may be a rewritten version
of the preferred value or not supplied at all. It is also used by
[`django.setup()`](applications.md#django.setup) to set the URL resolver script prefix outside of the
request/response cycle (e.g. in management commands and standalone scripts) to
generate correct URLs when `FORCE_SCRIPT_NAME` is provided.

<a id="std-setting-FORM_RENDERER"></a>

### `FORM_RENDERER`

Default: `'`[`django.forms.renderers.DjangoTemplates`](forms/renderers.md#django.forms.renderers.DjangoTemplates)`'`

The class that renders forms and form widgets. It must implement
[the low-level render API](forms/renderers.md#low-level-widget-render-api). Included form
renderers are:

* `'`[`django.forms.renderers.DjangoTemplates`](forms/renderers.md#django.forms.renderers.DjangoTemplates)`'`
* `'`[`django.forms.renderers.Jinja2`](forms/renderers.md#django.forms.renderers.Jinja2)`'`
* `'`[`django.forms.renderers.TemplatesSetting`](forms/renderers.md#django.forms.renderers.TemplatesSetting)`'`

<a id="std-setting-FORMAT_MODULE_PATH"></a>

### `FORMAT_MODULE_PATH`

Default: `None`

A full Python path to a Python package that contains custom format definitions
for project locales. If not `None`, Django will check for a `formats.py`
file, under the directory named as the current locale, and will use the
formats defined in this file.

The name of the directory containing the format definitions is expected to be
named using [locale name](../topics/i18n/index.md#term-locale-name) notation, for example `de`, `pt_BR`,
`en_US`, etc.

For example, if [`FORMAT_MODULE_PATH`](#std-setting-FORMAT_MODULE_PATH) is set to `mysite.formats`,
and current language is `en` (English), Django will expect a directory tree
like:

```text
mysite/
    formats/
        __init__.py
        en/
            __init__.py
            formats.py
```

You can also set this setting to a list of Python paths, for example:

```default
FORMAT_MODULE_PATH = [
    "mysite.formats",
    "some_app.formats",
]
```

When Django searches for a certain format, it will go through all given Python
paths until it finds a module that actually defines the given format. This
means that formats defined in packages farther up in the list will take
precedence over the same formats in packages farther down.

Available formats are:

* [`DATE_FORMAT`](#std-setting-DATE_FORMAT)
* [`DATE_INPUT_FORMATS`](#std-setting-DATE_INPUT_FORMATS)
* [`DATETIME_FORMAT`](#std-setting-DATETIME_FORMAT),
* [`DATETIME_INPUT_FORMATS`](#std-setting-DATETIME_INPUT_FORMATS)
* [`DECIMAL_SEPARATOR`](#std-setting-DECIMAL_SEPARATOR)
* [`FIRST_DAY_OF_WEEK`](#std-setting-FIRST_DAY_OF_WEEK)
* [`MONTH_DAY_FORMAT`](#std-setting-MONTH_DAY_FORMAT)
* [`NUMBER_GROUPING`](#std-setting-NUMBER_GROUPING)
* [`SHORT_DATE_FORMAT`](#std-setting-SHORT_DATE_FORMAT)
* [`SHORT_DATETIME_FORMAT`](#std-setting-SHORT_DATETIME_FORMAT)
* [`THOUSAND_SEPARATOR`](#std-setting-THOUSAND_SEPARATOR)
* [`TIME_FORMAT`](#std-setting-TIME_FORMAT)
* [`TIME_INPUT_FORMATS`](#std-setting-TIME_INPUT_FORMATS)
* [`YEAR_MONTH_FORMAT`](#std-setting-YEAR_MONTH_FORMAT)

<a id="std-setting-IGNORABLE_404_URLS"></a>

### `IGNORABLE_404_URLS`

Default: `[]` (Empty list)

List of compiled regular expression objects describing URLs that should be
ignored when reporting HTTP 404 errors via email (see
[How to manage error reporting](../howto/error-reporting.md)). Regular expressions are matched against
request’s full paths, as returned by
[`get_full_path()`](request-response.md#django.http.HttpRequest.get_full_path) (including any query strings).
Use this if your site does not provide a commonly requested file such as
`favicon.ico` or `robots.txt`.

This is only used if
[`BrokenLinkEmailsMiddleware`](middleware.md#django.middleware.common.BrokenLinkEmailsMiddleware) is enabled (see
[Middleware](../topics/http/middleware.md)).

<a id="std-setting-INSTALLED_APPS"></a>

### `INSTALLED_APPS`

Default: `[]` (Empty list)

A list of strings designating all applications that are enabled in this
Django installation. Each string should be a dotted Python path to:

* an application configuration class (preferred), or
* a package containing an application.

[Learn more about application configurations](applications.md).

When several applications provide different versions of the same resource
(template, static file, management command, translation), the application
listed first in [`INSTALLED_APPS`](#std-setting-INSTALLED_APPS) has precedence.

<a id="std-setting-INTERNAL_IPS"></a>

### `INTERNAL_IPS`

Default: `[]` (Empty list)

A list of IP addresses, as strings, that:

* Allow the [`debug()`](templates/api.md#django.template.context_processors.debug) context processor
  to add some variables to the template context.
* Can use the [admindocs bookmarklets](contrib/admin/admindocs.md#admindocs-bookmarklets) even if
  not logged in as a staff user.
* Are marked as “internal” (as opposed to “EXTERNAL”) in
  [`AdminEmailHandler`](logging.md#django.utils.log.AdminEmailHandler) emails.

<a id="std-setting-LANGUAGE_CODE"></a>

### `LANGUAGE_CODE`

Default: `'en-us'`

A string representing the language code for this installation. This should be
in standard [language ID format](../topics/i18n/index.md#term-language-code). For example, U.S.
English is `"en-us"`. See also the [list of language identifiers](http://www.i18nguy.com/unicode/language-identifiers.html) and
[Internationalization and localization](../topics/i18n/index.md).

It serves three purposes:

* If the locale middleware isn’t in use, it decides which translation is served
  to all users.
* If the locale middleware is active, it provides a fallback language in case
  the user’s preferred language can’t be determined or is not supported by the
  website. It also provides the fallback translation when a translation for a
  given literal doesn’t exist for the user’s preferred language.
* If localization is explicitly disabled via the [`unlocalize`](../topics/i18n/formatting.md#std-templatefilter-unlocalize) filter
  or the [`{% localize off %}`](../topics/i18n/formatting.md#std-templatetag-localize) tag, it provides fallback
  localization formats which will be applied instead. See
  [controlling localization in templates](../topics/i18n/formatting.md#topic-l10n-templates) for
  details.

See [How Django discovers language preference](../topics/i18n/translation.md#how-django-discovers-language-preference) for more details.

<a id="std-setting-LANGUAGE_COOKIE_AGE"></a>

### `LANGUAGE_COOKIE_AGE`

Default: `None` (expires at browser close)

The age of the language cookie, in seconds.

<a id="std-setting-LANGUAGE_COOKIE_DOMAIN"></a>

### `LANGUAGE_COOKIE_DOMAIN`

Default: `None`

The domain to use for the language cookie. Set this to a string such as
`"example.com"` for cross-domain cookies, or use `None` for a standard
domain cookie.

Be cautious when updating this setting on a production site. If you update
this setting to enable cross-domain cookies on a site that previously used
standard domain cookies, existing user cookies that have the old domain
will not be updated. This will result in site users being unable to switch
the language as long as these cookies persist. The only safe and reliable
option to perform the switch is to change the language cookie name
permanently (via the [`LANGUAGE_COOKIE_NAME`](#std-setting-LANGUAGE_COOKIE_NAME) setting) and to add
a middleware that copies the value from the old cookie to a new one and then
deletes the old one.

<a id="std-setting-LANGUAGE_COOKIE_HTTPONLY"></a>

### `LANGUAGE_COOKIE_HTTPONLY`

Default: `False`

Whether to use `HttpOnly` flag on the language cookie. If this is set to
`True`, client-side JavaScript will not be able to access the language
cookie.

See [`SESSION_COOKIE_HTTPONLY`](#std-setting-SESSION_COOKIE_HTTPONLY) for details on `HttpOnly`.

<a id="std-setting-LANGUAGE_COOKIE_NAME"></a>

### `LANGUAGE_COOKIE_NAME`

Default: `'django_language'`

The name of the cookie to use for the language cookie. This can be whatever
you want (as long as it’s different from the other cookie names in your
application). See [Internationalization and localization](../topics/i18n/index.md).

<a id="std-setting-LANGUAGE_COOKIE_PATH"></a>

### `LANGUAGE_COOKIE_PATH`

Default: `'/'`

The path set on the language cookie. This should either match the URL path of
your Django installation or be a parent of that path.

This is useful if you have multiple Django instances running under the same
hostname. They can use different cookie paths and each instance will only see
its own language cookie.

Be cautious when updating this setting on a production site. If you update this
setting to use a deeper path than it previously used, existing user cookies
that have the old path will not be updated. This will result in site users
being unable to switch the language as long as these cookies persist. The only
safe and reliable option to perform the switch is to change the language cookie
name permanently (via the [`LANGUAGE_COOKIE_NAME`](#std-setting-LANGUAGE_COOKIE_NAME) setting), and to add
a middleware that copies the value from the old cookie to a new one and then
deletes the one.

<a id="std-setting-LANGUAGE_COOKIE_SAMESITE"></a>

### `LANGUAGE_COOKIE_SAMESITE`

Default: `None`

The value of the [SameSite](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value) flag on the language cookie. This flag prevents
the cookie from being sent in cross-site requests.

See [`SESSION_COOKIE_SAMESITE`](#std-setting-SESSION_COOKIE_SAMESITE) for details about `SameSite`.

<a id="std-setting-LANGUAGE_COOKIE_SECURE"></a>

### `LANGUAGE_COOKIE_SECURE`

Default: `False`

Whether to use a secure cookie for the language cookie. If this is set to
`True`, the cookie will be marked as “secure”, which means browsers may
ensure that the cookie is only sent under an HTTPS connection.

<a id="std-setting-LANGUAGES"></a>

### `LANGUAGES`

Default: A list of all available languages. This list is continually growing
and including a copy here would inevitably become rapidly out of date. You can
see the current list of translated languages by looking in
[django/conf/global_settings.py](https://github.com/django/django/blob/main/django/conf/global_settings.py).

The list is a list of 2-tuples in the format
([language code](../topics/i18n/index.md#term-language-code), `language name`) – for example,
`('ja', 'Japanese')`.
This specifies which languages are available for language selection. See
[Internationalization and localization](../topics/i18n/index.md).

Generally, the default value should suffice. Only set this setting if you want
to restrict language selection to a subset of the Django-provided languages.

If you define a custom [`LANGUAGES`](#std-setting-LANGUAGES) setting, you can mark the
language names as translation strings using the
[`gettext_lazy()`](utils.md#django.utils.translation.gettext_lazy) function.

Here’s a sample settings file:

```default
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]
```

<a id="std-setting-LANGUAGES_BIDI"></a>

### `LANGUAGES_BIDI`

Default: A list of all language codes that are written right-to-left. You can
see the current list of these languages by looking in
[django/conf/global_settings.py](https://github.com/django/django/blob/main/django/conf/global_settings.py).

The list contains [language codes](../topics/i18n/index.md#term-language-code) for languages that are
written right-to-left.

Generally, the default value should suffice. Only set this setting if you want
to restrict language selection to a subset of the Django-provided languages.
If you define a custom [`LANGUAGES`](#std-setting-LANGUAGES) setting, the list of bidirectional
languages may contain language codes which are not enabled on a given site.

<a id="std-setting-LOCALE_PATHS"></a>

### `LOCALE_PATHS`

Default: `[]` (Empty list)

A list of directories where Django looks for translation files.
See [How Django discovers translations](../topics/i18n/translation.md#how-django-discovers-translations).

Example:

```default
LOCALE_PATHS = [
    "/home/www/project/common_files/locale",
    "/var/local/translations/locale",
]
```

Django will look within each of these paths for the
`<locale_code>/LC_MESSAGES` directories containing the actual translation
files.

<a id="std-setting-LOGGING"></a>

### `LOGGING`

Default: A logging configuration dictionary.

A data structure containing configuration information. When not-empty, the
contents of this data structure will be passed as the argument to the
configuration method described in [`LOGGING_CONFIG`](#std-setting-LOGGING_CONFIG).

Among other things, the default logging configuration passes HTTP 500 server
errors to an email log handler when [`DEBUG`](#std-setting-DEBUG) is `False`. See also
[Configuring logging](../topics/logging.md#configuring-logging).

You can see the default logging configuration by looking in
[django/utils/log.py](https://github.com/django/django/blob/main/django/utils/log.py).

<a id="std-setting-LOGGING_CONFIG"></a>

### `LOGGING_CONFIG`

Default: `'logging.config.dictConfig'`

A path to a callable that will be used to configure logging in the
Django project. Points at an instance of Python’s [dictConfig](https://docs.python.org/3/library/logging.config.html#logging-config-dictschema) configuration method by default.

If you set [`LOGGING_CONFIG`](#std-setting-LOGGING_CONFIG) to `None`, the logging
configuration process will be skipped.

<a id="std-setting-MANAGERS"></a>

### `MANAGERS`

Default: `[]` (Empty list)

A list in the same format as [`ADMINS`](#std-setting-ADMINS) that specifies who should get
broken link notifications when
[`BrokenLinkEmailsMiddleware`](middleware.md#django.middleware.common.BrokenLinkEmailsMiddleware) is enabled.

#### Versionchanged
In older versions, required a list of (name, address) tuples.

<a id="std-setting-MEDIA_ROOT"></a>

### `MEDIA_ROOT`

Default: `''` (Empty string)

Absolute filesystem path to the directory that will hold [user-uploaded
files](../topics/files.md).

Example: `"/var/www/example.com/media/"`

See also [`MEDIA_URL`](#std-setting-MEDIA_URL).

#### WARNING
[`MEDIA_ROOT`](#std-setting-MEDIA_ROOT) and [`STATIC_ROOT`](#std-setting-STATIC_ROOT) must have different
values. Before [`STATIC_ROOT`](#std-setting-STATIC_ROOT) was introduced, it was common to
rely or fallback on [`MEDIA_ROOT`](#std-setting-MEDIA_ROOT) to also serve static files;
however, since this can have serious security implications, there is a
validation check to prevent it.

<a id="std-setting-MEDIA_URL"></a>

### `MEDIA_URL`

Default: `''` (Empty string)

URL that handles the media served from [`MEDIA_ROOT`](#std-setting-MEDIA_ROOT), used
for [managing stored files](../topics/files.md). It must end in a slash if set
to a non-empty value. You will need to [configure these files to be served](../howto/static-files/index.md#serving-uploaded-files-in-development) in both development and production
environments.

If you want to use `{{ MEDIA_URL }}` in your templates, add
`'django.template.context_processors.media'` in the `'context_processors'`
option of [`TEMPLATES`](#std-setting-TEMPLATES).

Example: `"https://media.example.com/"`

#### WARNING
There are security risks if you are accepting uploaded content from
untrusted users! See the security guide’s topic on
[User-uploaded content](../topics/security.md#user-uploaded-content-security) for mitigation details.

#### WARNING
[`MEDIA_URL`](#std-setting-MEDIA_URL) and [`STATIC_URL`](#std-setting-STATIC_URL) must have different
values. See [`MEDIA_ROOT`](#std-setting-MEDIA_ROOT) for more details.

#### NOTE
If [`MEDIA_URL`](#std-setting-MEDIA_URL) is a relative path, then it will be prefixed by the
server-provided value of `SCRIPT_NAME` (or `/` if not set). This makes
it easier to serve a Django application in a subpath without adding an
extra configuration to the settings.

<a id="std-setting-MIDDLEWARE"></a>

### `MIDDLEWARE`

Default: `None`

A list of middleware to use. See [Middleware](../topics/http/middleware.md).

<a id="std-setting-MIGRATION_MODULES"></a>

### `MIGRATION_MODULES`

Default: `{}` (Empty dictionary)

A dictionary specifying the package where migration modules can be found on a
per-app basis. The default value of this setting is an empty dictionary, but
the default package name for migration modules is `migrations`.

Example:

```default
{"blog": "blog.db_migrations"}
```

In this case, migrations pertaining to the `blog` app will be contained in
the `blog.db_migrations` package.

If you provide the `app_label` argument, [`makemigrations`](django-admin.md#django-admin-makemigrations) will
automatically create the package if it doesn’t already exist.

When you supply `None` as a value for an app, Django will consider the app as
an app without migrations regardless of an existing `migrations` submodule.
This can be used, for example, in a test settings file to skip migrations while
testing (tables will still be created for the apps’ models). To disable
migrations for all apps during tests, you can set the
[`MIGRATE`](#std-setting-TEST_MIGRATE) to `False` instead. If
`MIGRATION_MODULES` is used in your general project settings, remember to use
the [`migrate --run-syncdb`](django-admin.md#cmdoption-migrate-run-syncdb) option if you want to create tables for the
app.

<a id="std-setting-MONTH_DAY_FORMAT"></a>

### `MONTH_DAY_FORMAT`

Default: `'F j'`

The default formatting to use for date fields on Django admin change-list
pages – and, possibly, by other parts of the system – in cases when only the
month and day are displayed.

For example, when a Django admin change-list page is being filtered by a date
drilldown, the header for a given day displays the day and month. Different
locales have different formats. For example, U.S. English would say
“January 1,” whereas Spanish might say “1 Enero.”

Note that the corresponding locale-dictated format has higher precedence and
will be applied instead.

See [`allowed date format strings`](templates/builtins.md#std-templatefilter-date). See also
[`DATE_FORMAT`](#std-setting-DATE_FORMAT), [`DATETIME_FORMAT`](#std-setting-DATETIME_FORMAT),
[`TIME_FORMAT`](#std-setting-TIME_FORMAT) and [`YEAR_MONTH_FORMAT`](#std-setting-YEAR_MONTH_FORMAT).

<a id="std-setting-NUMBER_GROUPING"></a>

### `NUMBER_GROUPING`

Default: `0`

Number of digits grouped together on the integer part of a number.

Common use is to display a thousand separator. If this setting is `0`, then
no grouping will be applied to the number. If this setting is greater than
`0`, then [`THOUSAND_SEPARATOR`](#std-setting-THOUSAND_SEPARATOR) will be used as the separator between
those groups.

Some locales use non-uniform digit grouping, e.g. `10,00,00,000` in
`en_IN`. For this case, you can provide a sequence with the number of digit
group sizes to be applied. The first number defines the size of the group
preceding the decimal delimiter, and each number that follows defines the size
of preceding groups. If the sequence is terminated with `-1`, no further
grouping is performed. If the sequence terminates with a `0`, the last group
size is used for the remainder of the number.

Example tuple for `en_IN`:

```default
NUMBER_GROUPING = (3, 2, 0)
```

Note that the locale-dictated format has higher precedence and will be applied
instead.

See also [`DECIMAL_SEPARATOR`](#std-setting-DECIMAL_SEPARATOR), [`THOUSAND_SEPARATOR`](#std-setting-THOUSAND_SEPARATOR) and
[`USE_THOUSAND_SEPARATOR`](#std-setting-USE_THOUSAND_SEPARATOR).

<a id="std-setting-PREPEND_WWW"></a>

### `PREPEND_WWW`

Default: `False`

Whether to prepend the “www.” subdomain to URLs that don’t have it. This is
only used if [`CommonMiddleware`](middleware.md#django.middleware.common.CommonMiddleware) is installed
(see [Middleware](../topics/http/middleware.md)). See also [`APPEND_SLASH`](#std-setting-APPEND_SLASH).

<a id="std-setting-ROOT_URLCONF"></a>

### `ROOT_URLCONF`

Default: Not defined

A string representing the full Python import path to your root URLconf, for
example `"mydjangoapps.urls"`. Can be overridden on a per-request basis by
setting the attribute `urlconf` on the incoming `HttpRequest`
object. See [How Django processes a request](../topics/http/urls.md#how-django-processes-a-request) for details.

<a id="std-setting-SECRET_KEY"></a>

### `SECRET_KEY`

Default: `''` (Empty string)

A secret key for a particular Django installation. This is used to provide
[cryptographic signing](../topics/signing.md), and should be set to a unique,
unpredictable value.

[`django-admin startproject`](django-admin.md#django-admin-startproject) automatically adds a
randomly-generated `SECRET_KEY` to each new project.

Uses of the key shouldn’t assume that it’s text or bytes. Every use should go
through [`force_str()`](utils.md#django.utils.encoding.force_str) or
[`force_bytes()`](utils.md#django.utils.encoding.force_bytes) to convert it to the desired type.

Django will refuse to start if [`SECRET_KEY`](#std-setting-SECRET_KEY) is not set.

#### WARNING
**Keep this value secret.**

Running Django with a known [`SECRET_KEY`](#std-setting-SECRET_KEY) defeats many of Django’s
security protections, and can lead to privilege escalation and remote code
execution vulnerabilities.

The secret key is used for:

* All [sessions](../topics/http/sessions.md) if you are using
  any other session backend than `django.contrib.sessions.backends.cache`,
  or are using the default
  [`get_session_auth_hash()`](../topics/auth/customizing.md#django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash).
* All [messages](contrib/messages.md) if you are using
  [`CookieStorage`](contrib/messages.md#django.contrib.messages.storage.cookie.CookieStorage) or
  [`FallbackStorage`](contrib/messages.md#django.contrib.messages.storage.fallback.FallbackStorage).
* All [`PasswordResetView`](../topics/auth/default.md#django.contrib.auth.views.PasswordResetView) tokens.
* Any usage of [cryptographic signing](../topics/signing.md), unless a
  different key is provided.

When a secret key is no longer set as [`SECRET_KEY`](#std-setting-SECRET_KEY) or contained within
[`SECRET_KEY_FALLBACKS`](#std-setting-SECRET_KEY_FALLBACKS) all of the above will be invalidated. When
rotating your secret key, you should move the old key to
[`SECRET_KEY_FALLBACKS`](#std-setting-SECRET_KEY_FALLBACKS) temporarily. Secret keys are not used for
passwords of users and key rotation will not affect them.

#### NOTE
The default `settings.py` file created by [`django-admin
startproject`](django-admin.md#django-admin-startproject) creates a unique `SECRET_KEY` for
convenience.

<a id="std-setting-SECRET_KEY_FALLBACKS"></a>

### `SECRET_KEY_FALLBACKS`

Default: `[]`

A list of fallback secret keys for a particular Django installation. These are
used to allow rotation of the `SECRET_KEY`.

In order to rotate your secret keys, set a new `SECRET_KEY` and move the
previous value to the beginning of `SECRET_KEY_FALLBACKS`. Then remove the
old values from the end of the `SECRET_KEY_FALLBACKS` when you are ready to
expire the sessions, password reset tokens, and so on, that make use of them.

#### NOTE
Signing operations are computationally expensive. Having multiple old key
values in `SECRET_KEY_FALLBACKS` adds additional overhead to all checks
that don’t match an earlier key.

As such, fallback values should be removed after an appropriate period,
allowing for key rotation.

Uses of the secret key values shouldn’t assume that they are text or bytes.
Every use should go through [`force_str()`](utils.md#django.utils.encoding.force_str) or
[`force_bytes()`](utils.md#django.utils.encoding.force_bytes) to convert it to the desired type.

<a id="std-setting-SECURE_CONTENT_TYPE_NOSNIFF"></a>

### `SECURE_CONTENT_TYPE_NOSNIFF`

Default: `True`

If `True`, the [`SecurityMiddleware`](middleware.md#django.middleware.security.SecurityMiddleware)
sets the [X-Content-Type-Options: nosniff](middleware.md#x-content-type-options) header on all responses that do not
already have it.

<a id="std-setting-SECURE_CROSS_ORIGIN_OPENER_POLICY"></a>

### `SECURE_CROSS_ORIGIN_OPENER_POLICY`

Default: `'same-origin'`

Unless set to `None`, the
[`SecurityMiddleware`](middleware.md#django.middleware.security.SecurityMiddleware) sets the
[Cross-Origin Opener Policy](middleware.md#cross-origin-opener-policy) header on all responses that do not already
have it to the value provided.

<a id="std-setting-SECURE_CSP"></a>

### `SECURE_CSP`

#### Versionadded

Default: `{}`

This setting defines the directives used by the
[`ContentSecurityPolicyMiddleware`](middleware.md#django.middleware.csp.ContentSecurityPolicyMiddleware), which
generates and adds a [Content-Security-Policy](csp.md#csp-overview) (CSP) header
to all responses that do not already include one.

The `Content-Security-Policy` header instructs browsers to restrict which
resources a page is allowed to load. A properly configured CSP can block
content that violates defined rules, helping prevent cross-site scripting (XSS)
and other content injection attacks by explicitly declaring trusted sources for
content such as scripts, styles, images, fonts, and more.

The setting must be a mapping (typically a dictionary) of directive names to
their values. Each key should be a valid CSP directive such as `default-src`
or `script-src`. The corresponding value can be a list, tuple, or set of
source expressions or URLs to allow for that directive. If a set is used, it
will be automatically sorted to ensure consistent output in the generated
headers.

This example illustrates the expected structure, using the constants defined in
[CSP constants](csp.md#csp-constants):

```default
from django.utils.csp import CSP

SECURE_CSP = {
    "default-src": [CSP.SELF],
    "img-src": ["data:", CSP.SELF, "https://images.example.com"],
    "frame-src": [CSP.NONE],
}
```

<a id="std-setting-SECURE_CSP_REPORT_ONLY"></a>

### `SECURE_CSP_REPORT_ONLY`

#### Versionadded

Default: `{}`

This setting is just like [`SECURE_CSP`](#std-setting-SECURE_CSP), but instead of enforcing the
policy, it instructs the
[`ContentSecurityPolicyMiddleware`](middleware.md#django.middleware.csp.ContentSecurityPolicyMiddleware) to apply a
`Content-Security-Policy-Report-Only` header to responses, which allows
browsers to monitor and report policy violations without blocking content. This
is useful for testing and refining a policy before enforcement.

Most browsers log CSP violations to the developer console and can optionally
send them to a reporting endpoint. To collect these reports, the `report-uri`
directive must be defined (see [Policy violation reports](csp.md#csp-reports) for more details).

As noted in the [MDN documentation on Content-Security-Policy-Report-Only](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy-Report-Only),
the `report-uri` directive must be specified for reports to be sent;
otherwise, the header has no reporting effect (other than logging to the
browser’s developer tools console).

Following the example from the [`SECURE_CSP`](#std-setting-SECURE_CSP) setting:

```default
from django.utils.csp import CSP

SECURE_CSP_REPORT_ONLY = {
    "default-src": [CSP.SELF],
    "img-src": ["data:", CSP.SELF, "https://images.example.com"],
    "frame-src": [CSP.NONE],
    "report-uri": "/my-site/csp/reports/",
}
```

<a id="std-setting-SECURE_HSTS_INCLUDE_SUBDOMAINS"></a>

### `SECURE_HSTS_INCLUDE_SUBDOMAINS`

Default: `False`

If `True`, the [`SecurityMiddleware`](middleware.md#django.middleware.security.SecurityMiddleware) adds
the `includeSubDomains` directive to the
[HTTP Strict Transport Security](middleware.md#http-strict-transport-security) header. It has no effect unless
[`SECURE_HSTS_SECONDS`](#std-setting-SECURE_HSTS_SECONDS) is set to a non-zero value.

#### WARNING
Setting this incorrectly can irreversibly (for the value of
[`SECURE_HSTS_SECONDS`](#std-setting-SECURE_HSTS_SECONDS)) break your site. Read the
[HTTP Strict Transport Security](middleware.md#http-strict-transport-security) documentation first.

<a id="std-setting-SECURE_HSTS_PRELOAD"></a>

### `SECURE_HSTS_PRELOAD`

Default: `False`

If `True`, the [`SecurityMiddleware`](middleware.md#django.middleware.security.SecurityMiddleware) adds
the `preload` directive to the [HTTP Strict Transport Security](middleware.md#http-strict-transport-security)
header. It has no effect unless [`SECURE_HSTS_SECONDS`](#std-setting-SECURE_HSTS_SECONDS) is set to a
non-zero value.

<a id="std-setting-SECURE_HSTS_SECONDS"></a>

### `SECURE_HSTS_SECONDS`

Default: `0`

If set to a non-zero integer value, the
[`SecurityMiddleware`](middleware.md#django.middleware.security.SecurityMiddleware) sets the
[HTTP Strict Transport Security](middleware.md#http-strict-transport-security) header on all responses that do not
already have it.

#### WARNING
Setting this incorrectly can irreversibly (for some time) break your site.
Read the [HTTP Strict Transport Security](middleware.md#http-strict-transport-security) documentation first.

<a id="std-setting-SECURE_PROXY_SSL_HEADER"></a>

### `SECURE_PROXY_SSL_HEADER`

Default: `None`

A tuple representing an HTTP header/value combination that signifies a request
is secure. This controls the behavior of the request object’s `is_secure()`
method.

By default, `is_secure()` determines if a request is secure by confirming
that a requested URL uses `https://`. This method is important for Django’s
CSRF protection, and it may be used by your own code or third-party apps.

If your Django app is behind a proxy, though, the proxy may be “swallowing”
whether the original request uses HTTPS or not. If there is a non-HTTPS
connection between the proxy and Django then `is_secure()` would always
return `False` – even for requests that were made via HTTPS by the end user.
In contrast, if there is an HTTPS connection between the proxy and Django then
`is_secure()` would always return `True` – even for requests that were
made originally via HTTP.

In this situation, configure your proxy to set a custom HTTP header that tells
Django whether the request came in via HTTPS, and set
`SECURE_PROXY_SSL_HEADER` so that Django knows what header to look for.

Set a tuple with two elements – the name of the header to look for and the
required value. For example:

```default
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

This tells Django to trust the `X-Forwarded-Proto` header that comes from our
proxy and that the request is guaranteed to be secure (i.e., it originally came
in via HTTPS) when:

* the header value is `'https'`, or
* its initial, leftmost value is `'https'` in the case of a comma-separated
  list of protocols (e.g. `'https,http,http'`).

You should *only* set this setting if you control your proxy or have some other
guarantee that it sets/strips this header appropriately.

Note that the header needs to be in the format as used by `request.META` –
all caps and likely starting with `HTTP_`. (Remember, Django automatically
adds `'HTTP_'` to the start of x-header names before making the header
available in `request.META`.)

#### WARNING
**Modifying this setting can compromise your site’s security. Ensure you
fully understand your setup before changing it.**

Make sure ALL of the following are true before setting this (assuming the
values from the example above):

* Your Django app is behind a proxy.
* Your proxy strips the `X-Forwarded-Proto` header from all incoming
  requests, even when it contains a comma-separated list of protocols. In
  other words, if end users include that header in their requests, the
  proxy will discard it.
* Your proxy sets the `X-Forwarded-Proto` header and sends it to Django,
  but only for requests that originally come in via HTTPS.

If any of those are not true, you should keep this setting set to `None`
and find another way of determining HTTPS, perhaps via custom middleware.

<a id="std-setting-SECURE_REDIRECT_EXEMPT"></a>

### `SECURE_REDIRECT_EXEMPT`

Default: `[]` (Empty list)

If a URL path matches a regular expression in this list, the request will not
be redirected to HTTPS. The
[`SecurityMiddleware`](middleware.md#django.middleware.security.SecurityMiddleware) strips leading slashes
from URL paths, so patterns shouldn’t include them, e.g.
`SECURE_REDIRECT_EXEMPT = [r'^no-ssl/$', …]`. If
[`SECURE_SSL_REDIRECT`](#std-setting-SECURE_SSL_REDIRECT) is `False`, this setting has no effect.

<a id="std-setting-SECURE_REFERRER_POLICY"></a>

### `SECURE_REFERRER_POLICY`

Default: `'same-origin'`

If configured, the [`SecurityMiddleware`](middleware.md#django.middleware.security.SecurityMiddleware) sets
the [Referrer Policy](middleware.md#referrer-policy) header on all responses that do not already have it
to the value provided.

<a id="std-setting-SECURE_SSL_HOST"></a>

### `SECURE_SSL_HOST`

Default: `None`

If a string (e.g. `secure.example.com`), all SSL redirects will be directed
to this host rather than the originally-requested host (e.g.
`www.example.com`). If [`SECURE_SSL_REDIRECT`](#std-setting-SECURE_SSL_REDIRECT) is `False`, this
setting has no effect.

<a id="std-setting-SECURE_SSL_REDIRECT"></a>

### `SECURE_SSL_REDIRECT`

Default: `False`

If `True`, the [`SecurityMiddleware`](middleware.md#django.middleware.security.SecurityMiddleware)
[redirects](middleware.md#ssl-redirect) all non-HTTPS requests to HTTPS (except for
those URLs matching a regular expression listed in
[`SECURE_REDIRECT_EXEMPT`](#std-setting-SECURE_REDIRECT_EXEMPT)).

#### NOTE
If turning this to `True` causes infinite redirects, it probably means
your site is running behind a proxy and can’t tell which requests are secure
and which are not. Your proxy likely sets a header to indicate secure
requests; you can correct the problem by finding out what that header is and
configuring the [`SECURE_PROXY_SSL_HEADER`](#std-setting-SECURE_PROXY_SSL_HEADER) setting accordingly.

<a id="std-setting-SERIALIZATION_MODULES"></a>

### `SERIALIZATION_MODULES`

Default: Not defined

A dictionary of modules containing serializer definitions (provided as
strings), keyed by a string identifier for that serialization type. For
example, to define a YAML serializer, use:

```default
SERIALIZATION_MODULES = {"yaml": "path.to.yaml_serializer"}
```

<a id="std-setting-SERVER_EMAIL"></a>

### `SERVER_EMAIL`

Default: `'root@localhost'`

The email address that error messages come from, such as those sent to
[`ADMINS`](#std-setting-ADMINS) and [`MANAGERS`](#std-setting-MANAGERS). This address is used in the
`From:` header and can take any format valid in the chosen email sending
protocol.

<a id="std-setting-SHORT_DATE_FORMAT"></a>

### `SHORT_DATE_FORMAT`

Default: `'m/d/Y'` (e.g. `12/31/2003`)

An available formatting that can be used for displaying date fields on
templates. Note that the corresponding locale-dictated format has higher
precedence and will be applied instead. See
[`allowed date format strings`](templates/builtins.md#std-templatefilter-date).

See also [`DATE_FORMAT`](#std-setting-DATE_FORMAT) and [`SHORT_DATETIME_FORMAT`](#std-setting-SHORT_DATETIME_FORMAT).

<a id="std-setting-SHORT_DATETIME_FORMAT"></a>

### `SHORT_DATETIME_FORMAT`

Default: `'m/d/Y P'` (e.g. `12/31/2003 4 p.m.`)

An available formatting that can be used for displaying datetime fields on
templates. Note that the corresponding locale-dictated format has higher
precedence and will be applied instead. See
[`allowed date format strings`](templates/builtins.md#std-templatefilter-date).

See also [`DATE_FORMAT`](#std-setting-DATE_FORMAT) and [`SHORT_DATE_FORMAT`](#std-setting-SHORT_DATE_FORMAT).

<a id="std-setting-SIGNING_BACKEND"></a>

### `SIGNING_BACKEND`

Default: `'django.core.signing.TimestampSigner'`

The backend used for signing cookies and other data.

See also the [Cryptographic signing](../topics/signing.md) documentation.

<a id="std-setting-SILENCED_SYSTEM_CHECKS"></a>

### `SILENCED_SYSTEM_CHECKS`

Default: `[]` (Empty list)

A list of identifiers of messages generated by the system check framework
(i.e. `["models.W001"]`) that you wish to permanently acknowledge and ignore.
Silenced checks will not be output to the console.

See also the [System check framework](checks.md) documentation.

<a id="std-setting-STORAGES"></a>

### `STORAGES`

Default:

```default
{
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```

A dictionary containing the settings for all storages to be used with Django.
It is a nested dictionary whose contents map a storage alias to a dictionary
containing the options for an individual storage.

Storages can have any alias you choose. However, there are two aliases with
special significance:

* `default` for [managing files](../topics/files.md).
  `'`[`django.core.files.storage.FileSystemStorage`](files/storage.md#django.core.files.storage.FileSystemStorage)`'` is the
  default storage engine.
* `staticfiles` for [managing static files](contrib/staticfiles.md).
  `'`[`django.contrib.staticfiles.storage.StaticFilesStorage`](contrib/staticfiles.md#django.contrib.staticfiles.storage.StaticFilesStorage)`'` is
  the default storage engine.

The following is an example `settings.py` snippet defining a custom file
storage called `example`:

```default
STORAGES = {
    # ...
    "example": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": "/example",
            "base_url": "/example/",
        },
    },
}
```

`OPTIONS` are passed to the `BACKEND` on initialization in `**kwargs`.

A ready-to-use instance of the storage backends can be retrieved from
[`django.core.files.storage.storages`](files/storage.md#django.core.files.storage.storages). Use a key corresponding to the
backend definition in [`STORAGES`](#std-setting-STORAGES).

<a id="std-setting-TASKS"></a>

### `TASKS`

#### Versionadded

Default:

```default
{
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
    }
}
```

A dictionary containing the settings for all Task backends to be used with
Django. It is a nested dictionary whose contents maps backend aliases to a
dictionary containing the options for each backend.

The [`TASKS`](#std-setting-TASKS) setting must configure a `default` backend; any number
of additional backends may also be specified. Depending on which backend is
used, other options may be required. The following options are available as
standard.

<a id="std-setting-TASKS-BACKEND"></a>

#### `BACKEND`

Default: `''` (Empty string)

The Tasks backend to use. The built-in backends are:

* `'django.tasks.backends.dummy.DummyBackend'`
* `'django.tasks.backends.immediate.ImmediateBackend'`

You can use a backend that doesn’t ship with Django by setting
[`BACKEND`](#std-setting-TASKS-BACKEND) to a fully-qualified path of a backend
class (i.e. `mypackage.backends.whatever.WhateverBackend`).

<a id="std-setting-TASKS-QUEUES"></a>

#### `QUEUES`

Default: `["default"]`

Specify the queue names supported by the backend. This can be used to ensure
Tasks aren’t enqueued to queues which do not exist.

To disable queue name validation, set to an empty list (`[]`).

<a id="std-setting-TASKS-OPTIONS"></a>

#### `OPTIONS`

Default: `{}`

Extra parameters to pass to the Task backend. Available parameters vary
depending on the Task backend.

<a id="std-setting-TEMPLATES"></a>

### `TEMPLATES`

Default: `[]` (Empty list)

A list containing the settings for all template engines to be used with
Django. Each item of the list is a dictionary containing the options for an
individual engine.

Here’s a setup that tells the Django template engine to load templates from the
`templates` subdirectory inside each installed application:

```default
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    },
]
```

The following options are available for all backends.

<a id="std-setting-TEMPLATES-BACKEND"></a>

#### `BACKEND`

Default: Not defined

The template backend to use. The built-in template backends are:

* `'django.template.backends.django.DjangoTemplates'`
* `'django.template.backends.jinja2.Jinja2'`

You can use a template backend that doesn’t ship with Django by setting
`BACKEND` to a fully-qualified path (i.e. `'mypackage.whatever.Backend'`).

<a id="std-setting-TEMPLATES-NAME"></a>

#### `NAME`

Default: see below

The alias for this particular template engine. It’s an identifier that allows
selecting an engine for rendering. Aliases must be unique across all
configured template engines.

It defaults to the name of the module defining the engine class, i.e. the
next to last piece of [`BACKEND`](#std-setting-TEMPLATES-BACKEND), when it isn’t
provided. For example if the backend is `'mypackage.whatever.Backend'` then
its default name is `'whatever'`.

<a id="std-setting-TEMPLATES-DIRS"></a>

#### `DIRS`

Default: `[]` (Empty list)

Directories where the engine should look for template source files, in search
order.

<a id="std-setting-TEMPLATES-APP_DIRS"></a>

#### `APP_DIRS`

Default: `False`

Whether the engine should look for template source files inside installed
applications.

#### NOTE
The default `settings.py` file created by [`django-admin
startproject`](django-admin.md#django-admin-startproject) sets `'APP_DIRS': True`.

<a id="std-setting-TEMPLATES-OPTIONS"></a>

#### `OPTIONS`

Default: `{}` (Empty dict)

Extra parameters to pass to the template backend. Available parameters vary
depending on the template backend. See
[`DjangoTemplates`](../topics/templates.md#django.template.backends.django.DjangoTemplates) and
[`Jinja2`](../topics/templates.md#django.template.backends.jinja2.Jinja2) for the options of the
built-in backends.

<a id="std-setting-TEST_RUNNER"></a>

### `TEST_RUNNER`

Default: `'django.test.runner.DiscoverRunner'`

The name of the class to use for starting the test suite. See
[Using different testing frameworks](../topics/testing/advanced.md#other-testing-frameworks).

<a id="std-setting-TEST_NON_SERIALIZED_APPS"></a>

### `TEST_NON_SERIALIZED_APPS`

Default: `[]` (Empty list)

In order to restore the database state between tests for
`TransactionTestCase`s and database backends without transactions, Django
will [serialize the contents of all apps](../topics/testing/overview.md#test-case-serialized-rollback)
when it starts the test run so it can then reload from that copy before running
tests that need it.

This slows down the startup time of the test runner; if you have apps that
you know don’t need this feature, you can add their full names in here (e.g.
`'django.contrib.contenttypes'`) to exclude them from this serialization
process.

<a id="std-setting-THOUSAND_SEPARATOR"></a>

### `THOUSAND_SEPARATOR`

Default: `','` (Comma)

Default thousand separator used when formatting numbers. This setting is
used only when [`USE_THOUSAND_SEPARATOR`](#std-setting-USE_THOUSAND_SEPARATOR) is `True` and
[`NUMBER_GROUPING`](#std-setting-NUMBER_GROUPING) is greater than `0`.

Note that the locale-dictated format has higher precedence and will be applied
instead.

See also [`NUMBER_GROUPING`](#std-setting-NUMBER_GROUPING), [`DECIMAL_SEPARATOR`](#std-setting-DECIMAL_SEPARATOR) and
[`USE_THOUSAND_SEPARATOR`](#std-setting-USE_THOUSAND_SEPARATOR).

<a id="std-setting-TIME_FORMAT"></a>

### `TIME_FORMAT`

Default: `'P'` (e.g. `4 p.m.`)

The default formatting to use for displaying time fields in any part of the
system. Note that the locale-dictated format has higher precedence and will be
applied instead. See [`allowed date format strings`](templates/builtins.md#std-templatefilter-date).

See also [`DATE_FORMAT`](#std-setting-DATE_FORMAT) and [`DATETIME_FORMAT`](#std-setting-DATETIME_FORMAT).

<a id="std-setting-TIME_INPUT_FORMATS"></a>

### `TIME_INPUT_FORMATS`

Default:

```default
[
    "%H:%M:%S",  # '14:30:59'
    "%H:%M:%S.%f",  # '14:30:59.000200'
    "%H:%M",  # '14:30'
]
```

A list of formats that will be accepted when inputting data on a time field.
Formats will be tried in order, using the first valid one. Note that these
format strings use Python’s [datetime module syntax](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior), not the format strings from the [`date`](templates/builtins.md#std-templatefilter-date)
template filter.

The locale-dictated format has higher precedence and will be applied instead.

See also [`DATE_INPUT_FORMATS`](#std-setting-DATE_INPUT_FORMATS) and [`DATETIME_INPUT_FORMATS`](#std-setting-DATETIME_INPUT_FORMATS).

<a id="std-setting-TIME_ZONE"></a>

### `TIME_ZONE`

Default: `'America/Chicago'`

A string representing the time zone for this installation. See the [list of
time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

#### NOTE
Since Django was first released with the [`TIME_ZONE`](#std-setting-TIME_ZONE) set to
`'America/Chicago'`, the global setting (used if nothing is defined in
your project’s `settings.py`) remains `'America/Chicago'` for backwards
compatibility. New project templates default to `'UTC'`.

Note that this isn’t necessarily the time zone of the server. For example, one
server may serve multiple Django-powered sites, each with a separate time zone
setting.

When [`USE_TZ`](#std-setting-USE_TZ) is `False`, this is the time zone in which Django
will store all datetimes. When [`USE_TZ`](#std-setting-USE_TZ) is `True`, this is the
default time zone that Django will use to display datetimes in templates and
to interpret datetimes entered in forms.

On Unix environments (where [`time.tzset()`](https://docs.python.org/3/library/time.html#time.tzset) is implemented), Django sets the
`os.environ['TZ']` variable to the time zone you specify in the
[`TIME_ZONE`](#std-setting-TIME_ZONE) setting. Thus, all your views and models will
automatically operate in this time zone. However, Django won’t set the `TZ`
environment variable if you’re using the manual configuration option as
described in [manually configuring settings](../topics/settings.md#settings-without-django-settings-module). If Django doesn’t set the `TZ`
environment variable, it’s up to you to ensure your processes are running in
the correct environment.

#### NOTE
Django cannot reliably use alternate time zones in a Windows environment.
If you’re running Django on Windows, [`TIME_ZONE`](#std-setting-TIME_ZONE) must be set to
match the system time zone.

<a id="std-setting-USE_I18N"></a>

### `USE_I18N`

Default: `True`

A boolean that specifies whether Django’s translation system should be enabled.
This provides a way to turn it off, for performance. If this is set to
`False`, Django will make some optimizations so as not to load the
translation machinery.

See also [`LANGUAGE_CODE`](#std-setting-LANGUAGE_CODE) and [`USE_TZ`](#std-setting-USE_TZ).

#### NOTE
The default `settings.py` file created by [`django-admin
startproject`](django-admin.md#django-admin-startproject) includes `USE_I18N = True` for convenience.

<a id="std-setting-USE_THOUSAND_SEPARATOR"></a>

### `USE_THOUSAND_SEPARATOR`

Default: `False`

A boolean that specifies whether to display numbers using a thousand separator.
When set to `True`, Django will format numbers using the
[`NUMBER_GROUPING`](#std-setting-NUMBER_GROUPING) and [`THOUSAND_SEPARATOR`](#std-setting-THOUSAND_SEPARATOR) settings. The
latter two settings may also be dictated by the locale, which takes precedence.

See also [`DECIMAL_SEPARATOR`](#std-setting-DECIMAL_SEPARATOR), [`NUMBER_GROUPING`](#std-setting-NUMBER_GROUPING) and
[`THOUSAND_SEPARATOR`](#std-setting-THOUSAND_SEPARATOR).

<a id="std-setting-USE_TZ"></a>

### `USE_TZ`

Default: `True`

A boolean that specifies if datetimes will be timezone-aware by default or not.
If this is set to `True`, Django will use timezone-aware datetimes
internally.

When `USE_TZ` is False, Django will use naive datetimes in local time, except
when parsing ISO 8601 formatted strings, where timezone information will always
be retained if present.

See also [`TIME_ZONE`](#std-setting-TIME_ZONE) and [`USE_I18N`](#std-setting-USE_I18N).

<a id="std-setting-USE_X_FORWARDED_HOST"></a>

### `USE_X_FORWARDED_HOST`

Default: `False`

A boolean that specifies whether to use the `X-Forwarded-Host` header in
preference to the `Host` header. This should only be enabled if a proxy
which sets this header is in use.

This setting takes priority over [`USE_X_FORWARDED_PORT`](#std-setting-USE_X_FORWARDED_PORT). Per
[**RFC 7239 Section 5.3**](https://datatracker.ietf.org/doc/html/rfc7239.html#section-5.3), the `X-Forwarded-Host` header can include the port
number, in which case you shouldn’t use [`USE_X_FORWARDED_PORT`](#std-setting-USE_X_FORWARDED_PORT).

<a id="std-setting-USE_X_FORWARDED_PORT"></a>

### `USE_X_FORWARDED_PORT`

Default: `False`

A boolean that specifies whether to use the `X-Forwarded-Port` header in
preference to the `SERVER_PORT` `META` variable. This should only be
enabled if a proxy which sets this header is in use.

[`USE_X_FORWARDED_HOST`](#std-setting-USE_X_FORWARDED_HOST) takes priority over this setting.

<a id="std-setting-URLIZE_ASSUME_HTTPS"></a>

### `URLIZE_ASSUME_HTTPS`

#### Versionadded

#### Deprecated
Deprecated since version 6.0.

Default: `False`

Set this transitional setting to `True` to opt into using HTTPS as the
default protocol when none is provided in URLs processed by the
[`urlize`](templates/builtins.md#std-templatefilter-urlize) and [`urlizetrunc`](templates/builtins.md#std-templatefilter-urlizetrunc) template filters during the Django
6.x release cycle.

<a id="std-setting-WSGI_APPLICATION"></a>

### `WSGI_APPLICATION`

Default: `None`

The full Python path of the WSGI application object that Django’s built-in
servers (e.g. [`runserver`](django-admin.md#django-admin-runserver)) will use. The [`django-admin
startproject`](django-admin.md#django-admin-startproject) management command will create a standard
`wsgi.py` file with an `application` callable in it, and point this setting
to that `application`.

If not set, the return value of `django.core.wsgi.get_wsgi_application()`
will be used. In this case, the behavior of [`runserver`](django-admin.md#django-admin-runserver) will be
identical to previous Django versions.

<a id="std-setting-YEAR_MONTH_FORMAT"></a>

### `YEAR_MONTH_FORMAT`

Default: `'F Y'`

The default formatting to use for date fields on Django admin change-list
pages – and, possibly, by other parts of the system – in cases when only the
year and month are displayed.

For example, when a Django admin change-list page is being filtered by a date
drilldown, the header for a given month displays the month and the year.
Different locales have different formats. For example, U.S. English would say
“January 2006,” whereas another locale might say “2006/January.”

Note that the corresponding locale-dictated format has higher precedence and
will be applied instead.

See [`allowed date format strings`](templates/builtins.md#std-templatefilter-date). See also
[`DATE_FORMAT`](#std-setting-DATE_FORMAT), [`DATETIME_FORMAT`](#std-setting-DATETIME_FORMAT), [`TIME_FORMAT`](#std-setting-TIME_FORMAT)
and [`MONTH_DAY_FORMAT`](#std-setting-MONTH_DAY_FORMAT).

<a id="std-setting-X_FRAME_OPTIONS"></a>

### `X_FRAME_OPTIONS`

Default: `'DENY'`

The default value for the X-Frame-Options header used by
[`XFrameOptionsMiddleware`](middleware.md#django.middleware.clickjacking.XFrameOptionsMiddleware). See the
[clickjacking protection](clickjacking.md) documentation.

## Auth

Settings for [`django.contrib.auth`](../topics/auth/index.md#module-django.contrib.auth).

<a id="std-setting-AUTHENTICATION_BACKENDS"></a>

### `AUTHENTICATION_BACKENDS`

Default: `['django.contrib.auth.backends.ModelBackend']`

A list of authentication backend classes (as strings) to use when attempting to
authenticate a user. See the [authentication backends documentation](../topics/auth/customizing.md#authentication-backends) for details.

<a id="std-setting-AUTH_USER_MODEL"></a>

### `AUTH_USER_MODEL`

Default: `'auth.User'`

The model to use to represent a User. See [Substituting a custom User model](../topics/auth/customizing.md#auth-custom-user).

#### WARNING
You cannot change the AUTH_USER_MODEL setting during the lifetime of
a project (i.e. once you have made and migrated models that depend on it)
without serious effort. It is intended to be set at the project start,
and the model it refers to must be available in the first migration of
the app that it lives in.
See [Substituting a custom User model](../topics/auth/customizing.md#auth-custom-user) for more details.

<a id="std-setting-LOGIN_REDIRECT_URL"></a>

### `LOGIN_REDIRECT_URL`

Default: `'/accounts/profile/'`

The URL or [named URL pattern](../topics/http/urls.md#naming-url-patterns) where requests are
redirected after login when the [`LoginView`](../topics/auth/default.md#django.contrib.auth.views.LoginView)
doesn’t get a `next` GET parameter.

<a id="std-setting-LOGIN_URL"></a>

### `LOGIN_URL`

Default: `'/accounts/login/'`

The URL or [named URL pattern](../topics/http/urls.md#naming-url-patterns) where requests are
redirected for login when using the
[`login_required()`](../topics/auth/default.md#django.contrib.auth.decorators.login_required) decorator,
[`LoginRequiredMixin`](../topics/auth/default.md#django.contrib.auth.mixins.LoginRequiredMixin),
[`AccessMixin`](../topics/auth/default.md#django.contrib.auth.mixins.AccessMixin), or when
[`LoginRequiredMiddleware`](middleware.md#django.contrib.auth.middleware.LoginRequiredMiddleware) is installed.

<a id="std-setting-LOGOUT_REDIRECT_URL"></a>

### `LOGOUT_REDIRECT_URL`

Default: `None`

The URL or [named URL pattern](../topics/http/urls.md#naming-url-patterns) where requests are
redirected after logout if [`LogoutView`](../topics/auth/default.md#django.contrib.auth.views.LogoutView)
doesn’t have a `next_page` attribute.

If `None`, no redirect will be performed and the logout view will be
rendered.

<a id="std-setting-PASSWORD_RESET_TIMEOUT"></a>

### `PASSWORD_RESET_TIMEOUT`

Default: `259200` (3 days, in seconds)

The number of seconds a password reset link is valid for.

Used by the [`PasswordResetConfirmView`](../topics/auth/default.md#django.contrib.auth.views.PasswordResetConfirmView).

#### NOTE
Reducing the value of this timeout doesn’t make any difference to the
ability of an attacker to brute-force a password reset token. Tokens are
designed to be safe from brute-forcing without any timeout.

This timeout exists to protect against some unlikely attack scenarios, such
as someone gaining access to email archives that may contain old, unused
password reset tokens.

<a id="std-setting-PASSWORD_HASHERS"></a>

### `PASSWORD_HASHERS`

See [How Django stores passwords](../topics/auth/passwords.md#auth-password-storage).

Default:

```default
[
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]
```

<a id="std-setting-AUTH_PASSWORD_VALIDATORS"></a>

### `AUTH_PASSWORD_VALIDATORS`

Default: `[]` (Empty list)

The list of validators that are used to check the strength of user’s passwords.
See [Password validation](../topics/auth/passwords.md#password-validation) for more details. By default, no validation is
performed and all passwords are accepted.

<a id="settings-messages"></a>

## Messages

Settings for [`django.contrib.messages`](contrib/messages.md#module-django.contrib.messages).

<a id="std-setting-MESSAGE_LEVEL"></a>

### `MESSAGE_LEVEL`

Default: `messages.INFO`

Sets the minimum message level that will be recorded by the messages
framework. See [message levels](contrib/messages.md#message-level) for more details.

<a id="std-setting-MESSAGE_STORAGE"></a>

### `MESSAGE_STORAGE`

Default: `'django.contrib.messages.storage.fallback.FallbackStorage'`

Controls where Django stores message data. Valid values are:

* `'django.contrib.messages.storage.fallback.FallbackStorage'`
* `'django.contrib.messages.storage.session.SessionStorage'`
* `'django.contrib.messages.storage.cookie.CookieStorage'`

See [message storage backends](contrib/messages.md#message-storage-backends) for more
details.

The backends that use cookies –
[`CookieStorage`](contrib/messages.md#django.contrib.messages.storage.cookie.CookieStorage) and
[`FallbackStorage`](contrib/messages.md#django.contrib.messages.storage.fallback.FallbackStorage) –
use the value of [`SESSION_COOKIE_DOMAIN`](#std-setting-SESSION_COOKIE_DOMAIN),
[`SESSION_COOKIE_SECURE`](#std-setting-SESSION_COOKIE_SECURE) and [`SESSION_COOKIE_HTTPONLY`](#std-setting-SESSION_COOKIE_HTTPONLY) when
setting their cookies.

<a id="std-setting-MESSAGE_TAGS"></a>

### `MESSAGE_TAGS`

Default:

```default
{
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}
```

This sets the mapping of message level to message tag, which is typically
rendered as a CSS class in HTML. If you specify a value, it will extend
the default. This means you only have to specify those values which you need
to override. See [Displaying messages](contrib/messages.md#message-displaying) above for more details.

<a id="settings-sessions"></a>

## Sessions

Settings for [`django.contrib.sessions`](../topics/http/sessions.md#module-django.contrib.sessions).

<a id="std-setting-SESSION_CACHE_ALIAS"></a>

### `SESSION_CACHE_ALIAS`

Default: `'default'`

If you’re using [cache-based session storage](../topics/http/sessions.md#cached-sessions-backend),
this selects the cache to use.

<a id="std-setting-SESSION_COOKIE_AGE"></a>

### `SESSION_COOKIE_AGE`

Default: `1209600` (2 weeks, in seconds)

The age of session cookies, in seconds.

<a id="std-setting-SESSION_COOKIE_DOMAIN"></a>

### `SESSION_COOKIE_DOMAIN`

Default: `None`

The domain to use for session cookies. Set this to a string such as
`"example.com"` for cross-domain cookies, or use `None` for a standard
domain cookie.

To use cross-domain cookies with [`CSRF_USE_SESSIONS`](#std-setting-CSRF_USE_SESSIONS), you must include
a leading dot (e.g. `".example.com"`) to accommodate the CSRF middleware’s
referer checking.

Be cautious when updating this setting on a production site. If you update
this setting to enable cross-domain cookies on a site that previously used
standard domain cookies, existing user cookies will be set to the old
domain. This may result in them being unable to log in as long as these cookies
persist.

This setting also affects cookies set by [`django.contrib.messages`](contrib/messages.md#module-django.contrib.messages).

<a id="std-setting-SESSION_COOKIE_HTTPONLY"></a>

### `SESSION_COOKIE_HTTPONLY`

Default: `True`

Whether to use `HttpOnly` flag on the session cookie. If this is set to
`True`, client-side JavaScript will not be able to access the session
cookie.

[HttpOnly](https://owasp.org/www-community/HttpOnly) is a flag included in a Set-Cookie HTTP response header. It’s part of
the [**RFC 6265 Section 4.1.2.6**](https://datatracker.ietf.org/doc/html/rfc6265.html#section-4.1.2.6) standard for cookies and can be a useful way to
mitigate the risk of a client-side script accessing the protected cookie data.

This makes it less trivial for an attacker to escalate a cross-site scripting
vulnerability into full hijacking of a user’s session. There aren’t many good
reasons for turning this off. Your code shouldn’t read session cookies from
JavaScript.

<a id="std-setting-SESSION_COOKIE_NAME"></a>

### `SESSION_COOKIE_NAME`

Default: `'sessionid'`

The name of the cookie to use for sessions. This can be whatever you want
(as long as it’s different from the other cookie names in your application).

<a id="std-setting-SESSION_COOKIE_PATH"></a>

### `SESSION_COOKIE_PATH`

Default: `'/'`

The path set on the session cookie. This should either match the URL path of
your Django installation or be parent of that path.

This is useful if you have multiple Django instances running under the same
hostname. They can use different cookie paths, and each instance will only see
its own session cookie.

<a id="std-setting-SESSION_COOKIE_SAMESITE"></a>

### `SESSION_COOKIE_SAMESITE`

Default: `'Lax'`

The value of the [SameSite](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value) flag on the session cookie. This flag prevents the
cookie from being sent in cross-site requests thus preventing CSRF attacks and
making some methods of stealing session cookie impossible.

Possible values for the setting are:

* `'Strict'`: prevents the cookie from being sent by the browser to the
  target site in all cross-site browsing context, even when following a regular
  link.

  For example, for a GitHub-like website this would mean that if a logged-in
  user follows a link to a private GitHub project posted on a corporate
  discussion forum or email, GitHub will not receive the session cookie and the
  user won’t be able to access the project. A bank website, however, most
  likely doesn’t want to allow any transactional pages to be linked from
  external sites so the `'Strict'` flag would be appropriate.
* `'Lax'` (default): provides a balance between security and usability for
  websites that want to maintain user’s logged-in session after the user
  arrives from an external link.

  In the GitHub scenario, the session cookie would be allowed when following a
  regular link from an external website and be blocked in CSRF-prone request
  methods (e.g. `POST`).
* `'None'` (string): the session cookie will be sent with all same-site and
  cross-site requests.
* `False`: disables the flag.

#### NOTE
Modern browsers provide a more secure default policy for the `SameSite`
flag and will assume `Lax` for cookies without an explicit value set.

<a id="std-setting-SESSION_COOKIE_SECURE"></a>

### `SESSION_COOKIE_SECURE`

Default: `False`

Whether to use a secure cookie for the session cookie. If this is set to
`True`, the cookie will be marked as “secure”, which means browsers may
ensure that the cookie is only sent under an HTTPS connection.

Leaving this setting off isn’t a good idea because an attacker could capture an
unencrypted session cookie with a packet sniffer and use the cookie to hijack
the user’s session.

<a id="std-setting-SESSION_ENGINE"></a>

### `SESSION_ENGINE`

Default: `'django.contrib.sessions.backends.db'`

Controls where Django stores session data. Included engines are:

* `'django.contrib.sessions.backends.db'`
* `'django.contrib.sessions.backends.file'`
* `'django.contrib.sessions.backends.cache'`
* `'django.contrib.sessions.backends.cached_db'`
* `'django.contrib.sessions.backends.signed_cookies'`

See [Configuring the session engine](../topics/http/sessions.md#configuring-sessions) for more details.

<a id="std-setting-SESSION_EXPIRE_AT_BROWSER_CLOSE"></a>

### `SESSION_EXPIRE_AT_BROWSER_CLOSE`

Default: `False`

Whether to expire the session when the user closes their browser. See
[Browser-length sessions vs. persistent sessions](../topics/http/sessions.md#browser-length-vs-persistent-sessions).

<a id="std-setting-SESSION_FILE_PATH"></a>

### `SESSION_FILE_PATH`

Default: `None`

If you’re using file-based session storage, this sets the directory in
which Django will store session data. When the default value (`None`) is
used, Django will use the standard temporary directory for the system.

<a id="std-setting-SESSION_SAVE_EVERY_REQUEST"></a>

### `SESSION_SAVE_EVERY_REQUEST`

Default: `False`

Whether to save the session data on every request. If this is `False`
(default), then the session data will only be saved if it has been modified –
that is, if any of its dictionary values have been assigned or deleted. Empty
sessions won’t be created, even if this setting is active.

<a id="std-setting-SESSION_SERIALIZER"></a>

### `SESSION_SERIALIZER`

Default: `'django.contrib.sessions.serializers.JSONSerializer'`

Full import path of a serializer class to use for serializing session data.
Included serializer is:

* `'django.contrib.sessions.serializers.JSONSerializer'`

See [Session serialization](../topics/http/sessions.md#session-serialization) for details.

## Sites

Settings for [`django.contrib.sites`](contrib/sites.md#module-django.contrib.sites).

<a id="std-setting-SITE_ID"></a>

### `SITE_ID`

Default: Not defined

The ID, as an integer, of the current site in the `django_site` database
table. This is used so that application data can hook into specific sites
and a single database can manage content for multiple sites.

<a id="settings-staticfiles"></a>

## Static Files

Settings for [`django.contrib.staticfiles`](contrib/staticfiles.md#module-django.contrib.staticfiles).

<a id="std-setting-STATIC_ROOT"></a>

### `STATIC_ROOT`

Default: `None`

The absolute path to the directory where [`collectstatic`](contrib/staticfiles.md#django-admin-collectstatic) will collect
static files for deployment.

Example: `"/var/www/example.com/static/"`

If the [staticfiles](contrib/staticfiles.md) contrib app is enabled
(as in the default project template), the [`collectstatic`](contrib/staticfiles.md#django-admin-collectstatic) management
command will collect static files into this directory. See the how-to on
[managing static files](../howto/static-files/index.md) for more details about
usage.

#### WARNING
This should be an initially empty destination directory for collecting
your static files from their permanent locations into one directory for
ease of deployment; it is **not** a place to store your static files
permanently. You should do that in directories that will be found by
[staticfiles](contrib/staticfiles.md)’s
[`finders`](#std-setting-STATICFILES_FINDERS), which by default, are
`'static/'` app sub-directories and any directories you include in
[`STATICFILES_DIRS`](#std-setting-STATICFILES_DIRS)).

<a id="std-setting-STATIC_URL"></a>

### `STATIC_URL`

Default: `None`

URL to use when referring to static files located in [`STATIC_ROOT`](#std-setting-STATIC_ROOT).

Example: `"static/"` or `"https://static.example.com/"`

If not `None`, this will be used as the base path for
[asset definitions](../topics/forms/media.md#form-asset-paths) (the `Media` class) and the
[staticfiles app](contrib/staticfiles.md).

It must end in a slash if set to a non-empty value.

You may need to [configure these files to be served in development](../howto/static-files/index.md#serving-static-files-in-development) and will definitely need to do so
[in production](../howto/static-files/deployment.md).

#### NOTE
If [`STATIC_URL`](#std-setting-STATIC_URL) is a relative path, then it will be prefixed by
the server-provided value of `SCRIPT_NAME` (or `/` if not set). This
makes it easier to serve a Django application in a subpath without adding
an extra configuration to the settings.

<a id="std-setting-STATICFILES_DIRS"></a>

### `STATICFILES_DIRS`

Default: `[]` (Empty list)

This setting defines the additional locations the staticfiles app will traverse
if the `FileSystemFinder` finder is enabled, e.g. if you use the
[`collectstatic`](contrib/staticfiles.md#django-admin-collectstatic) or [`findstatic`](contrib/staticfiles.md#django-admin-findstatic) management command or use the
static file serving view.

This should be set to a list of strings that contain full paths to
your additional files directory(ies) e.g.:

```default
STATICFILES_DIRS = [
    "/home/special.polls.com/polls/static",
    "/home/polls.com/polls/static",
    "/opt/webfiles/common",
]
```

Note that these paths should use Unix-style forward slashes, even on Windows
(e.g. `"C:/Users/user/mysite/extra_static_content"`).

<a id="staticfiles-dirs-prefixes"></a>

#### Prefixes (optional)

In case you want to refer to files in one of the locations with an additional
namespace, you can **optionally** provide a prefix as `(prefix, path)`
tuples, e.g.:

```default
STATICFILES_DIRS = [
    # ...
    ("downloads", "/opt/webfiles/stats"),
]
```

For example, assuming you have [`STATIC_URL`](#std-setting-STATIC_URL) set to `'static/'`, the
[`collectstatic`](contrib/staticfiles.md#django-admin-collectstatic) management command would collect the “stats” files
in a `'downloads'` subdirectory of [`STATIC_ROOT`](#std-setting-STATIC_ROOT).

This would allow you to refer to the local file
`'/opt/webfiles/stats/polls_20101022.tar.gz'` with
`'/static/downloads/polls_20101022.tar.gz'` in your templates, e.g.:

```html+django
<a href="{% static 'downloads/polls_20101022.tar.gz' %}">
```

<a id="std-setting-STATICFILES_FINDERS"></a>

### `STATICFILES_FINDERS`

Default:

```default
[
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
```

The list of finder backends that know how to find static files in
various locations.

The default will find files stored in the [`STATICFILES_DIRS`](#std-setting-STATICFILES_DIRS) setting
(using `django.contrib.staticfiles.finders.FileSystemFinder`) and in a
`static` subdirectory of each app (using
`django.contrib.staticfiles.finders.AppDirectoriesFinder`). If multiple
files with the same name are present, the first file that is found will be
used.

One finder is disabled by default:
`django.contrib.staticfiles.finders.DefaultStorageFinder`. If added to
your [`STATICFILES_FINDERS`](#std-setting-STATICFILES_FINDERS) setting, it will look for static files in
the default file storage as defined by the `default` key in the
[`STORAGES`](#std-setting-STORAGES) setting.

#### NOTE
When using the `AppDirectoriesFinder` finder, make sure your apps
can be found by staticfiles by adding the app to the
[`INSTALLED_APPS`](#std-setting-INSTALLED_APPS) setting of your site.

Static file finders are currently considered a private interface, and this
interface is thus undocumented.

## Core Settings Topical Index

### Cache

* [`CACHES`](#std-setting-CACHES)
* [`CACHE_MIDDLEWARE_ALIAS`](#std-setting-CACHE_MIDDLEWARE_ALIAS)
* [`CACHE_MIDDLEWARE_KEY_PREFIX`](#std-setting-CACHE_MIDDLEWARE_KEY_PREFIX)
* [`CACHE_MIDDLEWARE_SECONDS`](#std-setting-CACHE_MIDDLEWARE_SECONDS)

### Database

* [`DATABASES`](#std-setting-DATABASES)
* [`DATABASE_ROUTERS`](#std-setting-DATABASE_ROUTERS)
* [`DEFAULT_INDEX_TABLESPACE`](#std-setting-DEFAULT_INDEX_TABLESPACE)
* [`DEFAULT_TABLESPACE`](#std-setting-DEFAULT_TABLESPACE)

### Debugging

* [`DEBUG`](#std-setting-DEBUG)
* [`DEBUG_PROPAGATE_EXCEPTIONS`](#std-setting-DEBUG_PROPAGATE_EXCEPTIONS)

### Email

* [`ADMINS`](#std-setting-ADMINS)
* [`DEFAULT_CHARSET`](#std-setting-DEFAULT_CHARSET)
* [`DEFAULT_FROM_EMAIL`](#std-setting-DEFAULT_FROM_EMAIL)
* [`EMAIL_BACKEND`](#std-setting-EMAIL_BACKEND)
* [`EMAIL_FILE_PATH`](#std-setting-EMAIL_FILE_PATH)
* [`EMAIL_HOST`](#std-setting-EMAIL_HOST)
* [`EMAIL_HOST_PASSWORD`](#std-setting-EMAIL_HOST_PASSWORD)
* [`EMAIL_HOST_USER`](#std-setting-EMAIL_HOST_USER)
* [`EMAIL_PORT`](#std-setting-EMAIL_PORT)
* [`EMAIL_SSL_CERTFILE`](#std-setting-EMAIL_SSL_CERTFILE)
* [`EMAIL_SSL_KEYFILE`](#std-setting-EMAIL_SSL_KEYFILE)
* [`EMAIL_SUBJECT_PREFIX`](#std-setting-EMAIL_SUBJECT_PREFIX)
* [`EMAIL_TIMEOUT`](#std-setting-EMAIL_TIMEOUT)
* [`EMAIL_USE_LOCALTIME`](#std-setting-EMAIL_USE_LOCALTIME)
* [`EMAIL_USE_SSL`](#std-setting-EMAIL_USE_SSL)
* [`EMAIL_USE_TLS`](#std-setting-EMAIL_USE_TLS)
* [`MANAGERS`](#std-setting-MANAGERS)
* [`SERVER_EMAIL`](#std-setting-SERVER_EMAIL)

### Error reporting

* [`DEFAULT_EXCEPTION_REPORTER`](#std-setting-DEFAULT_EXCEPTION_REPORTER)
* [`DEFAULT_EXCEPTION_REPORTER_FILTER`](#std-setting-DEFAULT_EXCEPTION_REPORTER_FILTER)
* [`IGNORABLE_404_URLS`](#std-setting-IGNORABLE_404_URLS)
* [`MANAGERS`](#std-setting-MANAGERS)
* [`SILENCED_SYSTEM_CHECKS`](#std-setting-SILENCED_SYSTEM_CHECKS)

<a id="file-upload-settings"></a>

### File uploads

* [`FILE_UPLOAD_HANDLERS`](#std-setting-FILE_UPLOAD_HANDLERS)
* [`FILE_UPLOAD_MAX_MEMORY_SIZE`](#std-setting-FILE_UPLOAD_MAX_MEMORY_SIZE)
* [`FILE_UPLOAD_PERMISSIONS`](#std-setting-FILE_UPLOAD_PERMISSIONS)
* [`FILE_UPLOAD_TEMP_DIR`](#std-setting-FILE_UPLOAD_TEMP_DIR)
* [`MEDIA_ROOT`](#std-setting-MEDIA_ROOT)
* [`MEDIA_URL`](#std-setting-MEDIA_URL)
* [`STORAGES`](#std-setting-STORAGES)

### Forms

* [`FORM_RENDERER`](#std-setting-FORM_RENDERER)

### Globalization (`i18n`/`l10n`)

<a id="settings-i18n"></a>

#### Internationalization (`i18n`)

* [`FIRST_DAY_OF_WEEK`](#std-setting-FIRST_DAY_OF_WEEK)
* [`FORMAT_MODULE_PATH`](#std-setting-FORMAT_MODULE_PATH)
* [`LANGUAGE_COOKIE_AGE`](#std-setting-LANGUAGE_COOKIE_AGE)
* [`LANGUAGE_COOKIE_DOMAIN`](#std-setting-LANGUAGE_COOKIE_DOMAIN)
* [`LANGUAGE_COOKIE_HTTPONLY`](#std-setting-LANGUAGE_COOKIE_HTTPONLY)
* [`LANGUAGE_COOKIE_NAME`](#std-setting-LANGUAGE_COOKIE_NAME)
* [`LANGUAGE_COOKIE_PATH`](#std-setting-LANGUAGE_COOKIE_PATH)
* [`LANGUAGE_COOKIE_SAMESITE`](#std-setting-LANGUAGE_COOKIE_SAMESITE)
* [`LANGUAGE_COOKIE_SECURE`](#std-setting-LANGUAGE_COOKIE_SECURE)
* [`LANGUAGES`](#std-setting-LANGUAGES)
* [`LANGUAGES_BIDI`](#std-setting-LANGUAGES_BIDI)
* [`LOCALE_PATHS`](#std-setting-LOCALE_PATHS)
* [`TIME_ZONE`](#std-setting-TIME_ZONE)
* [`USE_I18N`](#std-setting-USE_I18N)
* [`USE_TZ`](#std-setting-USE_TZ)

<a id="settings-l10n"></a>

#### Localization (`l10n`)

* [`DATE_FORMAT`](#std-setting-DATE_FORMAT)
* [`DATE_INPUT_FORMATS`](#std-setting-DATE_INPUT_FORMATS)
* [`DATETIME_FORMAT`](#std-setting-DATETIME_FORMAT)
* [`DATETIME_INPUT_FORMATS`](#std-setting-DATETIME_INPUT_FORMATS)
* [`DECIMAL_SEPARATOR`](#std-setting-DECIMAL_SEPARATOR)
* [`LANGUAGE_CODE`](#std-setting-LANGUAGE_CODE)
* [`MONTH_DAY_FORMAT`](#std-setting-MONTH_DAY_FORMAT)
* [`NUMBER_GROUPING`](#std-setting-NUMBER_GROUPING)
* [`SHORT_DATE_FORMAT`](#std-setting-SHORT_DATE_FORMAT)
* [`SHORT_DATETIME_FORMAT`](#std-setting-SHORT_DATETIME_FORMAT)
* [`THOUSAND_SEPARATOR`](#std-setting-THOUSAND_SEPARATOR)
* [`TIME_FORMAT`](#std-setting-TIME_FORMAT)
* [`TIME_INPUT_FORMATS`](#std-setting-TIME_INPUT_FORMATS)
* [`USE_THOUSAND_SEPARATOR`](#std-setting-USE_THOUSAND_SEPARATOR)
* [`YEAR_MONTH_FORMAT`](#std-setting-YEAR_MONTH_FORMAT)

### HTTP

* [`DATA_UPLOAD_MAX_MEMORY_SIZE`](#std-setting-DATA_UPLOAD_MAX_MEMORY_SIZE)
* [`DATA_UPLOAD_MAX_NUMBER_FIELDS`](#std-setting-DATA_UPLOAD_MAX_NUMBER_FIELDS)
* [`DATA_UPLOAD_MAX_NUMBER_FILES`](#std-setting-DATA_UPLOAD_MAX_NUMBER_FILES)
* [`DEFAULT_CHARSET`](#std-setting-DEFAULT_CHARSET)
* [`DISALLOWED_USER_AGENTS`](#std-setting-DISALLOWED_USER_AGENTS)
* [`FORCE_SCRIPT_NAME`](#std-setting-FORCE_SCRIPT_NAME)
* [`INTERNAL_IPS`](#std-setting-INTERNAL_IPS)
* [`MIDDLEWARE`](#std-setting-MIDDLEWARE)
* Security
  * [`SECURE_CONTENT_TYPE_NOSNIFF`](#std-setting-SECURE_CONTENT_TYPE_NOSNIFF)
  * [`SECURE_CROSS_ORIGIN_OPENER_POLICY`](#std-setting-SECURE_CROSS_ORIGIN_OPENER_POLICY)
  * [`SECURE_CSP`](#std-setting-SECURE_CSP)
  * [`SECURE_CSP_REPORT_ONLY`](#std-setting-SECURE_CSP_REPORT_ONLY)
  * [`SECURE_HSTS_INCLUDE_SUBDOMAINS`](#std-setting-SECURE_HSTS_INCLUDE_SUBDOMAINS)
  * [`SECURE_HSTS_PRELOAD`](#std-setting-SECURE_HSTS_PRELOAD)
  * [`SECURE_HSTS_SECONDS`](#std-setting-SECURE_HSTS_SECONDS)
  * [`SECURE_PROXY_SSL_HEADER`](#std-setting-SECURE_PROXY_SSL_HEADER)
  * [`SECURE_REDIRECT_EXEMPT`](#std-setting-SECURE_REDIRECT_EXEMPT)
  * [`SECURE_REFERRER_POLICY`](#std-setting-SECURE_REFERRER_POLICY)
  * [`SECURE_SSL_HOST`](#std-setting-SECURE_SSL_HOST)
  * [`SECURE_SSL_REDIRECT`](#std-setting-SECURE_SSL_REDIRECT)
* [`SIGNING_BACKEND`](#std-setting-SIGNING_BACKEND)
* [`USE_X_FORWARDED_HOST`](#std-setting-USE_X_FORWARDED_HOST)
* [`USE_X_FORWARDED_PORT`](#std-setting-USE_X_FORWARDED_PORT)
* [`WSGI_APPLICATION`](#std-setting-WSGI_APPLICATION)

### Logging

* [`LOGGING`](#std-setting-LOGGING)
* [`LOGGING_CONFIG`](#std-setting-LOGGING_CONFIG)

### Models

* [`ABSOLUTE_URL_OVERRIDES`](#std-setting-ABSOLUTE_URL_OVERRIDES)
* [`FIXTURE_DIRS`](#std-setting-FIXTURE_DIRS)
* [`INSTALLED_APPS`](#std-setting-INSTALLED_APPS)

### Security

* Cross Site Request Forgery Protection
  * [`CSRF_COOKIE_DOMAIN`](#std-setting-CSRF_COOKIE_DOMAIN)
  * [`CSRF_COOKIE_NAME`](#std-setting-CSRF_COOKIE_NAME)
  * [`CSRF_COOKIE_PATH`](#std-setting-CSRF_COOKIE_PATH)
  * [`CSRF_COOKIE_SAMESITE`](#std-setting-CSRF_COOKIE_SAMESITE)
  * [`CSRF_COOKIE_SECURE`](#std-setting-CSRF_COOKIE_SECURE)
  * [`CSRF_FAILURE_VIEW`](#std-setting-CSRF_FAILURE_VIEW)
  * [`CSRF_HEADER_NAME`](#std-setting-CSRF_HEADER_NAME)
  * [`CSRF_TRUSTED_ORIGINS`](#std-setting-CSRF_TRUSTED_ORIGINS)
  * [`CSRF_USE_SESSIONS`](#std-setting-CSRF_USE_SESSIONS)
* [`SECRET_KEY`](#std-setting-SECRET_KEY)
* [`SECRET_KEY_FALLBACKS`](#std-setting-SECRET_KEY_FALLBACKS)
* [`URLIZE_ASSUME_HTTPS`](#std-setting-URLIZE_ASSUME_HTTPS)
* [`X_FRAME_OPTIONS`](#std-setting-X_FRAME_OPTIONS)

### Serialization

* [`DEFAULT_CHARSET`](#std-setting-DEFAULT_CHARSET)
* [`SERIALIZATION_MODULES`](#std-setting-SERIALIZATION_MODULES)

### Templates

* [`TEMPLATES`](#std-setting-TEMPLATES)

### Testing

* Database: [`TEST`](#std-setting-DATABASE-TEST)
* [`TEST_NON_SERIALIZED_APPS`](#std-setting-TEST_NON_SERIALIZED_APPS)
* [`TEST_RUNNER`](#std-setting-TEST_RUNNER)

### URLs

* [`APPEND_SLASH`](#std-setting-APPEND_SLASH)
* [`PREPEND_WWW`](#std-setting-PREPEND_WWW)
* [`ROOT_URLCONF`](#std-setting-ROOT_URLCONF)

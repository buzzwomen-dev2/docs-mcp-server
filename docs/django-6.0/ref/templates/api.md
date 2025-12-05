# The Django template language: for Python programmers

This document explains the Django template system from a technical
perspective – how it works and how to extend it. If you’re looking for
reference on the language syntax, see [The Django template language](language.md).

It assumes an understanding of templates, contexts, variables, tags, and
rendering. Start with the [introduction to the Django template language](../../topics/templates.md#template-language-intro) if you aren’t familiar with these concepts.

## Overview

Using the template system in Python is a three-step process:

1. You configure an [`Engine`](#django.template.Engine).
2. You compile template code into a [`Template`](#django.template.Template).
3. You render the template with a [`Context`](#django.template.Context).

Django projects generally rely on the [high level, backend agnostic APIs](../../topics/templates.md#template-engines) for each of these steps instead of the template system’s
lower level APIs:

1. For each [`DjangoTemplates`](../../topics/templates.md#django.template.backends.django.DjangoTemplates) backend
   in the [`TEMPLATES`](../settings.md#std-setting-TEMPLATES) setting, Django instantiates an
   [`Engine`](#django.template.Engine). [`DjangoTemplates`](../../topics/templates.md#django.template.backends.django.DjangoTemplates)
   wraps [`Engine`](#django.template.Engine) and adapts it to the common template backend API.
2. The [`django.template.loader`](../../topics/templates.md#module-django.template.loader) module provides functions such as
   [`get_template()`](../../topics/templates.md#django.template.loader.get_template) for loading templates. They
   return a `django.template.backends.django.Template` which wraps the
   actual [`django.template.Template`](#django.template.Template).
3. The `Template` obtained in the previous step has a
   [`render()`](../../topics/templates.md#django.template.backends.base.Template.render) method which
   marshals a context and possibly a request into a [`Context`](#django.template.Context) and
   delegates the rendering to the underlying [`Template`](#django.template.Template).

## Configuring an engine

If you are using the [`DjangoTemplates`](../../topics/templates.md#django.template.backends.django.DjangoTemplates)
backend, this probably isn’t the documentation you’re looking for. An instance
of the `Engine` class described below is accessible using the `engine`
attribute of that backend and any attribute defaults mentioned below are
overridden by what’s passed by
[`DjangoTemplates`](../../topics/templates.md#django.template.backends.django.DjangoTemplates).

### *class* Engine(dirs=None, app_dirs=False, context_processors=None, debug=False, loaders=None, string_if_invalid='', file_charset='utf-8', libraries=None, builtins=None, autoescape=True)

When instantiating an `Engine` all arguments must be passed as keyword
arguments:

* `dirs` is a list of directories where the engine should look for
  template source files. It is used to configure
  [`filesystem.Loader`](#django.template.loaders.filesystem.Loader).

  It defaults to an empty list.
* `app_dirs` only affects the default value of `loaders`. See below.

  It defaults to `False`.
* `autoescape` controls whether HTML autoescaping is enabled.

  It defaults to `True`.

  #### WARNING
  Only set it to `False` if you’re rendering non-HTML templates!
* `context_processors` is a list of dotted Python paths to callables
  that are used to populate the context when a template is rendered with a
  request. These callables take a request object as their argument and
  return a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) of items to be merged into the context.

  It defaults to an empty list.

  See [`RequestContext`](#django.template.RequestContext) for more information.
* `debug` is a boolean that turns on/off template debug mode. If it is
  `True`, the template engine will store additional debug information
  which can be used to display a detailed report for any exception raised
  during template rendering.

  It defaults to `False`.
* `loaders` is a list of template loader classes, specified as strings.
  Each `Loader` class knows how to import templates from a particular
  source. Optionally, a tuple can be used instead of a string. The first
  item in the tuple should be the `Loader` class name, subsequent items
  are passed to the `Loader` during initialization.

  It defaults to a list containing:
  * `'django.template.loaders.filesystem.Loader'`
  * `'django.template.loaders.app_directories.Loader'` if and only if
    `app_dirs` is `True`.

  These loaders are then wrapped in
  [`django.template.loaders.cached.Loader`](#django.template.loaders.cached.Loader).

  See [Loader types](#template-loaders) for details.
* `string_if_invalid` is the output, as a string, that the template
  system should use for invalid (e.g. misspelled) variables.

  It defaults to the empty string.

  See [How invalid variables are handled](#invalid-template-variables) for details.
* `file_charset` is the charset used to read template files on disk.

  It defaults to `'utf-8'`.
* `'libraries'`: A dictionary of labels and dotted Python paths of
  template tag modules to register with the template engine. This is used
  to add new libraries or provide alternate labels for existing ones. For
  example:
  ```default
  Engine(
      libraries={
          "myapp_tags": "path.to.myapp.tags",
          "admin.urls": "django.contrib.admin.templatetags.admin_urls",
      },
  )
  ```

  Libraries can be loaded by passing the corresponding dictionary key to
  the [`{% load %}`](builtins.md#std-templatetag-load) tag.
* `'builtins'`: A list of dotted Python paths of template tag modules to
  add to [built-ins](builtins.md). For example:
  ```default
  Engine(
      builtins=["myapp.builtins"],
  )
  ```

  Tags and filters from built-in libraries can be used without first
  calling the [`{% load %}`](builtins.md#std-templatetag-load) tag.

#### *static* Engine.get_default()

Returns the underlying [`Engine`](#django.template.Engine) from the first configured
[`DjangoTemplates`](../../topics/templates.md#django.template.backends.django.DjangoTemplates) engine. Raises
[`ImproperlyConfigured`](../exceptions.md#django.core.exceptions.ImproperlyConfigured) if no engines are
configured.

It’s required for preserving APIs that rely on a globally available,
implicitly configured engine. Any other use is strongly discouraged.

#### Engine.from_string(template_code)

Compiles the given template code and returns a [`Template`](#django.template.Template) object.

#### Engine.get_template(template_name)

Loads a template with the given name, compiles it and returns a
[`Template`](#django.template.Template) object.

#### Engine.select_template(template_name_list)

Like [`get_template()`](#django.template.Engine.get_template), except it takes a list of names
and returns the first template that was found.

## Loading a template

The recommended way to create a [`Template`](#django.template.Template) is by calling the factory
methods of the [`Engine`](#django.template.Engine): [`get_template()`](#django.template.Engine.get_template),
[`select_template()`](#django.template.Engine.select_template) and [`from_string()`](#django.template.Engine.from_string).

In a Django project where the [`TEMPLATES`](../settings.md#std-setting-TEMPLATES) setting defines a
[`DjangoTemplates`](../../topics/templates.md#django.template.backends.django.DjangoTemplates) engine, it’s
possible to instantiate a [`Template`](#django.template.Template) directly. If more than one
[`DjangoTemplates`](../../topics/templates.md#django.template.backends.django.DjangoTemplates) engine is defined,
the first one will be used.

### *class* Template

This class lives at `django.template.Template`. The constructor takes
one argument — the raw template code:

```default
from django.template import Template

template = Template("My name is {{ my_name }}.")
```

## Rendering a context

Once you have a compiled [`Template`](#django.template.Template) object, you can render a context
with it. You can reuse the same template to render it several times with
different contexts.

### *class* Context(dict_=None, autoescape=True, use_l10n=None, use_tz=None)

The constructor of `django.template.Context` takes an optional argument —
a dictionary mapping variable names to variable values.

Three optional keyword arguments can also be specified:

* `autoescape` controls whether HTML autoescaping is enabled.

  It defaults to `True`.

  #### WARNING
  Only set it to `False` if you’re rendering non-HTML templates!
* `use_l10n` overrides whether values will be localized by default. If
  set to `True` numbers and dates will be formatted based on locale.

  It defaults to `None`.

  See [Controlling localization in templates](../../topics/i18n/formatting.md#topic-l10n-templates) for details.
* `use_tz` overrides whether dates are converted to the local time when
  rendered in a template. If set to `True` all dates will be rendered
  using the local timezone. This takes precedence over [`USE_TZ`](../settings.md#std-setting-USE_TZ).

  It defaults to `None`.

  See [Time zone aware output in templates](../../topics/i18n/timezones.md#time-zones-in-templates) for details.

For example usage, see [Playing with Context objects](#playing-with-context) below.

#### Template.render(context)

Call the [`Template`](#django.template.Template) object’s `render()` method with a
[`Context`](#django.template.Context) to “fill” the template:

```pycon
>>> from django.template import Context, Template
>>> template = Template("My name is {{ my_name }}.")

>>> context = Context({"my_name": "Adrian"})
>>> template.render(context)
"My name is Adrian."

>>> context = Context({"my_name": "Dolores"})
>>> template.render(context)
"My name is Dolores."
```

### Variables and lookups

Variable names must consist of any letter (A-Z), any digit (0-9), an underscore
(but they must not start with an underscore) or a dot.

Dots have a special meaning in template rendering. A dot in a variable name
signifies a **lookup**. Specifically, when the template system encounters a
dot in a variable name, it tries the following lookups, in this order:

* Dictionary lookup. Example: `foo["bar"]`
* Attribute lookup. Example: `foo.bar`
* List-index lookup. Example: `foo[bar]`

Note that “bar” in a template expression like `{{ foo.bar }}` will be
interpreted as a literal string and not using the value of the variable “bar”,
if one exists in the template context.

The template system uses the first lookup type that works. It’s short-circuit
logic. Here are a few examples:

```pycon
>>> from django.template import Context, Template
>>> t = Template("My name is {{ person.first_name }}.")
>>> d = {"person": {"first_name": "Joe", "last_name": "Johnson"}}
>>> t.render(Context(d))
"My name is Joe."

>>> class PersonClass:
...     pass
...
>>> p = PersonClass()
>>> p.first_name = "Ron"
>>> p.last_name = "Nasty"
>>> t.render(Context({"person": p}))
"My name is Ron."

>>> t = Template("The first stooge in the list is {{ stooges.0 }}.")
>>> c = Context({"stooges": ["Larry", "Curly", "Moe"]})
>>> t.render(c)
"The first stooge in the list is Larry."
```

If any part of the variable is callable, the template system will try calling
it. Example:

```pycon
>>> class PersonClass2:
...     def name(self):
...         return "Samantha"
...
>>> t = Template("My name is {{ person.name }}.")
>>> t.render(Context({"person": PersonClass2}))
"My name is Samantha."
```

Callable variables are slightly more complex than variables which only require
straight lookups. Here are some things to keep in mind:

* If the variable raises an exception when called, the exception will be
  propagated, unless the exception has an attribute
  `silent_variable_failure` whose value is `True`. If the exception
  *does* have a `silent_variable_failure` attribute whose value is
  `True`, the variable will render as the value of the engine’s
  `string_if_invalid` configuration option (an empty string, by default).
  Example:
  ```pycon
  >>> t = Template("My name is {{ person.first_name }}.")
  >>> class PersonClass3:
  ...     def first_name(self):
  ...         raise AssertionError("foo")
  ...
  >>> p = PersonClass3()
  >>> t.render(Context({"person": p}))
  Traceback (most recent call last):
  ...
  AssertionError: foo

  >>> class SilentAssertionError(Exception):
  ...     silent_variable_failure = True
  ...
  >>> class PersonClass4:
  ...     def first_name(self):
  ...         raise SilentAssertionError
  ...
  >>> p = PersonClass4()
  >>> t.render(Context({"person": p}))
  "My name is ."
  ```

  Note that [`django.core.exceptions.ObjectDoesNotExist`](../exceptions.md#django.core.exceptions.ObjectDoesNotExist), which is the
  base class for all Django database API `DoesNotExist` exceptions, has
  `silent_variable_failure = True`. So if you’re using Django templates
  with Django model objects, any `DoesNotExist` exception will fail
  silently.
* A variable can only be called if it has no required arguments. Otherwise,
  the system will return the value of the engine’s `string_if_invalid`
  option.

<a id="alters-data-description"></a>
* There can be side effects when calling some variables, and it’d be either
  foolish or a security hole to allow the template system to access them.

  A good example is the [`delete()`](../models/instances.md#django.db.models.Model.delete) method on
  each Django model object. The template system shouldn’t be allowed to do
  something like this:
  ```html+django
  I will now delete this valuable data. {{ data.delete }}
  ```

  To prevent this, set an `alters_data` attribute on the callable
  variable. The template system won’t call a variable if it has
  `alters_data=True` set, and will instead replace the variable with
  `string_if_invalid`, unconditionally. The
  dynamically-generated [`delete()`](../models/instances.md#django.db.models.Model.delete) and
  [`save()`](../models/instances.md#django.db.models.Model.save) methods on Django model objects get
  `alters_data=True` automatically. Example:
  ```default
  def sensitive_function(self):
      self.database_record.delete()


  sensitive_function.alters_data = True
  ```
* Occasionally you may want to turn off this feature for other reasons,
  and tell the template system to leave a variable uncalled no matter
  what. To do so, set a `do_not_call_in_templates` attribute on the
  callable with the value `True`. The template system then will act as
  if your variable is not callable (allowing you to access attributes of
  the callable, for example).

<a id="invalid-template-variables"></a>

### How invalid variables are handled

Generally, if a variable doesn’t exist, the template system inserts the value
of the engine’s `string_if_invalid` configuration option, which is set to
`''` (the empty string) by default.

Filters that are applied to an invalid variable will only be applied if
`string_if_invalid` is set to `''` (the empty string). If
`string_if_invalid` is set to any other value, variable filters will be
ignored.

This behavior is slightly different for the `if`, `for` and `regroup`
template tags. If an invalid variable is provided to one of these template
tags, the variable will be interpreted as `None`. Filters are always
applied to invalid variables within these template tags.

If `string_if_invalid` contains a `'%s'`, the format marker will be
replaced with the name of the invalid variable.

### Built-in variables

Every context contains `True`, `False` and `None`. As you would expect,
these variables resolve to the corresponding Python objects.

### Limitations with string literals

Django’s template language has no way to escape the characters used for its own
syntax. For example, the [`templatetag`](builtins.md#std-templatetag-templatetag) tag is required if you need to
output character sequences like `{%` and `%}`.

A similar issue exists if you want to include these sequences in template
filter or tag arguments. For example, when parsing a block tag, Django’s
template parser looks for the first occurrence of `%}` after a `{%`. This
prevents the use of `"%}"` as a string literal. For example, a
`TemplateSyntaxError` will be raised for the following expressions:

```html+django
{% include "template.html" tvar="Some string literal with %} in it." %}

{% with tvar="Some string literal with %} in it." %}{% endwith %}
```

The same issue can be triggered by using a reserved sequence in filter
arguments:

```html+django
{{ some.variable|default:"}}" }}
```

If you need to use strings with these sequences, store them in template
variables or use a custom template tag or filter to workaround the limitation.

<a id="playing-with-context"></a>

## Playing with `Context` objects

Most of the time, you’ll instantiate [`Context`](#django.template.Context) objects by passing in a
fully-populated dictionary to `Context()`. But you can add and delete items
from a `Context` object once it’s been instantiated, too, using standard
dictionary syntax:

```pycon
>>> from django.template import Context
>>> c = Context({"foo": "bar"})
>>> c["foo"]
'bar'
>>> del c["foo"]
>>> c["foo"]
Traceback (most recent call last):
...
KeyError: 'foo'
>>> c["newvariable"] = "hello"
>>> c["newvariable"]
'hello'
```

#### Context.get(key, otherwise=None)

Returns the value for `key` if `key` is in the context, else returns
`otherwise`.

#### Context.setdefault(key, default=None)

If `key` is in the context, returns its value. Otherwise inserts `key`
with a value of `default` and returns `default`.

#### Context.pop()

#### Context.push()

### *exception* ContextPopException

A `Context` object is a stack. That is, you can `push()` and `pop()` it.
If you `pop()` too much, it’ll raise
`django.template.ContextPopException`:

```pycon
>>> c = Context()
>>> c["foo"] = "first level"
>>> c.push()
{}
>>> c["foo"] = "second level"
>>> c["foo"]
'second level'
>>> c.pop()
{'foo': 'second level'}
>>> c["foo"]
'first level'
>>> c["foo"] = "overwritten"
>>> c["foo"]
'overwritten'
>>> c.pop()
Traceback (most recent call last):
...
ContextPopException
```

You can also use `push()` as a context manager to ensure a matching `pop()`
is called.

```pycon
>>> c = Context()
>>> c["foo"] = "first level"
>>> with c.push():
...     c["foo"] = "second level"
...     c["foo"]
...
'second level'
>>> c["foo"]
'first level'
```

All arguments passed to `push()` will be passed to the `dict` constructor
used to build the new context level.

```pycon
>>> c = Context()
>>> c["foo"] = "first level"
>>> with c.push(foo="second level"):
...     c["foo"]
...
'second level'
>>> c["foo"]
'first level'
```

#### Context.update(other_dict)

In addition to `push()` and `pop()`, the `Context`
object also defines an `update()` method. This works like `push()`
but takes a dictionary as an argument and pushes that dictionary onto
the stack instead of an empty one.

```pycon
>>> c = Context()
>>> c["foo"] = "first level"
>>> c.update({"foo": "updated"})
{'foo': 'updated'}
>>> c["foo"]
'updated'
>>> c.pop()
{'foo': 'updated'}
>>> c["foo"]
'first level'
```

Like `push()`, you can use `update()` as a context manager to ensure a
matching `pop()` is called.

```pycon
>>> c = Context()
>>> c["foo"] = "first level"
>>> with c.update({"foo": "second level"}):
...     c["foo"]
...
'second level'
>>> c["foo"]
'first level'
```

Using a `Context` as a stack comes in handy in [some custom template
tags](../../howto/custom-template-tags.md#howto-writing-custom-template-tags).

#### Context.flatten()

Using `flatten()` method you can get whole `Context` stack as one
dictionary including builtin variables.

```pycon
>>> c = Context()
>>> c["foo"] = "first level"
>>> c.update({"bar": "second level"})
{'bar': 'second level'}
>>> c.flatten()
{'True': True, 'None': None, 'foo': 'first level', 'False': False, 'bar': 'second level'}
```

A `flatten()` method is also internally used to make `Context` objects
comparable.

```pycon
>>> c1 = Context()
>>> c1["foo"] = "first level"
>>> c1["bar"] = "second level"
>>> c2 = Context()
>>> c2.update({"bar": "second level", "foo": "first level"})
{'foo': 'first level', 'bar': 'second level'}
>>> c1 == c2
True
```

Result from `flatten()` can be useful in unit tests to compare `Context`
against `dict`:

```default
class ContextTest(unittest.TestCase):
    def test_against_dictionary(self):
        c1 = Context()
        c1["update"] = "value"
        self.assertEqual(
            c1.flatten(),
            {
                "True": True,
                "None": None,
                "False": False,
                "update": "value",
            },
        )
```

<a id="subclassing-context-requestcontext"></a>

### Using `RequestContext`

### *class* RequestContext(request, dict_=None, processors=None, use_l10n=None, use_tz=None, autoescape=True)

Django comes with a special [`Context`](#django.template.Context) class,
`django.template.RequestContext`, that acts slightly differently from the
normal `django.template.Context`. The first difference is that it takes an
[`HttpRequest`](../request-response.md#django.http.HttpRequest) as its first argument. For example:

```default
c = RequestContext(
    request,
    {
        "foo": "bar",
    },
)
```

The second difference is that it automatically populates the context with a
few variables, according to the engine’s `context_processors` configuration
option.

The `context_processors` option is a list of callables – called **context
processors** – that take a request object as their argument and return a
dictionary of items to be merged into the context. In the default generated
settings file, the default template engine contains the following context
processors:

```default
[
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
]
```

In addition to these, [`RequestContext`](#django.template.RequestContext) always enables
`'django.template.context_processors.csrf'`. This is a security related
context processor required by the admin and other contrib apps, and, in case
of accidental misconfiguration, it is deliberately hardcoded in and cannot be
turned off in the `context_processors` option.

Each processor is applied in order. That means, if one processor adds a
variable to the context and a second processor adds a variable with the same
name, the second will override the first. The default processors are explained
below.

Also, you can give [`RequestContext`](#django.template.RequestContext) a list of additional processors,
using the optional, third positional argument, `processors`. In this
example, the [`RequestContext`](#django.template.RequestContext) instance gets an `ip_address` variable:

```default
from django.http import HttpResponse
from django.template import RequestContext, Template


def ip_address_processor(request):
    return {"ip_address": request.META["REMOTE_ADDR"]}


def client_ip_view(request):
    template = Template("{{ title }}: {{ ip_address }}")
    context = RequestContext(
        request,
        {
            "title": "Your IP Address",
        },
        [ip_address_processor],
    )
    return HttpResponse(template.render(context))
```

<a id="context-processors"></a>

### Built-in template context processors

Here’s what each of the built-in processors does:

#### `django.contrib.auth.context_processors.auth`

### auth(request)

If this processor is enabled, every `RequestContext` will contain these
variables:

* `user` – An `auth.User` instance representing the currently
  logged-in user (or an `AnonymousUser` instance, if the client isn’t
  logged in).
* `perms` – An instance of
  `django.contrib.auth.context_processors.PermWrapper`, representing the
  permissions that the currently logged-in user has.

#### `django.template.context_processors.debug`

### debug(request)

If this processor is enabled, every `RequestContext` will contain these two
variables – but only if your [`DEBUG`](../settings.md#std-setting-DEBUG) setting is set to `True` and
the request’s IP address (`request.META['REMOTE_ADDR']`) is in the
[`INTERNAL_IPS`](../settings.md#std-setting-INTERNAL_IPS) setting:

* `debug` – `True`. You can use this in templates to test whether
  you’re in [`DEBUG`](../settings.md#std-setting-DEBUG) mode.
* `sql_queries` – A list of `{'sql': ..., 'time': ...}` dictionaries,
  representing every SQL query that has happened so far during the request
  and how long it took. The list is in order by database alias and then by
  query. It’s lazily generated on access.

#### `django.template.context_processors.i18n`

### i18n(request)

If this processor is enabled, every `RequestContext` will contain these
variables:

* `LANGUAGES` – The value of the [`LANGUAGES`](../settings.md#std-setting-LANGUAGES) setting.
* `LANGUAGE_BIDI` – `True` if the current language is a right-to-left
  language, e.g. Hebrew, Arabic. `False` if it’s a left-to-right language,
  e.g. English, French, German.
* `LANGUAGE_CODE` – `request.LANGUAGE_CODE`, if it exists. Otherwise,
  the value of the [`LANGUAGE_CODE`](../settings.md#std-setting-LANGUAGE_CODE) setting.

See [i18n template tags](../../topics/i18n/translation.md#i18n-template-tags) for template tags that
generate the same values.

#### `django.template.context_processors.media`

If this processor is enabled, every `RequestContext` will contain a variable
`MEDIA_URL`, providing the value of the [`MEDIA_URL`](../settings.md#std-setting-MEDIA_URL) setting.

#### `django.template.context_processors.static`

### static(request)

If this processor is enabled, every `RequestContext` will contain a variable
`STATIC_URL`, providing the value of the [`STATIC_URL`](../settings.md#std-setting-STATIC_URL) setting.

#### `django.template.context_processors.csrf`

This processor adds a token that is needed by the [`csrf_token`](builtins.md#std-templatetag-csrf_token) template
tag for protection against [Cross Site Request Forgeries](../csrf.md).

#### `django.template.context_processors.csp`

### csp(request)

#### Versionadded

If this processor is enabled, every `RequestContext` will contain a variable
`csp_nonce`, providing a securely generated, request-specific nonce suitable
for use under a Content Security Policy. See [CSP nonce usage](../csp.md#csp-nonce)
for details.

#### `django.template.context_processors.request`

If this processor is enabled, every `RequestContext` will contain a variable
`request`, which is the current [`HttpRequest`](../request-response.md#django.http.HttpRequest).

#### `django.template.context_processors.tz`

### tz(request)

If this processor is enabled, every `RequestContext` will contain a variable
`TIME_ZONE`, providing the name of the currently active time zone.

#### `django.contrib.messages.context_processors.messages`

If this processor is enabled, every `RequestContext` will contain these two
variables:

* `messages` – A list of messages (as strings) that have been set
  via the [messages framework](../contrib/messages.md).
* `DEFAULT_MESSAGE_LEVELS` – A mapping of the message level names to
  [their numeric value](../contrib/messages.md#message-level-constants).

### Writing your own context processors

A context processor has a simple interface: It’s a Python function that takes
one argument, an [`HttpRequest`](../request-response.md#django.http.HttpRequest) object, and returns a
dictionary that gets added to the template context.

For example, to add the [`DEFAULT_FROM_EMAIL`](../settings.md#std-setting-DEFAULT_FROM_EMAIL) setting to every
context:

```default
from django.conf import settings


def from_email(request):
    return {
        "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
    }
```

Custom context processors can live anywhere in your code base. All Django
cares about is that your custom context processors are pointed to by the
`'context_processors'` option in your [`TEMPLATES`](../settings.md#std-setting-TEMPLATES) setting — or the
`context_processors` argument of [`Engine`](#django.template.Engine) if you’re
using it directly.

## Loading templates

Generally, you’ll store templates in files on your filesystem rather than
using the low-level [`Template`](#django.template.Template) API yourself. Save
templates in a directory specified as a **template directory**.

Django searches for template directories in a number of places, depending on
your template loading settings (see “Loader types” below), but the most basic
way of specifying template directories is by using the [`DIRS`](../settings.md#std-setting-TEMPLATES-DIRS) option.

### The [`DIRS`](../settings.md#std-setting-TEMPLATES-DIRS) option

Tell Django what your template directories are by using the [`DIRS`](../settings.md#std-setting-TEMPLATES-DIRS) option in the [`TEMPLATES`](../settings.md#std-setting-TEMPLATES) setting in your settings
file — or the `dirs` argument of [`Engine`](#django.template.Engine). This
should be set to a list of strings that contain full paths to your template
directories:

```default
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "/home/html/templates/lawrence.com",
            "/home/html/templates/default",
        ],
    },
]
```

Your templates can go anywhere you want, as long as the directories and
templates are readable by the web server. They can have any extension you want,
such as `.html` or `.txt`, or they can have no extension at all.

Note that these paths should use Unix-style forward slashes, even on Windows.

<a id="template-loaders"></a>

### Loader types

By default, Django uses a filesystem-based template loader, but Django comes
with a few other template loaders, which know how to load templates from other
sources.

Some of these other loaders are disabled by default, but you can activate them
by adding a `'loaders'` option to your `DjangoTemplates` backend in the
[`TEMPLATES`](../settings.md#std-setting-TEMPLATES) setting or passing a `loaders` argument to
[`Engine`](#django.template.Engine). `loaders` should be a list of strings or
tuples, where each represents a template loader class. Here are the template
loaders that come with Django:

`django.template.loaders.filesystem.Loader`

#### *class* filesystem.Loader

Loads templates from the filesystem, according to
[`DIRS`](../settings.md#std-setting-TEMPLATES-DIRS).

This loader is enabled by default. However it won’t find any templates
until you set [`DIRS`](../settings.md#std-setting-TEMPLATES-DIRS) to a non-empty list:

```default
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
    }
]
```

You can also override `'DIRS'` and specify specific directories for a
particular filesystem loader:

```default
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.filesystem.Loader",
                    [BASE_DIR / "templates"],
                ),
            ],
        },
    }
]
```

`django.template.loaders.app_directories.Loader`

#### *class* app_directories.Loader

Loads templates from Django apps on the filesystem. For each app in
[`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS), the loader looks for a `templates`
subdirectory. If the directory exists, Django looks for templates in there.

This means you can store templates with your individual apps. This also
helps to distribute Django apps with default templates.

For example, for this setting:

```default
INSTALLED_APPS = ["myproject.polls", "myproject.music"]
```

…then `get_template('foo.html')` will look for `foo.html` in these
directories, in this order:

* `/path/to/myproject/polls/templates/`
* `/path/to/myproject/music/templates/`

… and will use the one it finds first.

The order of [`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS) is significant! For example, if you
want to customize the Django admin, you might choose to override the
standard `admin/base_site.html` template, from `django.contrib.admin`,
with your own `admin/base_site.html` in `myproject.polls`. You must
then make sure that your `myproject.polls` comes *before*
`django.contrib.admin` in [`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS), otherwise
`django.contrib.admin`’s will be loaded first and yours will be ignored.

Note that the loader performs an optimization when it first runs:
it caches a list of which [`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS) packages have a
`templates` subdirectory.

You can enable this loader by setting [`APP_DIRS`](../settings.md#std-setting-TEMPLATES-APP_DIRS) to `True`:

```default
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    }
]
```

`django.template.loaders.cached.Loader`

#### *class* cached.Loader

While the Django template system is quite fast, if it needs to read and
compile your templates every time they’re rendered, the overhead from that
can add up.

You configure the cached template loader with a list of other loaders that
it should wrap. The wrapped loaders are used to locate unknown templates
when they’re first encountered. The cached loader then stores the compiled
`Template` in memory. The cached `Template` instance is returned for
subsequent requests to load the same template.

This loader is automatically enabled if [`OPTIONS['loaders']`](../settings.md#std-setting-TEMPLATES-OPTIONS) isn’t specified.

You can manually specify template caching with some custom template loaders
using settings like this:

```default
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "path.to.custom.Loader",
                    ],
                ),
            ],
        },
    }
]
```

#### NOTE
All of the built-in Django template tags are safe to use with the
cached loader, but if you’re using custom template tags that come from
third party packages, or that you wrote yourself, you should ensure
that the `Node` implementation for each tag is thread-safe. For more
information, see [template tag thread safety considerations](../../howto/custom-template-tags.md#template-tag-thread-safety).

`django.template.loaders.locmem.Loader`

#### *class* locmem.Loader

Loads templates from a Python dictionary. This is useful for testing.

This loader takes a dictionary of templates as its first argument:

```default
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.locmem.Loader",
                    {
                        "index.html": "content here",
                    },
                ),
            ],
        },
    }
]
```

This loader is disabled by default.

Django uses the template loaders in order according to the `'loaders'`
option. It uses each loader until a loader finds a match.

<a id="custom-template-loaders"></a>

## Custom loaders

It’s possible to load templates from additional sources using custom template
loaders. Custom `Loader` classes should inherit from
`django.template.loaders.base.Loader` and define the `get_contents()` and
`get_template_sources()` methods.

### Loader methods

### *class* Loader

Loads templates from a given source, such as the filesystem or a database.

#### get_template_sources(template_name)

A method that takes a `template_name` and yields
[`Origin`](#django.template.base.Origin) instances for each possible
source.

For example, the filesystem loader may receive `'index.html'` as a
`template_name` argument. This method would yield origins for the
full path of `index.html` as it appears in each template directory
the loader looks at.

The method doesn’t need to verify that the template exists at a given
path, but it should ensure the path is valid. For instance, the
filesystem loader makes sure the path lies under a valid template
directory.

#### get_contents(origin)

Returns the contents for a template given a
[`Origin`](#django.template.base.Origin) instance.

This is where a filesystem loader would read contents from the
filesystem, or a database loader would read from the database. If a
matching template doesn’t exist, this should raise a
[`TemplateDoesNotExist`](../../topics/templates.md#django.template.TemplateDoesNotExist) error.

#### get_template(template_name, skip=None)

Returns a `Template` object for a given `template_name` by looping
through results from [`get_template_sources()`](#django.template.loaders.base.Loader.get_template_sources) and calling
[`get_contents()`](#django.template.loaders.base.Loader.get_contents). This returns the first matching template. If no
template is found, [`TemplateDoesNotExist`](../../topics/templates.md#django.template.TemplateDoesNotExist) is
raised.

The optional `skip` argument is a list of origins to ignore when
extending templates. This allow templates to extend other templates of
the same name. It also used to avoid recursion errors.

In general, it is enough to define [`get_template_sources()`](#django.template.loaders.base.Loader.get_template_sources) and
[`get_contents()`](#django.template.loaders.base.Loader.get_contents) for custom template loaders. `get_template()`
will usually not need to be overridden.

## Template origin

Templates have an `origin` containing attributes depending on the source
they are loaded from.

### *class* Origin(name, template_name=None, loader=None)

#### name

The path to the template as returned by the template loader.
For loaders that read from the file system, this is the full
path to the template.

If the template is instantiated directly rather than through a
template loader, this is a string value of `<unknown_source>`.

#### template_name

The relative path to the template as passed into the
template loader.

If the template is instantiated directly rather than through a
template loader, this is `None`.

#### loader

The template loader instance that constructed this `Origin`.

If the template is instantiated directly rather than through a
template loader, this is `None`.

[`django.template.loaders.cached.Loader`](#django.template.loaders.cached.Loader) requires all of its
wrapped loaders to set this attribute, typically by instantiating
the `Origin` with `loader=self`.

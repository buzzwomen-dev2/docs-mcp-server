# The flatpages app

Django comes with an optional “flatpages” application. It lets you store “flat”
HTML content in a database and handles the management for you via Django’s
admin interface and a Python API.

A flatpage is an object with a URL, title and content. Use it for one-off,
special-case pages, such as “About” or “Privacy Policy” pages, that you want to
store in a database but for which you don’t want to develop a custom Django
application.

A flatpage can use a custom template or a default, systemwide flatpage
template. It can be associated with one, or multiple, sites.

The content field may optionally be left blank if you prefer to put your
content in a custom template.

## Installation

To install the flatpages app, follow these steps:

1. Install the [`sites framework`](sites.md#module-django.contrib.sites) by adding
   `'django.contrib.sites'` to your [`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS) setting,
   if it’s not already in there.

   Also make sure you’ve correctly set [`SITE_ID`](../settings.md#std-setting-SITE_ID) to the ID of the
   site the settings file represents. This will usually be `1` (i.e.
   `SITE_ID = 1`), but if you’re using the sites framework to manage
   multiple sites, it could be the ID of a different site.
2. Add `'django.contrib.flatpages'` to your [`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS)
   setting.

Then either:

1. Add an entry in your URLconf. For example:
   ```default
   urlpatterns = [
       path("pages/", include("django.contrib.flatpages.urls")),
   ]
   ```

or:

1. Add `'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'`
   to your [`MIDDLEWARE`](../settings.md#std-setting-MIDDLEWARE) setting.
2. Run the command [`manage.py migrate`](../django-admin.md#django-admin-migrate).

## How it works

`manage.py migrate` creates two tables in your database: `django_flatpage`
and `django_flatpage_sites`. `django_flatpage` is a lookup table that maps
a URL to a title and bunch of text content. `django_flatpage_sites`
associates a flatpage with a site.

### Using the URLconf

There are several ways to include the flatpages in your URLconf. You can
dedicate a particular path to flatpages:

```default
urlpatterns = [
    path("pages/", include("django.contrib.flatpages.urls")),
]
```

You can also set it up as a “catchall” pattern. In this case, it is important
to place the pattern at the end of the other urlpatterns:

```default
from django.contrib.flatpages import views

# Your other patterns here
urlpatterns += [
    re_path(r"^(?P<url>.*/)$", views.flatpage),
]
```

#### WARNING
If you set [`APPEND_SLASH`](../settings.md#std-setting-APPEND_SLASH) to `False`, you must remove the slash
in the catchall pattern or flatpages without a trailing slash will not be
matched.

Another common setup is to use flatpages for a limited set of known pages and
to hardcode their URLs in the [URLconf](../../topics/http/urls.md):

```default
from django.contrib.flatpages import views

urlpatterns += [
    path("about-us/", views.flatpage, kwargs={"url": "/about-us/"}, name="about"),
    path("license/", views.flatpage, kwargs={"url": "/license/"}, name="license"),
]
```

The `kwargs` argument sets the `url` value used for the `FlatPage` model
lookup in the flatpage view.

The `name` argument allows the URL to be reversed in templates, for example
using the [`url`](../templates/builtins.md#std-templatetag-url) template tag.

### Using the middleware

The [`FlatpageFallbackMiddleware`](#django.contrib.flatpages.middleware.FlatpageFallbackMiddleware)
can do all of the work.

### *class* FlatpageFallbackMiddleware

Each time any Django application raises a 404 error, this middleware
checks the flatpages database for the requested URL as a last resort.
Specifically, it checks for a flatpage with the given URL with a site ID
that corresponds to the [`SITE_ID`](../settings.md#std-setting-SITE_ID) setting.

If it finds a match, it follows this algorithm:

* If the flatpage has a custom template, it loads that template.
  Otherwise, it loads the template `flatpages/default.html`.
* It passes that template a single context variable, `flatpage`,
  which is the flatpage object. It uses
  [`RequestContext`](../templates/api.md#django.template.RequestContext) in rendering the
  template.

The middleware will only add a trailing slash and redirect (by looking
at the [`APPEND_SLASH`](../settings.md#std-setting-APPEND_SLASH) setting) if the resulting URL refers to
a valid flatpage. Redirects are permanent (301 status code).

If it doesn’t find a match, the request continues to be processed as usual.

The middleware only gets activated for 404s – not for 500s or responses
of any other status code.

Note that the order of [`MIDDLEWARE`](../settings.md#std-setting-MIDDLEWARE) matters. Generally, you can put
[`FlatpageFallbackMiddleware`](#django.contrib.flatpages.middleware.FlatpageFallbackMiddleware) at the
end of the list. This means it will run first when processing the response, and
ensures that any other response-processing middleware see the real flatpage
response rather than the 404.

For more on middleware, read the [middleware docs](../../topics/http/middleware.md).

## How to add, change and delete flatpages

#### WARNING
Permissions to add or edit flatpages should be restricted to trusted users.
Flatpages are defined by raw HTML and are **not sanitized** by Django. As a
consequence, a malicious flatpage can lead to various security
vulnerabilities, including permission escalation.

<a id="flatpages-admin"></a>

### Via the admin interface

If you’ve activated the automatic Django admin interface, you should see a
“Flatpages” section on the admin index page. Edit flatpages as you edit any
other object in the system.

The `FlatPage` model has an `enable_comments` field that isn’t used by
`contrib.flatpages`, but that could be useful for your project or third-party
apps. It doesn’t appear in the admin interface, but you can add it by
registering a custom `ModelAdmin` for `FlatPage`:

```default
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _


# Define a new FlatPageAdmin
class FlatPageAdmin(FlatPageAdmin):
    fieldsets = [
        (None, {"fields": ["url", "title", "content", "sites"]}),
        (
            _("Advanced options"),
            {
                "classes": ["collapse"],
                "fields": [
                    "enable_comments",
                    "registration_required",
                    "template_name",
                ],
            },
        ),
    ]


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
```

### Via the Python API

Flatpages are represented by a standard
[Django model](../../topics/db/models.md), [`FlatPage`](#django.contrib.flatpages.models.FlatPage). You can access
flatpage objects via the [Django database API](../../topics/db/queries.md).

## `FlatPage` model

#### *class* models.FlatPage

### Fields

[`FlatPage`](#django.contrib.flatpages.models.FlatPage) objects have the following
fields:

#### *class* models.FlatPage

#### url

Required. 100 characters or fewer. Indexed for faster lookups.

#### title

Required. 200 characters or fewer.

#### content

Optional ([`blank=True`](../models/fields.md#django.db.models.Field.blank)).
[`TextField`](../models/fields.md#django.db.models.TextField) that typically, contains the HTML
content of the page.

#### enable_comments

Boolean. This field is not used by [`flatpages`](#module-django.contrib.flatpages) by
default and does not appear in the admin interface. Please see
[flatpages admin interface section](#flatpages-admin) for a
detailed explanation.

#### template_name

Optional ([`blank=True`](../models/fields.md#django.db.models.Field.blank)). 70
characters or fewer. Specifies the template used to render the page.
Defaults to `flatpages/default.html` if not provided.

<!-- attribute: registration_required

Boolean. When ``True``, restricts the page access to logged-in users
only. -->

#### sites

Many-to-many relationship to
[`Site`](sites.md#django.contrib.sites.models.Site), which determines the
[sites](sites.md) the flatpage is available on.

### Methods

#### *class* models.FlatPage

#### get_absolute_url()

Returns the relative URL path of the page based on the
[`url`](#django.contrib.flatpages.models.FlatPage.url) attribute.

## Flatpage templates

By default, flatpages are rendered via the template
`flatpages/default.html`, but you can override that for a particular
flatpage: in the admin, a collapsed fieldset titled “Advanced options”
(clicking will expand it) contains a field for specifying a template name. If
you’re creating a flatpage via the Python API you can set the template name as
the field `template_name` on the `FlatPage` object.

Creating the `flatpages/default.html` template is your responsibility;
in your template directory, create a `flatpages` directory containing a
file `default.html`.

Flatpage templates are passed a single context variable, `flatpage`,
which is the flatpage object.

Here’s a sample `flatpages/default.html` template:

```html+django
<!DOCTYPE html>
<html lang="en">
<head>
<title>{{ flatpage.title }}</title>
</head>
<body>
{{ flatpage.content }}
</body>
</html>
```

Since you’re already entering raw HTML into the admin page for a flatpage,
both `flatpage.title` and `flatpage.content` are marked as **not**
requiring [automatic HTML escaping](../templates/language.md#automatic-html-escaping) in the
template.

## Getting a list of [`FlatPage`](#django.contrib.flatpages.models.FlatPage) objects in your templates

The flatpages app provides a template tag that allows you to iterate
over all of the available flatpages on the [current site](sites.md#hooking-into-current-site-from-views).

Like all custom template tags, you’ll need to [load its custom
tag library](../templates/language.md#loading-custom-template-libraries) before you can use
it. After loading the library, you can retrieve all current flatpages
via the [`get_flatpages`](#std-templatetag-get_flatpages) tag:

```html+django
{% load flatpages %}
{% get_flatpages as flatpages %}
<ul>
    {% for page in flatpages %}
        <li><a href="{{ page.url }}">{{ page.title }}</a></li>
    {% endfor %}
</ul>
```

<a id="std-templatetag-get_flatpages"></a>

### Displaying `registration_required` flatpages

By default, the [`get_flatpages`](#std-templatetag-get_flatpages) template tag will only show
flatpages that are marked `registration_required = False`. If you
want to display registration-protected flatpages, you need to specify
an authenticated user using a `for` clause.

For example:

```html+django
{% get_flatpages for someuser as about_pages %}
```

If you provide an anonymous user, [`get_flatpages`](#std-templatetag-get_flatpages) will behave
the same as if you hadn’t provided a user – i.e., it will only show you
public flatpages.

### Limiting flatpages by base URL

An optional argument, `starts_with`, can be applied to limit the
returned pages to those beginning with a particular base URL. This
argument may be passed as a string, or as a variable to be resolved
from the context.

For example:

```html+django
{% get_flatpages '/about/' as about_pages %}
{% get_flatpages about_prefix as about_pages %}
{% get_flatpages '/about/' for someuser as about_pages %}
```

## Integrating with [`django.contrib.sitemaps`](sitemaps.md#module-django.contrib.sitemaps)

### *class* FlatPageSitemap

The [`sitemaps.FlatPageSitemap`](#django.contrib.flatpages.sitemaps.FlatPageSitemap) class looks at all
publicly visible [`flatpages`](#module-django.contrib.flatpages) defined for the current
[`SITE_ID`](../settings.md#std-setting-SITE_ID) (see the [`sites documentation`](sites.md#module-django.contrib.sites)) and creates an entry in the sitemap. These entries
include only the [`location`](sitemaps.md#django.contrib.sitemaps.Sitemap.location)
attribute – not [`lastmod`](sitemaps.md#django.contrib.sitemaps.Sitemap.lastmod),
[`changefreq`](sitemaps.md#django.contrib.sitemaps.Sitemap.changefreq) or
[`priority`](sitemaps.md#django.contrib.sitemaps.Sitemap.priority).

### Example

Here’s an example of a URLconf using [`FlatPageSitemap`](#django.contrib.flatpages.sitemaps.FlatPageSitemap):

```default
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path

urlpatterns = [
    # ...
    # the sitemap
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"flatpages": FlatPageSitemap}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
```

# Django documentation

### Everything you need to know about Django.

<a id="index-first-steps"></a>

## First steps

Are you new to Django or to programming? This is the place to start!

* **From scratch:**
  [Overview](intro/overview.md) |
  [Installation](intro/install.md)
* **Tutorial:**
  [Part 1: Requests and responses](intro/tutorial01.md) |
  [Part 2: Models and the admin site](intro/tutorial02.md) |
  [Part 3: Views and templates](intro/tutorial03.md) |
  [Part 4: Forms and generic views](intro/tutorial04.md) |
  [Part 5: Testing](intro/tutorial05.md) |
  [Part 6: Static files](intro/tutorial06.md) |
  [Part 7: Customizing the admin site](intro/tutorial07.md) |
  [Part 8: Adding third-party packages](intro/tutorial08.md)
* **Advanced Tutorials:**
  [How to write reusable apps](intro/reusable-apps.md) |
  [Writing your first contribution to Django](intro/contributing.md)

## Getting help

Having trouble? We’d like to help!

* Try the [FAQ](faq/index.md) – it’s got answers to many common questions.
* Looking for specific information? Try the [Index](genindex.md), [Module Index](py-modindex.md) or
  the [detailed table of contents](contents.md).
* Not found anything? See [FAQ: Getting Help](faq/help.md) for information on getting support
  and asking questions to the community.
* Report bugs with Django in our [ticket tracker](https://code.djangoproject.com/).

## How the documentation is organized

Django has a lot of documentation. A high-level overview of how it’s organized
will help you know where to look for certain things:

* [Tutorials](intro/index.md) take you by the hand through a series of
  steps to create a web application. Start here if you’re new to Django or web
  application development. Also look at the “[First steps](#index-first-steps)”.
* [Topic guides](topics/index.md) discuss key topics and concepts at a
  fairly high level and provide useful background information and explanation.
* [Reference guides](ref/index.md) contain technical reference for APIs and
  other aspects of Django’s machinery. They describe how it works and how to
  use it but assume that you have a basic understanding of key concepts.
* [How-to guides](howto/index.md) are recipes. They guide you through the
  steps involved in addressing key problems and use-cases. They are more
  advanced than tutorials and assume some knowledge of how Django works.

## The model layer

Django provides an abstraction layer (the “models”) for structuring and
manipulating the data of your web application. Learn more about it below:

* **Models:**
  [Introduction to models](topics/db/models.md) |
  [Field types](ref/models/fields.md) |
  [Indexes](ref/models/indexes.md) |
  [Meta options](ref/models/options.md) |
  [Model class](ref/models/class.md)
* **QuerySets:**
  [Making queries](topics/db/queries.md) |
  [QuerySet method reference](ref/models/querysets.md) |
  [Lookup expressions](ref/models/lookups.md)
* **Model instances:**
  [Instance methods](ref/models/instances.md) |
  [Accessing related objects](ref/models/relations.md)
* **Migrations:**
  [Introduction to Migrations](topics/migrations.md) |
  [Operations reference](ref/migration-operations.md) |
  [SchemaEditor](ref/schema-editor.md) |
  [Writing migrations](howto/writing-migrations.md)
* **Advanced:**
  [Managers](topics/db/managers.md) |
  [Raw SQL](topics/db/sql.md) |
  [Transactions](topics/db/transactions.md) |
  [Aggregation](topics/db/aggregation.md) |
  [Search](topics/db/search.md) |
  [Custom fields](howto/custom-model-fields.md) |
  [Multiple databases](topics/db/multi-db.md) |
  [Custom lookups](howto/custom-lookups.md) |
  [Query Expressions](ref/models/expressions.md) |
  [Conditional Expressions](ref/models/conditional-expressions.md) |
  [Database Functions](ref/models/database-functions.md)
* **Other:**
  [Supported databases](ref/databases.md) |
  [Legacy databases](howto/legacy-databases.md) |
  [Providing initial data](howto/initial-data.md) |
  [Optimize database access](topics/db/optimization.md) |
  [PostgreSQL specific features](ref/contrib/postgres/index.md)

## The view layer

Django has the concept of “views” to encapsulate the logic responsible for
processing a user’s request and for returning the response. Find all you need
to know about views via the links below:

* **The basics:**
  [URLconfs](topics/http/urls.md) |
  [View functions](topics/http/views.md) |
  [Shortcuts](topics/http/shortcuts.md) |
  [Decorators](topics/http/decorators.md) |
  [Asynchronous Support](topics/async.md)
* **Reference:**
  [Built-in Views](ref/views.md) |
  [Request/response objects](ref/request-response.md) |
  [TemplateResponse objects](ref/template-response.md)
* **File uploads:**
  [Overview](topics/http/file-uploads.md) |
  [File objects](ref/files/file.md) |
  [Storage API](ref/files/storage.md) |
  [Managing files](topics/files.md) |
  [Custom storage](howto/custom-file-storage.md)
* **Class-based views:**
  [Overview](topics/class-based-views/index.md) |
  [Built-in display views](topics/class-based-views/generic-display.md) |
  [Built-in editing views](topics/class-based-views/generic-editing.md) |
  [Using mixins](topics/class-based-views/mixins.md) |
  [API reference](ref/class-based-views/index.md) |
  [Flattened index](ref/class-based-views/flattened-index.md)
* **Advanced:**
  [Generating CSV](howto/outputting-csv.md) |
  [Generating PDF](howto/outputting-pdf.md)
* **Middleware:**
  [Overview](topics/http/middleware.md) |
  [Built-in middleware classes](ref/middleware.md)

## The template layer

The template layer provides a designer-friendly syntax for rendering the
information to be presented to the user. Learn how this syntax can be used by
designers and how it can be extended by programmers:

* **The basics:**
  [Overview](topics/templates.md)
* **For designers:**
  [Language overview](ref/templates/language.md) |
  [Built-in tags and filters](ref/templates/builtins.md) |
  [Humanization](ref/contrib/humanize.md)
* **For programmers:**
  [Template API](ref/templates/api.md) |
  [Custom tags and filters](howto/custom-template-tags.md) |
  [Custom template backend](howto/custom-template-backend.md)

## Forms

Django provides a rich framework to facilitate the creation of forms and the
manipulation of form data.

* **The basics:**
  [Overview](topics/forms/index.md) |
  [Form API](ref/forms/api.md) |
  [Built-in fields](ref/forms/fields.md) |
  [Built-in widgets](ref/forms/widgets.md)
* **Advanced:**
  [Forms for models](topics/forms/modelforms.md) |
  [Integrating media](topics/forms/media.md) |
  [Formsets](topics/forms/formsets.md) |
  [Customizing validation](ref/forms/validation.md)

## The development process

Learn about the various components and tools to help you in the development and
testing of Django applications:

* **Settings:**
  [Overview](topics/settings.md) |
  [Full list of settings](ref/settings.md)
* **Applications:**
  [Overview](ref/applications.md)
* **Exceptions:**
  [Overview](ref/exceptions.md)
* **django-admin and manage.py:**
  [Overview](ref/django-admin.md) |
  [Adding custom commands](howto/custom-management-commands.md)
* **Testing:**
  [Introduction](topics/testing/index.md) |
  [Writing and running tests](topics/testing/overview.md) |
  [Included testing tools](topics/testing/tools.md) |
  [Advanced topics](topics/testing/advanced.md)
* **Deployment:**
  [Overview](howto/deployment/index.md) |
  [WSGI servers](howto/deployment/wsgi/index.md) |
  [ASGI servers](howto/deployment/asgi/index.md) |
  [Deploying static files](howto/static-files/deployment.md) |
  [Tracking code errors by email](howto/error-reporting.md) |
  [Deployment checklist](howto/deployment/checklist.md)

## The admin

Find all you need to know about the automated admin interface, one of Django’s
most popular features:

* [Admin site](ref/contrib/admin/index.md)
* [Admin actions](ref/contrib/admin/actions.md)
* [Admin documentation generator](ref/contrib/admin/admindocs.md)

## Security

Security is a topic of paramount importance in the development of web
applications and Django provides multiple protection tools and mechanisms:

* [Security overview](topics/security.md)
* [Disclosed security issues in Django](releases/security.md)
* [Clickjacking protection](ref/clickjacking.md)
* [Cross Site Request Forgery protection](ref/csrf.md)
* [Cryptographic signing](topics/signing.md)
* [Security Middleware](ref/middleware.md#security-middleware)
* [Content Security Policy](ref/csp.md)

## Internationalization and localization

Django offers a robust internationalization and localization framework to
assist you in the development of applications for multiple languages and world
regions:

* [Overview](topics/i18n/index.md) |
  [Internationalization](topics/i18n/translation.md) |
  [Localization](topics/i18n/translation.md#how-to-create-language-files) |
  [Localized web UI formatting and form input](topics/i18n/formatting.md)
* [Time zones](topics/i18n/timezones.md)

## Performance and optimization

There are a variety of techniques and tools that can help get your code running
more efficiently - faster, and using fewer system resources.

* [Performance and optimization overview](topics/performance.md)

## Geographic framework

[GeoDjango](ref/contrib/gis/index.md) intends to be a world-class
geographic web framework. Its goal is to make it as easy as possible to build
GIS web applications and harness the power of spatially enabled data.

## Common web application tools

Django offers multiple tools commonly needed in the development of web
applications:

* **Authentication:**
  [Overview](topics/auth/index.md) |
  [Using the authentication system](topics/auth/default.md) |
  [Password management](topics/auth/passwords.md) |
  [Customizing authentication](topics/auth/customizing.md) |
  [API Reference](ref/contrib/auth.md)
* [Caching](topics/cache.md)
* [Logging](topics/logging.md)
* [Tasks framework](topics/tasks.md)
* [Sending emails](topics/email.md)
* [Syndication feeds (RSS/Atom)](ref/contrib/syndication.md)
* [Pagination](topics/pagination.md)
* [Messages framework](ref/contrib/messages.md)
* [Serialization](topics/serialization.md)
* [Sessions](topics/http/sessions.md)
* [Sitemaps](ref/contrib/sitemaps.md)
* [Static files management](ref/contrib/staticfiles.md)
* [Data validation](ref/validators.md)

## Other core functionalities

Learn about some other core functionalities of the Django framework:

* [Conditional content processing](topics/conditional-view-processing.md)
* [Content types and generic relations](ref/contrib/contenttypes.md)
* [Flatpages](ref/contrib/flatpages.md)
* [Redirects](ref/contrib/redirects.md)
* [Signals](topics/signals.md)
* [System check framework](topics/checks.md)
* [The sites framework](ref/contrib/sites.md)
* [Unicode in Django](ref/unicode.md)

## The Django open-source project

Learn about the development process for the Django project itself and about how
you can contribute:

* **Community:**
  [Contributing to Django](internals/contributing/index.md) |
  [The release process](internals/release-process.md) |
  [Team organization](internals/organization.md) |
  [The Django source code repository](internals/git.md) |
  [Security policies](internals/security.md) |
  [Mailing lists and Forum](internals/mailing-lists.md)
* **Design philosophies:**
  [Overview](misc/design-philosophies.md)
* **Documentation:**
  [About this documentation](internals/contributing/writing-documentation.md)
* **Third-party distributions:**
  [Overview](misc/distributions.md)
* **Django over time:**
  [API stability](misc/api-stability.md) |
  [Release notes and upgrading instructions](releases/index.md) |
  [Deprecation Timeline](internals/deprecation.md)

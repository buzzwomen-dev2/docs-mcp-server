# Glossary

<a id="term-concrete-model"></a>

concrete model
: A non-abstract ([`abstract=False`](ref/models/options.md#django.db.models.Options.abstract)) model.

<a id="term-field"></a>

field
: An attribute on a [model](#term-model); a given field usually maps directly to
  a single database column.
  <br/>
  See [Models](topics/db/models.md).

<a id="term-generic-view"></a>

generic view
: A higher-order [view](#term-view) function that provides an abstract/generic
  implementation of a common idiom or pattern found in view development.
  <br/>
  See [Class-based views](topics/class-based-views/index.md).

<a id="term-model"></a>

model
: Models store your application’s data.
  <br/>
  See [Models](topics/db/models.md).

<a id="term-MTV"></a>

MTV
: “Model-template-view”; a software pattern, similar in style to MVC, but
  a better description of the way Django does things.
  <br/>
  See [the FAQ entry](faq/general.md#faq-mtv).

<a id="term-MVC"></a>

MVC
: [Model-view-controller](https://en.wikipedia.org/wiki/Model-view-controller); a software pattern. Django [follows MVC
  to some extent](faq/general.md#faq-mtv).

<a id="term-project"></a>

project
: A Python package – i.e. a directory of code – that contains all the
  settings for an instance of Django. This would include database
  configuration, Django-specific options and application-specific
  settings.

<a id="term-property"></a>

property
: Also known as “managed attributes”, and a feature of Python since
  version 2.2. This is a neat way to implement attributes whose usage
  resembles attribute access, but whose implementation uses method calls.
  <br/>
  See [`property`](https://docs.python.org/3/library/functions.html#property).

<a id="term-queryset"></a>

queryset
: An object representing some set of rows to be fetched from the
  database.
  <br/>
  See [Making queries](topics/db/queries.md).

<a id="term-slug"></a>

slug
: A short label for something, containing only letters, numbers,
  underscores or hyphens. They’re generally used in URLs. For
  example, in a typical blog entry URL:
  <br/>
  ```default
  [https://www.djangoproject.com/weblog/2008/apr/12/](https://www.djangoproject.com/weblog/2008/apr/12/)**spring**/
  ```
  <br/>
  the last bit (`spring`) is the slug.

<a id="term-template"></a>

template
: A chunk of text that acts as formatting for representing data. A
  template helps to abstract the presentation of data from the data
  itself.
  <br/>
  See [Templates](topics/templates.md).

<a id="term-view"></a>

view
: A function responsible for rendering a page.

# Templates

Django’s template engine provides a powerful mini-language for defining the
user-facing layer of your application, encouraging a clean separation of
application and presentation logic. Templates can be maintained by anyone with
an understanding of HTML; no knowledge of Python is required. For introductory
material, see [Templates](../../topics/templates.md) topic guide.

* [The Django template language](language.md)
  * [Templates](language.md#templates)
  * [Variables](language.md#variables)
  * [Filters](language.md#filters)
  * [Tags](language.md#tags)
  * [Comments](language.md#comments)
  * [Template inheritance](language.md#template-inheritance)
  * [Template partials](language.md#template-partials)
  * [Automatic HTML escaping](language.md#automatic-html-escaping)
  * [Accessing method calls](language.md#accessing-method-calls)
  * [Custom tag and filter libraries](language.md#custom-tag-and-filter-libraries)
* [Built-in template tags and filters](builtins.md)
  * [Built-in tag reference](builtins.md#built-in-tag-reference)
  * [Built-in filter reference](builtins.md#built-in-filter-reference)
  * [Internationalization tags and filters](builtins.md#internationalization-tags-and-filters)
  * [Other tags and filters libraries](builtins.md#other-tags-and-filters-libraries)
* [The Django template language: for Python programmers](api.md)
  * [Overview](api.md#overview)
  * [Configuring an engine](api.md#configuring-an-engine)
  * [Loading a template](api.md#loading-a-template)
  * [Rendering a context](api.md#rendering-a-context)
  * [Playing with `Context` objects](api.md#playing-with-context-objects)
  * [Loading templates](api.md#loading-templates)
  * [Custom loaders](api.md#custom-loaders)
  * [Template origin](api.md#template-origin)

#### SEE ALSO
For information on writing your own custom tags and filters, see
[How to create custom template tags and filters](../../howto/custom-template-tags.md).

To learn how to override templates in other Django applications, see
[How to override templates](../../howto/overriding-templates.md).

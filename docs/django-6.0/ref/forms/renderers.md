# The form rendering API

Django’s form widgets are rendered using Django’s [template engines
system](../../topics/templates.md).

The form rendering process can be customized at several levels:

* Widgets can specify custom template names.
* Forms and widgets can specify custom renderer classes.
* A widget’s template can be overridden by a project. (Reusable applications
  typically shouldn’t override built-in templates because they might conflict
  with a project’s custom templates.)

<a id="low-level-widget-render-api"></a>

## The low-level render API

The rendering of form templates is controlled by a customizable renderer class.
A custom renderer can be specified by updating the [`FORM_RENDERER`](../settings.md#std-setting-FORM_RENDERER)
setting. It defaults to
`'`[`django.forms.renderers.DjangoTemplates`](#django.forms.renderers.DjangoTemplates)`'`.

By specifying a custom form renderer and overriding
[`form_template_name`](#django.forms.renderers.BaseRenderer.form_template_name) you can adjust the default form
markup across your project from a single place.

You can also provide a custom renderer per-form or per-widget by setting the
[`Form.default_renderer`](api.md#django.forms.Form.default_renderer) attribute or by using the `renderer` argument
of [`Form.render()`](api.md#django.forms.Form.render), or [`Widget.render()`](widgets.md#django.forms.Widget.render).

Matching points apply to formset rendering. See [Using a formset in views and templates](../../topics/forms/formsets.md#formset-rendering) for
discussion.

Use one of the [built-in template form renderers](#built-in-template-form-renderers) or implement your own. Custom renderers
must implement a `render(template_name, context, request=None)` method. It
should return a rendered template (as a string) or raise
[`TemplateDoesNotExist`](../../topics/templates.md#django.template.TemplateDoesNotExist).

### *class* BaseRenderer

The base class for the built-in form renderers.

#### form_template_name

The default name of the template to use to render a form.

Defaults to `"django/forms/div.html"` template.

#### formset_template_name

The default name of the template to use to render a formset.

Defaults to `"django/forms/formsets/div.html"` template.

#### field_template_name

The default name of the template used to render a `BoundField`.

Defaults to `"django/forms/field.html"`

#### bound_field_class

The default class used to represent form fields across the project.

Defaults to [`BoundField`](api.md#django.forms.BoundField) class.

This can be customized further using [`Form.bound_field_class`](api.md#django.forms.Form.bound_field_class)
for per-form overrides, or [`Field.bound_field_class`](fields.md#django.forms.Field.bound_field_class) for
per-field overrides.

#### get_template(template_name)

Subclasses must implement this method with the appropriate template
finding logic.

#### render(template_name, context, request=None)

Renders the given template, or raises
[`TemplateDoesNotExist`](../../topics/templates.md#django.template.TemplateDoesNotExist).

<a id="built-in-template-form-renderers"></a>

## Built-in-template form renderers

### `DjangoTemplates`

### *class* DjangoTemplates

This renderer uses a standalone
[`DjangoTemplates`](../../topics/templates.md#django.template.backends.django.DjangoTemplates)
engine (unconnected to what you might have configured in the
[`TEMPLATES`](../settings.md#std-setting-TEMPLATES) setting). It loads templates first from the built-in form
templates directory in [django/forms/templates](https://github.com/django/django/blob/main/django/forms/templates) and then from the
installed apps’ templates directories using the [`app_directories`](../templates/api.md#django.template.loaders.app_directories.Loader) loader.

If you want to render templates with customizations from your
[`TEMPLATES`](../settings.md#std-setting-TEMPLATES) setting, such as context processors for example, use the
[`TemplatesSetting`](#django.forms.renderers.TemplatesSetting) renderer.

### `Jinja2`

### *class* Jinja2

This renderer is the same as the [`DjangoTemplates`](#django.forms.renderers.DjangoTemplates) renderer except that
it uses a [`Jinja2`](../../topics/templates.md#django.template.backends.jinja2.Jinja2) backend. Templates
for the built-in widgets are located in [django/forms/jinja2](https://github.com/django/django/blob/main/django/forms/jinja2) and
installed apps can provide templates in a `jinja2` directory.

To use this backend, all the forms and widgets in your project and its
third-party apps must have Jinja2 templates. Unless you provide your own Jinja2
templates for widgets that don’t have any, you can’t use this renderer. For
example, [`django.contrib.admin`](../contrib/admin/index.md#module-django.contrib.admin) doesn’t include Jinja2 templates for its
widgets due to their usage of Django template tags.

### `TemplatesSetting`

### *class* TemplatesSetting

This renderer gives you complete control of how form and widget templates are
sourced. It uses [`get_template()`](../../topics/templates.md#django.template.loader.get_template) to find templates
based on what’s configured in the [`TEMPLATES`](../settings.md#std-setting-TEMPLATES) setting.

Using this renderer along with the built-in templates requires either:

* `'django.forms'` in [`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS) and at least one engine
  with [`APP_DIRS=True`](../settings.md#std-setting-TEMPLATES-APP_DIRS).
* Adding the built-in templates directory in [`DIRS`](../settings.md#std-setting-TEMPLATES-DIRS)
  of one of your template engines. To generate that path:
  ```default
  import django

  django.__path__[0] + "/forms/templates"  # or '/forms/jinja2'
  ```

Using this renderer requires you to make sure the form templates your project
needs can be located.

## Context available in formset templates

Formset templates receive a context from [`BaseFormSet.get_context()`](../../topics/forms/formsets.md#django.forms.formsets.BaseFormSet.get_context). By
default, formsets receive a dictionary with the following values:

* `formset`: The formset instance.

## Context available in form templates

Form templates receive a context from [`Form.get_context()`](api.md#django.forms.Form.get_context). By default,
forms receive a dictionary with the following values:

* `form`: The bound form.
* `fields`: All bound fields, except the hidden fields.
* `hidden_fields`: All hidden bound fields.
* `errors`: All non field related or hidden field related form errors.

## Context available in field templates

Field templates receive a context from [`BoundField.get_context()`](api.md#django.forms.BoundField.get_context). By
default, fields receive a dictionary with the following values:

* `field`: The [`BoundField`](api.md#django.forms.BoundField).

## Context available in widget templates

Widget templates receive a context from [`Widget.get_context()`](widgets.md#django.forms.Widget.get_context). By
default, widgets receive a single value in the context, `widget`. This is a
dictionary that contains values like:

* `name`
* `value`
* `attrs`
* `is_hidden`
* `template_name`

Some widgets add further information to the context. For instance, all widgets
that subclass `Input` defines `widget['type']` and [`MultiWidget`](widgets.md#django.forms.MultiWidget)
defines `widget['subwidgets']` for looping purposes.

<a id="overriding-built-in-formset-templates"></a>

## Overriding built-in formset templates

[`BaseFormSet.template_name`](../../topics/forms/formsets.md#django.forms.formsets.BaseFormSet.template_name)

To override formset templates, you must use the [`TemplatesSetting`](#django.forms.renderers.TemplatesSetting)
renderer. Then overriding formset templates works [the same as](../../howto/overriding-templates.md) overriding any other template in your project.

<a id="overriding-built-in-form-templates"></a>

## Overriding built-in form templates

[`Form.template_name`](api.md#django.forms.Form.template_name)

To override form templates, you must use the [`TemplatesSetting`](#django.forms.renderers.TemplatesSetting)
renderer. Then overriding form templates works [the same as](../../howto/overriding-templates.md) overriding any other template in your project.

<a id="overriding-built-in-field-templates"></a>

## Overriding built-in field templates

[`Field.template_name`](fields.md#django.forms.Field.template_name)

To override field templates, you must use the [`TemplatesSetting`](#django.forms.renderers.TemplatesSetting)
renderer. Then overriding field templates works [the same as](../../howto/overriding-templates.md) overriding any other template in your project.

<a id="overriding-built-in-widget-templates"></a>

## Overriding built-in widget templates

Each widget has a `template_name` attribute with a value such as
`input.html`. Built-in widget templates are stored in the
`django/forms/widgets` path. You can provide a custom template for
`input.html` by defining `django/forms/widgets/input.html`, for example.
See [Built-in widgets](widgets.md#built-in-widgets) for the name of each widget’s template.

To override widget templates, you must use the [`TemplatesSetting`](#django.forms.renderers.TemplatesSetting)
renderer. Then overriding widget templates works [the same as](../../howto/overriding-templates.md) overriding any other template in your project.

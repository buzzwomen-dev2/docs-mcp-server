# Model forms

`ModelForm` API reference. For introductory material about using a
`ModelForm`, see the [Creating forms from models](../../topics/forms/modelforms.md) topic guide.

## Model form `Meta` API

### *class* ModelFormOptions

The `_meta` API is used to build forms that reflect a Django model. It is
accessible through the `_meta` attribute of each model form, and is an
`django.forms.models.ModelFormOptions` instance.

The structure of the generated form can be customized by defining metadata
options as attributes of an inner `Meta` class. For example:

```default
from django.forms import ModelForm
from myapp.models import Book


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author"]
        help_texts = {
            "title": "The title of the book",
            "author": "The author of the book",
        }
        # ... other attributes
```

Required attributes are [`model`](#django.forms.ModelFormOptions.model), and either
[`fields`](#django.forms.ModelFormOptions.fields) or [`exclude`](#django.forms.ModelFormOptions.exclude). All
other `Meta` attributes are optional.

Optional attributes, other than [`localized_fields`](#django.forms.ModelFormOptions.localized_fields) and
[`formfield_callback`](#django.forms.ModelFormOptions.formfield_callback), expect a dictionary that maps a
model field name to a value. Any field that is not defined in the dictionary
falls back to the field’s default value.

### `error_messages`

#### ModelFormOptions.error_messages

A dictionary that maps a model field name to a dictionary of error message
keys (`null`, `blank`, `invalid`, `unique`, etc.) mapped to custom
error messages.

When a field is not specified, Django will fall back on the error messages
defined in that model field’s [`django.db.models.Field.error_messages`](../models/fields.md#django.db.models.Field.error_messages)
and then finally on the default error messages for that field type.

### `exclude`

#### ModelFormOptions.exclude

A tuple or list of [`model`](#django.forms.ModelFormOptions.model) field names to be
excluded from the form.

Either [`fields`](#django.forms.ModelFormOptions.fields) or
[`exclude`](#django.forms.ModelFormOptions.exclude) must be set. If neither are set, an
[`ImproperlyConfigured`](../exceptions.md#django.core.exceptions.ImproperlyConfigured) exception will be
raised. If [`exclude`](#django.forms.ModelFormOptions.exclude) is set and
[`fields`](#django.forms.ModelFormOptions.fields) is unset, all model fields, except for
those specified in [`exclude`](#django.forms.ModelFormOptions.exclude), are included in the
form.

### `field_classes`

#### ModelFormOptions.field_classes

A dictionary that maps a model field name to a [`Field`](fields.md#django.forms.Field)
class, which overrides the `form_class` used in the model field’s
[`Field.formfield()`](../models/fields.md#django.db.models.Field.formfield) method.

When a field is not specified, Django will fall back on the model field’s
[default field class](../../topics/forms/modelforms.md#model-form-field-types).

### `fields`

#### ModelFormOptions.fields

A tuple or list of [`model`](#django.forms.ModelFormOptions.model) field names to be
included in the form. The value `'__all__'` can be used to specify that
all fields should be included.

If any field is specified in [`exclude`](#django.forms.ModelFormOptions.exclude), this will
not be included in the form despite being specified in
[`fields`](#django.forms.ModelFormOptions.fields).

Either [`fields`](#django.forms.ModelFormOptions.fields) or
[`exclude`](#django.forms.ModelFormOptions.exclude) must be set. If neither are set, an
[`ImproperlyConfigured`](../exceptions.md#django.core.exceptions.ImproperlyConfigured) exception will be
raised.

### `formfield_callback`

#### ModelFormOptions.formfield_callback

A function or callable that takes a model field and returns a
[`django.forms.Field`](fields.md#django.forms.Field) object.

### `help_texts`

#### ModelFormOptions.help_texts

A dictionary that maps a model field name to a help text string.

When a field is not specified, Django will fall back on that model field’s
[`help_text`](../models/fields.md#django.db.models.Field.help_text).

### `labels`

#### ModelFormOptions.labels

A dictionary that maps a model field names to a label string.

When a field is not specified, Django will fall back on that model field’s
[`verbose_name`](../models/fields.md#django.db.models.Field.verbose_name) and then the field’s attribute
name.

### `localized_fields`

#### ModelFormOptions.localized_fields

A tuple or list of [`model`](#django.forms.ModelFormOptions.model) field names to be
localized. The value `'__all__'` can be used to specify that all fields
should be localized.

By default, form fields are not localized, see
[enabling localization of fields](../../topics/forms/modelforms.md#modelforms-enabling-localization-of-fields) for more details.

### `model`

#### ModelFormOptions.model

Required. The [`django.db.models.Model`](../models/instances.md#django.db.models.Model) to be used for the
[`ModelForm`](../../topics/forms/modelforms.md#django.forms.ModelForm).

### `widgets`

#### ModelFormOptions.widgets

A dictionary that maps a model field name to a
[`django.forms.Widget`](widgets.md#django.forms.Widget).

When a field is not specified, Django will fall back on the default widget
for that particular type of [`django.db.models.Field`](../models/fields.md#django.db.models.Field).

## Model form factory functions

### `modelform_factory`

### modelform_factory(model, form=ModelForm, fields=None, exclude=None, formfield_callback=None, widgets=None, localized_fields=None, labels=None, help_texts=None, error_messages=None, field_classes=None)

Returns a [`ModelForm`](../../topics/forms/modelforms.md#django.forms.ModelForm) class for the given `model`.
You can optionally pass a `form` argument to use as a starting point for
constructing the `ModelForm`.

`fields` is an optional list of field names. If provided, only the named
fields will be included in the returned fields.

`exclude` is an optional list of field names. If provided, the named
fields will be excluded from the returned fields, even if they are listed
in the `fields` argument.

`formfield_callback` is a callable that takes a model field and returns
a form field.

`widgets` is a dictionary of model field names mapped to a widget.

`localized_fields` is a list of names of fields which should be
localized.

`labels` is a dictionary of model field names mapped to a label.

`help_texts` is a dictionary of model field names mapped to a help text.

`error_messages` is a dictionary of model field names mapped to a
dictionary of error messages.

`field_classes` is a dictionary of model field names mapped to a form
field class.

See [ModelForm factory function](../../topics/forms/modelforms.md#modelforms-factory) for example usage.

You must provide the list of fields explicitly, either via keyword
arguments `fields` or `exclude`, or the corresponding attributes on the
form’s inner `Meta` class. See [Selecting the fields to use](../../topics/forms/modelforms.md#modelforms-selecting-fields) for
more information. Omitting any definition of the fields to use will result
in an [`ImproperlyConfigured`](../exceptions.md#django.core.exceptions.ImproperlyConfigured) exception.

### `modelformset_factory`

### modelformset_factory(model, form=ModelForm, formfield_callback=None, formset=BaseModelFormSet, extra=1, can_delete=False, can_order=False, max_num=None, fields=None, exclude=None, widgets=None, validate_max=False, localized_fields=None, labels=None, help_texts=None, error_messages=None, min_num=None, validate_min=False, field_classes=None, absolute_max=None, can_delete_extra=True, renderer=None, edit_only=False)

Returns a `FormSet` class for the given `model` class.

Arguments `model`, `form`, `fields`, `exclude`,
`formfield_callback`, `widgets`, `localized_fields`, `labels`,
`help_texts`, `error_messages`, and `field_classes` are all passed
through to [`modelform_factory()`](#django.forms.models.modelform_factory).

Arguments `formset`, `extra`, `can_delete`, `can_order`,
`max_num`, `validate_max`, `min_num`, `validate_min`,
`absolute_max`, `can_delete_extra`, and `renderer` are passed
through to [`formset_factory()`](formsets.md#django.forms.formsets.formset_factory). See
[formsets](../../topics/forms/formsets.md) for details.

The `edit_only` argument allows [preventing new objects creation](../../topics/forms/modelforms.md#model-formsets-edit-only).

See [Model formsets](../../topics/forms/modelforms.md#model-formsets) for example usage.

### `inlineformset_factory`

### inlineformset_factory(parent_model, model, form=ModelForm, formset=BaseInlineFormSet, fk_name=None, fields=None, exclude=None, extra=3, can_order=False, can_delete=True, max_num=None, formfield_callback=None, widgets=None, validate_max=False, localized_fields=None, labels=None, help_texts=None, error_messages=None, min_num=None, validate_min=False, field_classes=None, absolute_max=None, can_delete_extra=True, renderer=None, edit_only=False)

Returns an `InlineFormSet` using [`modelformset_factory()`](#django.forms.models.modelformset_factory) with
defaults of `formset=`[`BaseInlineFormSet`](../../topics/forms/modelforms.md#django.forms.models.BaseInlineFormSet),
`can_delete=True`, and `extra=3`.

If your model has more than one [`ForeignKey`](../models/fields.md#django.db.models.ForeignKey) to
the `parent_model`, you must specify a `fk_name`.

See [Inline formsets](../../topics/forms/modelforms.md#inline-formsets) for example usage.

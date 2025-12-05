# PostgreSQL specific form fields and widgets

All of these fields and widgets are available from the
`django.contrib.postgres.forms` module.

## Fields

### `SimpleArrayField`

### *class* SimpleArrayField(base_field, delimiter=',', max_length=None, min_length=None)

A field which maps to an array. It is represented by an HTML `<input>`.

#### base_field

This is a required argument.

It specifies the underlying form field for the array. This is not used
to render any HTML, but it is used to process the submitted data and
validate it. For example:

```pycon
>>> from django import forms
>>> from django.contrib.postgres.forms import SimpleArrayField

>>> class NumberListForm(forms.Form):
...     numbers = SimpleArrayField(forms.IntegerField())
...

>>> form = NumberListForm({"numbers": "1,2,3"})
>>> form.is_valid()
True
>>> form.cleaned_data
{'numbers': [1, 2, 3]}

>>> form = NumberListForm({"numbers": "1,2,a"})
>>> form.is_valid()
False
```

#### delimiter

This is an optional argument which defaults to a comma: `,`. This
value is used to split the submitted data. It allows you to chain
`SimpleArrayField` for multidimensional data:

```pycon
>>> from django import forms
>>> from django.contrib.postgres.forms import SimpleArrayField

>>> class GridForm(forms.Form):
...     places = SimpleArrayField(SimpleArrayField(IntegerField()), delimiter="|")
...

>>> form = GridForm({"places": "1,2|2,1|4,3"})
>>> form.is_valid()
True
>>> form.cleaned_data
{'places': [[1, 2], [2, 1], [4, 3]]}
```

#### NOTE
The field does not support escaping of the delimiter, so be careful
in cases where the delimiter is a valid character in the underlying
field. The delimiter does not need to be only one character.

#### max_length

This is an optional argument which validates that the array does not
exceed the stated length.

#### min_length

This is an optional argument which validates that the array reaches at
least the stated length.

### `SplitArrayField`

### *class* SplitArrayField(base_field, size, remove_trailing_nulls=False)

This field handles arrays by reproducing the underlying field a fixed
number of times.

#### base_field

This is a required argument. It specifies the form field to be
repeated.

#### size

This is the fixed number of times the underlying field will be used.

#### remove_trailing_nulls

By default, this is set to `False`. When `False`, each value from
the repeated fields is stored. When set to `True`, any trailing
values which are blank will be stripped from the result. If the
underlying field has `required=True`, but `remove_trailing_nulls`
is `True`, then null values are only allowed at the end, and will be
stripped.

Some examples:

```default
SplitArrayField(IntegerField(required=True), size=3, remove_trailing_nulls=False)

["1", "2", "3"]  # -> [1, 2, 3]
["1", "2", ""]  # -> ValidationError - third entry required.
["1", "", "3"]  # -> ValidationError - second entry required.
["", "2", ""]  # -> ValidationError - first and third entries required.

SplitArrayField(IntegerField(required=False), size=3, remove_trailing_nulls=False)

["1", "2", "3"]  # -> [1, 2, 3]
["1", "2", ""]  # -> [1, 2, None]
["1", "", "3"]  # -> [1, None, 3]
["", "2", ""]  # -> [None, 2, None]

SplitArrayField(IntegerField(required=True), size=3, remove_trailing_nulls=True)

["1", "2", "3"]  # -> [1, 2, 3]
["1", "2", ""]  # -> [1, 2]
["1", "", "3"]  # -> ValidationError - second entry required.
["", "2", ""]  # -> ValidationError - first entry required.

SplitArrayField(IntegerField(required=False), size=3, remove_trailing_nulls=True)

["1", "2", "3"]  # -> [1, 2, 3]
["1", "2", ""]  # -> [1, 2]
["1", "", "3"]  # -> [1, None, 3]
["", "2", ""]  # -> [None, 2]
```

### `HStoreField`

### *class* HStoreField

A field which accepts JSON encoded data for an
[`HStoreField`](fields.md#django.contrib.postgres.fields.HStoreField). It casts all values
(except nulls) to strings. It is represented by an HTML `<textarea>`.

#### NOTE
On occasions it may be useful to require or restrict the keys which are
valid for a given field. This can be done using the
[`KeysValidator`](validators.md#django.contrib.postgres.validators.KeysValidator).

### Range Fields

This group of fields all share similar functionality for accepting range data.
They are based on [`MultiValueField`](../../forms/fields.md#django.forms.MultiValueField). They treat one
omitted value as an unbounded range. They also validate that the lower bound is
not greater than the upper bound. All of these fields use
[`RangeWidget`](#django.contrib.postgres.forms.RangeWidget).

#### `IntegerRangeField`

### *class* IntegerRangeField

Based on [`IntegerField`](../../forms/fields.md#django.forms.IntegerField) and translates its input into
`django.db.backends.postgresql.psycopg_any.NumericRange`. Default for
[`IntegerRangeField`](fields.md#django.contrib.postgres.fields.IntegerRangeField) and
[`BigIntegerRangeField`](fields.md#django.contrib.postgres.fields.BigIntegerRangeField).

#### `DecimalRangeField`

### *class* DecimalRangeField

Based on [`DecimalField`](../../forms/fields.md#django.forms.DecimalField) and translates its input into
`django.db.backends.postgresql.psycopg_any.NumericRange`. Default for
[`DecimalRangeField`](fields.md#django.contrib.postgres.fields.DecimalRangeField).

#### `DateTimeRangeField`

### *class* DateTimeRangeField

Based on [`DateTimeField`](../../forms/fields.md#django.forms.DateTimeField) and translates its input into
`django.db.backends.postgresql.psycopg_any.DateTimeTZRange`. Default for
[`DateTimeRangeField`](fields.md#django.contrib.postgres.fields.DateTimeRangeField).

#### `DateRangeField`

### *class* DateRangeField

Based on [`DateField`](../../forms/fields.md#django.forms.DateField) and translates its input into
`django.db.backends.postgresql.psycopg_any.DateRange`. Default for
[`DateRangeField`](fields.md#django.contrib.postgres.fields.DateRangeField).

## Widgets

### `RangeWidget`

### *class* RangeWidget(base_widget, attrs=None)

Widget used by all of the range fields.
Based on [`MultiWidget`](../../forms/widgets.md#django.forms.MultiWidget).

[`RangeWidget`](#django.contrib.postgres.forms.RangeWidget) has one required argument:

#### base_widget

A [`RangeWidget`](#django.contrib.postgres.forms.RangeWidget) comprises a 2-tuple of `base_widget`.

#### decompress(value)

Takes a single “compressed” value of a field, for example a
[`DateRangeField`](fields.md#django.contrib.postgres.fields.DateRangeField),
and returns a tuple representing a lower and upper bound.

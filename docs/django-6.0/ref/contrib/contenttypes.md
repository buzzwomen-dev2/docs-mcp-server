# The contenttypes framework

Django includes a [`contenttypes`](#module-django.contrib.contenttypes) application that can
track all of the models installed in your Django-powered project, providing a
high-level, generic interface for working with your models.

## Overview

At the heart of the contenttypes application is the
[`ContentType`](#django.contrib.contenttypes.models.ContentType) model, which lives at
`django.contrib.contenttypes.models.ContentType`. Instances of
[`ContentType`](#django.contrib.contenttypes.models.ContentType) represent and store
information about the models installed in your project, and new instances of
[`ContentType`](#django.contrib.contenttypes.models.ContentType) are automatically
created whenever new models are installed.

Instances of [`ContentType`](#django.contrib.contenttypes.models.ContentType) have
methods for returning the model classes they represent and for querying objects
from those models. [`ContentType`](#django.contrib.contenttypes.models.ContentType)
also has a [custom manager](../../topics/db/managers.md#custom-managers) that adds methods for
working with [`ContentType`](#django.contrib.contenttypes.models.ContentType) and for
obtaining instances of [`ContentType`](#django.contrib.contenttypes.models.ContentType)
for a particular model.

Relations between your models and
[`ContentType`](#django.contrib.contenttypes.models.ContentType) can also be used to
enable “generic” relationships between an instance of one of your
models and instances of any model you have installed.

## Installing the contenttypes framework

The contenttypes framework is included in the default
[`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS) list created by `django-admin startproject`,
but if you’ve removed it or if you manually set up your
[`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS) list, you can enable it by adding
`'django.contrib.contenttypes'` to your [`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS) setting.

It’s generally a good idea to have the contenttypes framework
installed; several of Django’s other bundled applications require it:

* The admin application uses it to log the history of each object
  added or changed through the admin interface.
* Django’s [`authentication framework`](../../topics/auth/index.md#module-django.contrib.auth) uses it
  to tie user permissions to specific models.

## The `ContentType` model

### *class* ContentType

Each instance of [`ContentType`](#django.contrib.contenttypes.models.ContentType)
has two fields which, taken together, uniquely describe an installed
model:

#### app_label

The name of the application the model is part of. This is taken from
the [`app_label`](#django.contrib.contenttypes.models.ContentType.app_label) attribute of the model, and includes only the
*last* part of the application’s Python import path;
`django.contrib.contenttypes`, for example, becomes an
[`app_label`](#django.contrib.contenttypes.models.ContentType.app_label) of `contenttypes`.

#### model

The name of the model class.

Additionally, the following property is available:

#### name

The human-readable name of the content type. This is taken from the
[`verbose_name`](../models/fields.md#django.db.models.Field.verbose_name)
attribute of the model.

Let’s look at an example to see how this works. If you already have
the [`contenttypes`](#module-django.contrib.contenttypes) application installed, and then add
[`the sites application`](sites.md#module-django.contrib.sites) to your
[`INSTALLED_APPS`](../settings.md#std-setting-INSTALLED_APPS) setting and run `manage.py migrate` to install it,
the model [`django.contrib.sites.models.Site`](sites.md#django.contrib.sites.models.Site) will be installed into
your database. Along with it a new instance of
[`ContentType`](#django.contrib.contenttypes.models.ContentType) will be
created with the following values:

* [`app_label`](#django.contrib.contenttypes.models.ContentType.app_label)
  will be set to `'sites'` (the last part of the Python
  path `django.contrib.sites`).
* [`model`](#django.contrib.contenttypes.models.ContentType.model)
  will be set to `'site'`.

## Methods on `ContentType` instances

Each [`ContentType`](#django.contrib.contenttypes.models.ContentType) instance has
methods that allow you to get from a
[`ContentType`](#django.contrib.contenttypes.models.ContentType) instance to the
model it represents, or to retrieve objects from that model:

#### ContentType.get_object_for_this_type(using=None, \*\*kwargs)

Takes a set of valid [lookup arguments](../../topics/db/queries.md#field-lookups-intro) for the
model the [`ContentType`](#django.contrib.contenttypes.models.ContentType)
represents, and does a [`get()`](../models/querysets.md#django.db.models.query.QuerySet.get) lookup
on that model, returning the corresponding object. The `using` argument
can be used to specify a different database than the default one.

#### ContentType.model_class()

Returns the model class represented by this
[`ContentType`](#django.contrib.contenttypes.models.ContentType) instance.

For example, we could look up the
[`ContentType`](#django.contrib.contenttypes.models.ContentType) for the
[`User`](auth.md#django.contrib.auth.models.User) model:

```pycon
>>> from django.contrib.contenttypes.models import ContentType
>>> user_type = ContentType.objects.get(app_label="auth", model="user")
>>> user_type
<ContentType: user>
```

And then use it to query for a particular
[`User`](auth.md#django.contrib.auth.models.User), or to get access
to the `User` model class:

```pycon
>>> user_type.model_class()
<class 'django.contrib.auth.models.User'>
>>> user_type.get_object_for_this_type(username="Guido")
<User: Guido>
```

Together,
[`get_object_for_this_type()`](#django.contrib.contenttypes.models.ContentType.get_object_for_this_type)
and [`model_class()`](#django.contrib.contenttypes.models.ContentType.model_class) enable
two extremely important use cases:

1. Using these methods, you can write high-level generic code that
   performs queries on any installed model – instead of importing and
   using a single specific model class, you can pass an `app_label` and
   `model` into a
   [`ContentType`](#django.contrib.contenttypes.models.ContentType) lookup at
   runtime, and then work with the model class or retrieve objects from it.
2. You can relate another model to
   [`ContentType`](#django.contrib.contenttypes.models.ContentType) as a way of
   tying instances of it to particular model classes, and use these methods
   to get access to those model classes.

Several of Django’s bundled applications make use of the latter technique.
For example, [the permissions system](../../topics/auth/default.md#topic-authorization) in Django’s
authentication framework uses a [`Permission`](auth.md#django.contrib.auth.models.Permission)
model with a foreign key to
[`ContentType`](#django.contrib.contenttypes.models.ContentType); this lets
[`Permission`](auth.md#django.contrib.auth.models.Permission) represent concepts like
“can add blog entry” or “can delete news story”.

### The `ContentTypeManager`

### *class* ContentTypeManager

[`ContentType`](#django.contrib.contenttypes.models.ContentType) also has a custom
manager, [`ContentTypeManager`](#django.contrib.contenttypes.models.ContentTypeManager),
which adds the following methods:

#### clear_cache()

Clears an internal cache used by
[`ContentType`](#django.contrib.contenttypes.models.ContentType) to keep track
of models for which it has created
[`ContentType`](#django.contrib.contenttypes.models.ContentType) instances. You
probably won’t ever need to call this method yourself; Django will call
it automatically when it’s needed.

#### get_for_id(id)

Lookup a [`ContentType`](#django.contrib.contenttypes.models.ContentType) by
ID. Since this method uses the same shared cache as
[`get_for_model()`](#django.contrib.contenttypes.models.ContentTypeManager.get_for_model),
it’s preferred to use this method over the usual
`ContentType.objects.get(pk=id)`

#### get_for_model(model, for_concrete_model=True)

Takes either a model class or an instance of a model, and returns the
[`ContentType`](#django.contrib.contenttypes.models.ContentType) instance
representing that model. `for_concrete_model=False` allows fetching
the [`ContentType`](#django.contrib.contenttypes.models.ContentType) of a proxy
model.

#### get_for_models(\*models, for_concrete_models=True)

Takes a variadic number of model classes, and returns a dictionary
mapping the model classes to the
[`ContentType`](#django.contrib.contenttypes.models.ContentType) instances
representing them. `for_concrete_models=False` allows fetching the
[`ContentType`](#django.contrib.contenttypes.models.ContentType) of proxy
models.

#### get_by_natural_key(app_label, model)

Returns the [`ContentType`](#django.contrib.contenttypes.models.ContentType)
instance uniquely identified by the given application label and model
name. The primary purpose of this method is to allow
[`ContentType`](#django.contrib.contenttypes.models.ContentType) objects to be
referenced via a [natural key](../../topics/serialization.md#topics-serialization-natural-keys)
during deserialization.

The [`get_for_model()`](#django.contrib.contenttypes.models.ContentTypeManager.get_for_model) method is especially
useful when you know you need to work with a
[`ContentType`](#django.contrib.contenttypes.models.ContentType) but don’t
want to go to the trouble of obtaining the model’s metadata to perform a manual
lookup:

```pycon
>>> from django.contrib.auth.models import User
>>> ContentType.objects.get_for_model(User)
<ContentType: user>
```

<a id="module-django.contrib.contenttypes.fields"></a>

<a id="generic-relations"></a>

## Generic relations

Adding a foreign key from one of your own models to
[`ContentType`](#django.contrib.contenttypes.models.ContentType) allows your model to
effectively tie itself to another model class, as in the example of the
[`Permission`](auth.md#django.contrib.auth.models.Permission) model above. But it’s possible
to go one step further and use
[`ContentType`](#django.contrib.contenttypes.models.ContentType) to enable truly
generic (sometimes called “polymorphic”) relationships between models.

For example, it could be used for a tagging system like so:

```default
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class TaggedItem(models.Model):
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.tag

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
```

A normal [`ForeignKey`](../models/fields.md#django.db.models.ForeignKey) can only “point
to” one other model, which means that if the `TaggedItem` model used a
[`ForeignKey`](../models/fields.md#django.db.models.ForeignKey) it would have to
choose one and only one model to store tags for. The contenttypes
application provides a special field type (`GenericForeignKey`) which
works around this and allows the relationship to be with any
model:

### *class* GenericForeignKey

There are three parts to setting up a
[`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey):

1. Give your model a [`ForeignKey`](../models/fields.md#django.db.models.ForeignKey)
   to [`ContentType`](#django.contrib.contenttypes.models.ContentType). The usual
   name for this field is “content_type”.
2. Give your model a field that can store primary key values from the
   models you’ll be relating to. For most models, this means a
   [`PositiveBigIntegerField`](../models/fields.md#django.db.models.PositiveBigIntegerField). The usual name
   for this field is “object_id”.
3. Give your model a
   [`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey), and
   pass it the names of the two fields described above. If these fields
   are named “content_type” and “object_id”, you can omit this – those
   are the default field names
   [`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey) will
   look for.

Unlike for the [`ForeignKey`](../models/fields.md#django.db.models.ForeignKey), a database index is
*not* automatically created on the
[`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey), so it’s
recommended that you use
[`Meta.indexes`](../models/options.md#django.db.models.Options.indexes) to add your own
multiple column index. This behavior [may change](https://code.djangoproject.com/ticket/23435) in the
future.

#### for_concrete_model

If `False`, the field will be able to reference proxy models. Default
is `True`. This mirrors the `for_concrete_model` argument to
[`get_for_model()`](#django.contrib.contenttypes.models.ContentTypeManager.get_for_model).

This will enable an API similar to the one used for a normal
[`ForeignKey`](../models/fields.md#django.db.models.ForeignKey);
each `TaggedItem` will have a `content_object` field that returns the
object it’s related to, and you can also assign to that field or use it when
creating a `TaggedItem`:

```pycon
>>> from django.contrib.auth.models import User
>>> guido = User.objects.get(username="Guido")
>>> t = TaggedItem(content_object=guido, tag="bdfl")
>>> t.save()
>>> t.content_object
<User: Guido>
```

If the related object is deleted, the `content_type` and `object_id` fields
remain set to their original values and the `GenericForeignKey` returns
`None`:

```pycon
>>> guido.delete()
>>> t.content_object  # returns None
```

Due to the way [`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey)
is implemented, you cannot use such fields directly with filters (`filter()`
and `exclude()`, for example) via the database API. Because a
[`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey) isn’t a
normal field object, these examples will *not* work:

```pycon
# This will fail
>>> TaggedItem.objects.filter(content_object=guido)
# This will also fail
>>> TaggedItem.objects.get(content_object=guido)
```

Likewise, [`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey)s
do not appear in [`ModelForm`](../../topics/forms/modelforms.md#django.forms.ModelForm)s.

### Reverse generic relations

### *class* GenericRelation

#### related_query_name

The relation on the related object back to this object doesn’t exist by
default. Setting `related_query_name` creates a relation from the
related object back to this one. This allows querying and filtering
from the related object.

If you know which models you’ll be using most often, you can also add
a “reverse” generic relationship to enable an additional API. For example:

```default
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class Bookmark(models.Model):
    url = models.URLField()
    tags = GenericRelation(TaggedItem)
```

`Bookmark` instances will each have a `tags` attribute, which can
be used to retrieve their associated `TaggedItems`:

```pycon
>>> b = Bookmark(url="https://www.djangoproject.com/")
>>> b.save()
>>> t1 = TaggedItem(content_object=b, tag="django")
>>> t1.save()
>>> t2 = TaggedItem(content_object=b, tag="python")
>>> t2.save()
>>> b.tags.all()
<QuerySet [<TaggedItem: django>, <TaggedItem: python>]>
```

You can also use `add()`, `create()`, or `set()` to create
relationships:

```pycon
>>> t3 = TaggedItem(tag="Web development")
>>> b.tags.add(t3, bulk=False)
>>> b.tags.create(tag="Web framework")
<TaggedItem: Web framework>
>>> b.tags.all()
<QuerySet [<TaggedItem: django>, <TaggedItem: python>, <TaggedItem: Web development>, <TaggedItem: Web framework>]>
>>> b.tags.set([t1, t3])
>>> b.tags.all()
<QuerySet [<TaggedItem: django>, <TaggedItem: Web development>]>
```

The `remove()` call will bulk delete the specified model objects:

```pycon
>>> b.tags.remove(t3)
>>> b.tags.all()
<QuerySet [<TaggedItem: django>]>
>>> TaggedItem.objects.all()
<QuerySet [<TaggedItem: django>]>
```

The `clear()` method can be used to bulk delete all related objects for an
instance:

```pycon
>>> b.tags.clear()
>>> b.tags.all()
<QuerySet []>
>>> TaggedItem.objects.all()
<QuerySet []>
```

Defining [`GenericRelation`](#django.contrib.contenttypes.fields.GenericRelation) with
`related_query_name` set allows querying from the related object:

```default
tags = GenericRelation(TaggedItem, related_query_name="bookmark")
```

This enables filtering, ordering, and other query operations on `Bookmark`
from `TaggedItem`:

```pycon
>>> # Get all tags belonging to bookmarks containing `django` in the url
>>> TaggedItem.objects.filter(bookmark__url__contains="django")
<QuerySet [<TaggedItem: django>, <TaggedItem: python>]>
```

If you don’t add the `related_query_name`, you can do the same types of
lookups manually:

```pycon
>>> bookmarks = Bookmark.objects.filter(url__contains="django")
>>> bookmark_type = ContentType.objects.get_for_model(Bookmark)
>>> TaggedItem.objects.filter(content_type__pk=bookmark_type.id, object_id__in=bookmarks)
<QuerySet [<TaggedItem: django>, <TaggedItem: python>]>
```

Just as [`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey)
accepts the names of the content-type and object-ID fields as
arguments, so too does
[`GenericRelation`](#django.contrib.contenttypes.fields.GenericRelation);
if the model which has the generic foreign key is using non-default names
for those fields, you must pass the names of the fields when setting up a
[`GenericRelation`](#django.contrib.contenttypes.fields.GenericRelation) to it. For example, if the `TaggedItem` model
referred to above used fields named `content_type_fk` and
`object_primary_key` to create its generic foreign key, then a
[`GenericRelation`](#django.contrib.contenttypes.fields.GenericRelation) back to it would need to be defined like so:

```default
tags = GenericRelation(
    TaggedItem,
    content_type_field="content_type_fk",
    object_id_field="object_primary_key",
)
```

Note also, that if you delete an object that has a
[`GenericRelation`](#django.contrib.contenttypes.fields.GenericRelation), any objects
which have a [`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey)
pointing at it will be deleted as well. In the example above, this means that
if a `Bookmark` object were deleted, any `TaggedItem` objects pointing at
it would be deleted at the same time.

Unlike [`ForeignKey`](../models/fields.md#django.db.models.ForeignKey),
[`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey) does not accept
an [`on_delete`](../models/fields.md#django.db.models.ForeignKey.on_delete) argument to customize this
behavior; if desired, you can avoid the cascade-deletion by not using
[`GenericRelation`](#django.contrib.contenttypes.fields.GenericRelation), and alternate
behavior can be provided via the [`pre_delete`](../signals.md#django.db.models.signals.pre_delete)
signal.

### Generic relations and aggregation

[Django’s database aggregation API](../../topics/db/aggregation.md) works with a
[`GenericRelation`](#django.contrib.contenttypes.fields.GenericRelation). For example, you
can find out how many tags all the bookmarks have:

```pycon
>>> Bookmark.objects.aggregate(Count("tags"))
{'tags__count': 3}
```

<a id="module-django.contrib.contenttypes.forms"></a>

### Generic relation in forms

The [`django.contrib.contenttypes.forms`](#module-django.contrib.contenttypes.forms) module provides:

* [`BaseGenericInlineFormSet`](#django.contrib.contenttypes.forms.BaseGenericInlineFormSet)
* A formset factory, [`generic_inlineformset_factory()`](#django.contrib.contenttypes.forms.generic_inlineformset_factory), for use with
  [`GenericForeignKey`](#django.contrib.contenttypes.fields.GenericForeignKey).

### *class* BaseGenericInlineFormSet

### generic_inlineformset_factory(model, form=ModelForm, formset=BaseGenericInlineFormSet, ct_field='content_type', fk_field='object_id', fields=None, exclude=None, extra=3, can_order=False, can_delete=True, max_num=None, formfield_callback=None, validate_max=False, for_concrete_model=True, min_num=None, validate_min=False, absolute_max=None, can_delete_extra=True)

Returns a `GenericInlineFormSet` using
[`modelformset_factory()`](../forms/models.md#django.forms.models.modelformset_factory).

You must provide `ct_field` and `fk_field` if they are different from
the defaults, `content_type` and `object_id` respectively. Other
parameters are similar to those documented in
[`modelformset_factory()`](../forms/models.md#django.forms.models.modelformset_factory) and
[`inlineformset_factory()`](../forms/models.md#django.forms.models.inlineformset_factory).

The `for_concrete_model` argument corresponds to the
[`for_concrete_model`](#django.contrib.contenttypes.fields.GenericForeignKey.for_concrete_model)
argument on `GenericForeignKey`.

<a id="module-django.contrib.contenttypes.admin"></a>

### Generic relations in admin

The [`django.contrib.contenttypes.admin`](#module-django.contrib.contenttypes.admin) module provides
[`GenericTabularInline`](#django.contrib.contenttypes.admin.GenericTabularInline) and
[`GenericStackedInline`](#django.contrib.contenttypes.admin.GenericStackedInline) (subclasses of
[`GenericInlineModelAdmin`](#django.contrib.contenttypes.admin.GenericInlineModelAdmin))

These classes and functions enable the use of generic relations in forms
and the admin. See the [model formset](../../topics/forms/modelforms.md) and
[admin](admin/index.md#using-generic-relations-as-an-inline) documentation for more
information.

### *class* GenericInlineModelAdmin

The [`GenericInlineModelAdmin`](#django.contrib.contenttypes.admin.GenericInlineModelAdmin)
class inherits all properties from an
[`InlineModelAdmin`](admin/index.md#django.contrib.admin.InlineModelAdmin) class. However,
it adds a couple of its own for working with the generic relation:

#### ct_field

The name of the
[`ContentType`](#django.contrib.contenttypes.models.ContentType) foreign key
field on the model. Defaults to `content_type`.

#### ct_fk_field

The name of the integer field that represents the ID of the related
object. Defaults to `object_id`.

### *class* GenericTabularInline

### *class* GenericStackedInline

Subclasses of [`GenericInlineModelAdmin`](#django.contrib.contenttypes.admin.GenericInlineModelAdmin) with stacked and tabular
layouts, respectively.

<a id="module-django.contrib.contenttypes.prefetch"></a>

### `GenericPrefetch()`

### *class* GenericPrefetch(lookup, querysets, to_attr=None)

This lookup is similar to `Prefetch()` and it should only be used on
`GenericForeignKey`. The `querysets` argument accepts a list of querysets,
each for a different `ContentType`. This is useful for `GenericForeignKey`
with non-homogeneous set of results.

```pycon
>>> from django.contrib.contenttypes.prefetch import GenericPrefetch
>>> bookmark = Bookmark.objects.create(url="https://www.djangoproject.com/")
>>> animal = Animal.objects.create(name="lion", weight=100)
>>> TaggedItem.objects.create(tag="great", content_object=bookmark)
>>> TaggedItem.objects.create(tag="awesome", content_object=animal)
>>> prefetch = GenericPrefetch(
...     "content_object", [Bookmark.objects.all(), Animal.objects.only("name")]
... )
>>> TaggedItem.objects.prefetch_related(prefetch).all()
<QuerySet [<TaggedItem: Great>, <TaggedItem: Awesome>]>
```

# Class-based generic views - flattened index

This index provides an alternate organization of the reference documentation
for class-based views. For each view, the effective attributes and methods from
the class tree are represented under that view. For the reference
documentation organized by the class which defines the behavior, see
[Class-based views](index.md).

#### SEE ALSO
[Classy Class-Based Views](https://ccbv.co.uk/) provides a nice interface
to navigate the class hierarchy of the built-in class-based views.

## Simple generic views

### `View`

### *class* View

**Attributes** (with optional accessor):

* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `TemplateView`

### *class* TemplateView

**Attributes** (with optional accessor):

* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-simple.md#django.views.generic.base.ContextMixin.get_context_data)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `RedirectView`

### *class* RedirectView

**Attributes** (with optional accessor):

* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`pattern_name`](base.md#django.views.generic.base.RedirectView.pattern_name)
* [`permanent`](base.md#django.views.generic.base.RedirectView.permanent)
* [`query_string`](base.md#django.views.generic.base.RedirectView.query_string)
* [`url`](base.md#django.views.generic.base.RedirectView.url) [[`get_redirect_url()`](base.md#django.views.generic.base.RedirectView.get_redirect_url)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* `delete()`
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* `options()`
* `post()`
* `put()`
* [`setup()`](base.md#django.views.generic.base.View.setup)

## Detail Views

### `DetailView`

### *class* DetailView

**Attributes** (with optional accessor):

* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_context_object_name)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.model)
* [`pk_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.pk_url_kwarg)
* [`query_pk_and_slug`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.query_pk_and_slug)
* [`queryset`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.queryset) [[`get_queryset()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`slug_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_field) [[`get_slug_field()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_slug_field)]
* [`slug_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_url_kwarg)
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_field)
* [`template_name_suffix`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_suffix)

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* [`get()`](generic-display.md#django.views.generic.detail.BaseDetailView.get)
* [`get_context_data()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_context_data)
* [`get_object()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_object)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

## List Views

### `ListView`

### *class* ListView

**Attributes** (with optional accessor):

* [`allow_empty`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.allow_empty) [[`get_allow_empty()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_allow_empty)]
* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_object_name)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.model)
* [`ordering`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.ordering) [[`get_ordering()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_ordering)]
* [`paginate_by`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_by) [[`get_paginate_by()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_by)]
* [`paginate_orphans`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_orphans) [[`get_paginate_orphans()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_orphans)]
* [`paginator_class`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginator_class)
* [`queryset`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.queryset) [[`get_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_suffix`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectTemplateResponseMixin.template_name_suffix)

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* [`get()`](generic-display.md#django.views.generic.list.BaseListView.get)
* [`get_context_data()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_data)
* [`get_paginator()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginator)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`paginate_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_queryset)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

## Editing views

### `FormView`

### *class* FormView

**Attributes** (with optional accessor):

* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`form_class`](mixins-editing.md#django.views.generic.edit.FormMixin.form_class) [[`get_form_class()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_form_class)]
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`initial`](mixins-editing.md#django.views.generic.edit.FormMixin.initial) [[`get_initial()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_initial)]
* [`prefix`](mixins-editing.md#django.views.generic.edit.FormMixin.prefix) [[`get_prefix()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_prefix)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`success_url`](mixins-editing.md#django.views.generic.edit.FormMixin.success_url) [[`get_success_url()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_success_url)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* [`form_invalid()`](mixins-editing.md#django.views.generic.edit.FormMixin.form_invalid)
* [`form_valid()`](mixins-editing.md#django.views.generic.edit.FormMixin.form_valid)
* [`get()`](mixins-editing.md#django.views.generic.edit.ProcessFormView.get)
* [`get_context_data()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_context_data)
* [`get_form()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_form)
* [`get_form_kwargs()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_form_kwargs)
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`post()`](mixins-editing.md#django.views.generic.edit.ProcessFormView.post)
* [`put()`](mixins-editing.md#django.views.generic.edit.ProcessFormView.put)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `CreateView`

### *class* CreateView

**Attributes** (with optional accessor):

* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_context_object_name)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`fields`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.fields)
* [`form_class`](mixins-editing.md#django.views.generic.edit.FormMixin.form_class) [[`get_form_class()`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.get_form_class)]
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`initial`](mixins-editing.md#django.views.generic.edit.FormMixin.initial) [[`get_initial()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_initial)]
* [`model`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.model)
* [`pk_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.pk_url_kwarg)
* [`prefix`](mixins-editing.md#django.views.generic.edit.FormMixin.prefix) [[`get_prefix()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_prefix)]
* [`query_pk_and_slug`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.query_pk_and_slug)
* [`queryset`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.queryset) [[`get_queryset()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`slug_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_field) [[`get_slug_field()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_slug_field)]
* [`slug_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_url_kwarg)
* [`success_url`](mixins-editing.md#django.views.generic.edit.FormMixin.success_url) [[`get_success_url()`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.get_success_url)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_field)
* [`template_name_suffix`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_suffix)

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* [`form_invalid()`](mixins-editing.md#django.views.generic.edit.FormMixin.form_invalid)
* [`form_valid()`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.form_valid)
* [`get()`](mixins-editing.md#django.views.generic.edit.ProcessFormView.get)
* [`get_context_data()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_context_data)
* [`get_form()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_form)
* [`get_form_kwargs()`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.get_form_kwargs)
* [`get_object()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_object)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`post()`](mixins-editing.md#django.views.generic.edit.ProcessFormView.post)
* `put()`
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `UpdateView`

### *class* UpdateView

**Attributes** (with optional accessor):

* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_context_object_name)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`fields`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.fields)
* [`form_class`](mixins-editing.md#django.views.generic.edit.FormMixin.form_class) [[`get_form_class()`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.get_form_class)]
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`initial`](mixins-editing.md#django.views.generic.edit.FormMixin.initial) [[`get_initial()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_initial)]
* [`model`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.model)
* [`pk_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.pk_url_kwarg)
* [`prefix`](mixins-editing.md#django.views.generic.edit.FormMixin.prefix) [[`get_prefix()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_prefix)]
* [`query_pk_and_slug`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.query_pk_and_slug)
* [`queryset`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.queryset) [[`get_queryset()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`slug_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_field) [[`get_slug_field()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_slug_field)]
* [`slug_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_url_kwarg)
* [`success_url`](mixins-editing.md#django.views.generic.edit.FormMixin.success_url) [[`get_success_url()`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.get_success_url)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_field)
* [`template_name_suffix`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_suffix)

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* [`form_invalid()`](mixins-editing.md#django.views.generic.edit.FormMixin.form_invalid)
* [`form_valid()`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.form_valid)
* [`get()`](mixins-editing.md#django.views.generic.edit.ProcessFormView.get)
* [`get_context_data()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_context_data)
* [`get_form()`](mixins-editing.md#django.views.generic.edit.FormMixin.get_form)
* [`get_form_kwargs()`](mixins-editing.md#django.views.generic.edit.ModelFormMixin.get_form_kwargs)
* [`get_object()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_object)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`post()`](mixins-editing.md#django.views.generic.edit.ProcessFormView.post)
* `put()`
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `DeleteView`

### *class* DeleteView

**Attributes** (with optional accessor):

* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_context_object_name)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.model)
* [`pk_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.pk_url_kwarg)
* [`query_pk_and_slug`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.query_pk_and_slug)
* [`queryset`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.queryset) [[`get_queryset()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`slug_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_field) [[`get_slug_field()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_slug_field)]
* [`slug_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_url_kwarg)
* [`success_url`](mixins-editing.md#django.views.generic.edit.DeletionMixin.success_url) [[`get_success_url()`](mixins-editing.md#django.views.generic.edit.DeletionMixin.get_success_url)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_field)
* [`template_name_suffix`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_suffix)

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* `delete()`
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_context_data)
* [`get_object()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_object)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* `post()`
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

## Date-based views

### `ArchiveIndexView`

### *class* ArchiveIndexView

**Attributes** (with optional accessor):

* [`allow_empty`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.allow_empty) [[`get_allow_empty()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_allow_empty)]
* [`allow_future`](mixins-date-based.md#django.views.generic.dates.DateMixin.allow_future) [[`get_allow_future()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_allow_future)]
* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_object_name)]
* [`date_field`](mixins-date-based.md#django.views.generic.dates.DateMixin.date_field) [[`get_date_field()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_date_field)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.model)
* [`ordering`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.ordering) [[`get_ordering()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_ordering)]
* [`paginate_by`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_by) [[`get_paginate_by()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_by)]
* [`paginate_orphans`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_orphans) [[`get_paginate_orphans()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_orphans)]
* [`paginator_class`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginator_class)
* [`queryset`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.queryset) [[`get_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_suffix`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectTemplateResponseMixin.template_name_suffix)

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_data)
* [`get_date_list()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_date_list)
* [`get_dated_items()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_items)
* [`get_dated_queryset()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_queryset)
* [`get_paginator()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginator)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`paginate_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_queryset)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `YearArchiveView`

### *class* YearArchiveView

**Attributes** (with optional accessor):

* [`allow_empty`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.allow_empty) [[`get_allow_empty()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_allow_empty)]
* [`allow_future`](mixins-date-based.md#django.views.generic.dates.DateMixin.allow_future) [[`get_allow_future()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_allow_future)]
* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_object_name)]
* [`date_field`](mixins-date-based.md#django.views.generic.dates.DateMixin.date_field) [[`get_date_field()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_date_field)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`make_object_list`](generic-date-based.md#django.views.generic.dates.YearArchiveView.make_object_list) [[`get_make_object_list()`](generic-date-based.md#django.views.generic.dates.YearArchiveView.get_make_object_list)]
* [`model`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.model)
* [`ordering`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.ordering) [[`get_ordering()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_ordering)]
* [`paginate_by`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_by) [[`get_paginate_by()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_by)]
* [`paginate_orphans`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_orphans) [[`get_paginate_orphans()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_orphans)]
* [`paginator_class`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginator_class)
* [`queryset`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.queryset) [[`get_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_suffix`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectTemplateResponseMixin.template_name_suffix)
* [`year`](mixins-date-based.md#django.views.generic.dates.YearMixin.year) [[`get_year()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year)]
* [`year_format`](mixins-date-based.md#django.views.generic.dates.YearMixin.year_format) [[`get_year_format()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year_format)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_data)
* [`get_date_list()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_date_list)
* [`get_dated_items()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_items)
* [`get_dated_queryset()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_queryset)
* [`get_paginator()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginator)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`paginate_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_queryset)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `MonthArchiveView`

### *class* MonthArchiveView

**Attributes** (with optional accessor):

* [`allow_empty`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.allow_empty) [[`get_allow_empty()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_allow_empty)]
* [`allow_future`](mixins-date-based.md#django.views.generic.dates.DateMixin.allow_future) [[`get_allow_future()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_allow_future)]
* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_object_name)]
* [`date_field`](mixins-date-based.md#django.views.generic.dates.DateMixin.date_field) [[`get_date_field()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_date_field)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.model)
* [`month`](mixins-date-based.md#django.views.generic.dates.MonthMixin.month) [[`get_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_month)]
* [`month_format`](mixins-date-based.md#django.views.generic.dates.MonthMixin.month_format) [[`get_month_format()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_month_format)]
* [`ordering`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.ordering) [[`get_ordering()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_ordering)]
* [`paginate_by`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_by) [[`get_paginate_by()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_by)]
* [`paginate_orphans`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_orphans) [[`get_paginate_orphans()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_orphans)]
* [`paginator_class`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginator_class)
* [`queryset`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.queryset) [[`get_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_suffix`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectTemplateResponseMixin.template_name_suffix)
* [`year`](mixins-date-based.md#django.views.generic.dates.YearMixin.year) [[`get_year()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year)]
* [`year_format`](mixins-date-based.md#django.views.generic.dates.YearMixin.year_format) [[`get_year_format()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year_format)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_data)
* [`get_date_list()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_date_list)
* [`get_dated_items()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_items)
* [`get_dated_queryset()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_queryset)
* [`get_next_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_next_month)
* [`get_paginator()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginator)
* [`get_previous_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_previous_month)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`paginate_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_queryset)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `WeekArchiveView`

### *class* WeekArchiveView

**Attributes** (with optional accessor):

* [`allow_empty`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.allow_empty) [[`get_allow_empty()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_allow_empty)]
* [`allow_future`](mixins-date-based.md#django.views.generic.dates.DateMixin.allow_future) [[`get_allow_future()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_allow_future)]
* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_object_name)]
* [`date_field`](mixins-date-based.md#django.views.generic.dates.DateMixin.date_field) [[`get_date_field()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_date_field)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.model)
* [`ordering`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.ordering) [[`get_ordering()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_ordering)]
* [`paginate_by`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_by) [[`get_paginate_by()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_by)]
* [`paginate_orphans`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_orphans) [[`get_paginate_orphans()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_orphans)]
* [`paginator_class`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginator_class)
* [`queryset`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.queryset) [[`get_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_suffix`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectTemplateResponseMixin.template_name_suffix)
* [`week`](mixins-date-based.md#django.views.generic.dates.WeekMixin.week) [[`get_week()`](mixins-date-based.md#django.views.generic.dates.WeekMixin.get_week)]
* [`week_format`](mixins-date-based.md#django.views.generic.dates.WeekMixin.week_format) [[`get_week_format()`](mixins-date-based.md#django.views.generic.dates.WeekMixin.get_week_format)]
* [`year`](mixins-date-based.md#django.views.generic.dates.YearMixin.year) [[`get_year()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year)]
* [`year_format`](mixins-date-based.md#django.views.generic.dates.YearMixin.year_format) [[`get_year_format()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year_format)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_data)
* [`get_date_list()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_date_list)
* [`get_dated_items()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_items)
* [`get_dated_queryset()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_queryset)
* [`get_paginator()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginator)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`paginate_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_queryset)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `DayArchiveView`

### *class* DayArchiveView

**Attributes** (with optional accessor):

* [`allow_empty`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.allow_empty) [[`get_allow_empty()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_allow_empty)]
* [`allow_future`](mixins-date-based.md#django.views.generic.dates.DateMixin.allow_future) [[`get_allow_future()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_allow_future)]
* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_object_name)]
* [`date_field`](mixins-date-based.md#django.views.generic.dates.DateMixin.date_field) [[`get_date_field()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_date_field)]
* [`day`](mixins-date-based.md#django.views.generic.dates.DayMixin.day) [[`get_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_day)]
* [`day_format`](mixins-date-based.md#django.views.generic.dates.DayMixin.day_format) [[`get_day_format()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_day_format)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.model)
* [`month`](mixins-date-based.md#django.views.generic.dates.MonthMixin.month) [[`get_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_month)]
* [`month_format`](mixins-date-based.md#django.views.generic.dates.MonthMixin.month_format) [[`get_month_format()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_month_format)]
* [`ordering`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.ordering) [[`get_ordering()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_ordering)]
* [`paginate_by`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_by) [[`get_paginate_by()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_by)]
* [`paginate_orphans`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_orphans) [[`get_paginate_orphans()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_orphans)]
* [`paginator_class`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginator_class)
* [`queryset`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.queryset) [[`get_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_suffix`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectTemplateResponseMixin.template_name_suffix)
* [`year`](mixins-date-based.md#django.views.generic.dates.YearMixin.year) [[`get_year()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year)]
* [`year_format`](mixins-date-based.md#django.views.generic.dates.YearMixin.year_format) [[`get_year_format()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year_format)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_data)
* [`get_date_list()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_date_list)
* [`get_dated_items()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_items)
* [`get_dated_queryset()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_queryset)
* [`get_next_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_next_day)
* [`get_next_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_next_month)
* [`get_paginator()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginator)
* [`get_previous_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_previous_day)
* [`get_previous_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_previous_month)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`paginate_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_queryset)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `TodayArchiveView`

### *class* TodayArchiveView

**Attributes** (with optional accessor):

* [`allow_empty`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.allow_empty) [[`get_allow_empty()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_allow_empty)]
* [`allow_future`](mixins-date-based.md#django.views.generic.dates.DateMixin.allow_future) [[`get_allow_future()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_allow_future)]
* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_object_name)]
* [`date_field`](mixins-date-based.md#django.views.generic.dates.DateMixin.date_field) [[`get_date_field()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_date_field)]
* [`day`](mixins-date-based.md#django.views.generic.dates.DayMixin.day) [[`get_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_day)]
* [`day_format`](mixins-date-based.md#django.views.generic.dates.DayMixin.day_format) [[`get_day_format()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_day_format)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.model)
* [`month`](mixins-date-based.md#django.views.generic.dates.MonthMixin.month) [[`get_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_month)]
* [`month_format`](mixins-date-based.md#django.views.generic.dates.MonthMixin.month_format) [[`get_month_format()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_month_format)]
* [`ordering`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.ordering) [[`get_ordering()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_ordering)]
* [`paginate_by`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_by) [[`get_paginate_by()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_by)]
* [`paginate_orphans`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_orphans) [[`get_paginate_orphans()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginate_orphans)]
* [`paginator_class`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginator_class)
* [`queryset`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.queryset) [[`get_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_suffix`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectTemplateResponseMixin.template_name_suffix)
* [`year`](mixins-date-based.md#django.views.generic.dates.YearMixin.year) [[`get_year()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year)]
* [`year_format`](mixins-date-based.md#django.views.generic.dates.YearMixin.year_format) [[`get_year_format()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year_format)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_context_data)
* [`get_date_list()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_date_list)
* [`get_dated_items()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_items)
* [`get_dated_queryset()`](mixins-date-based.md#django.views.generic.dates.BaseDateListView.get_dated_queryset)
* [`get_next_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_next_day)
* [`get_next_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_next_month)
* [`get_paginator()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.get_paginator)
* [`get_previous_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_previous_day)
* [`get_previous_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_previous_month)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`paginate_queryset()`](mixins-multiple-object.md#django.views.generic.list.MultipleObjectMixin.paginate_queryset)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

### `DateDetailView`

### *class* DateDetailView

**Attributes** (with optional accessor):

* [`allow_future`](mixins-date-based.md#django.views.generic.dates.DateMixin.allow_future) [[`get_allow_future()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_allow_future)]
* [`content_type`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.content_type)
* [`context_object_name`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.context_object_name) [[`get_context_object_name()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_context_object_name)]
* [`date_field`](mixins-date-based.md#django.views.generic.dates.DateMixin.date_field) [[`get_date_field()`](mixins-date-based.md#django.views.generic.dates.DateMixin.get_date_field)]
* [`day`](mixins-date-based.md#django.views.generic.dates.DayMixin.day) [[`get_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_day)]
* [`day_format`](mixins-date-based.md#django.views.generic.dates.DayMixin.day_format) [[`get_day_format()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_day_format)]
* [`extra_context`](mixins-simple.md#django.views.generic.base.ContextMixin.extra_context)
* [`http_method_names`](base.md#django.views.generic.base.View.http_method_names)
* [`model`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.model)
* [`month`](mixins-date-based.md#django.views.generic.dates.MonthMixin.month) [[`get_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_month)]
* [`month_format`](mixins-date-based.md#django.views.generic.dates.MonthMixin.month_format) [[`get_month_format()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_month_format)]
* [`pk_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.pk_url_kwarg)
* [`query_pk_and_slug`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.query_pk_and_slug)
* [`queryset`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.queryset) [[`get_queryset()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_queryset)]
* [`response_class`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.response_class) [[`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)]
* [`slug_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_field) [[`get_slug_field()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_slug_field)]
* [`slug_url_kwarg`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.slug_url_kwarg)
* [`template_engine`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_engine)
* [`template_name`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.template_name) [[`get_template_names()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.get_template_names)]
* [`template_name_field`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_field)
* [`template_name_suffix`](mixins-single-object.md#django.views.generic.detail.SingleObjectTemplateResponseMixin.template_name_suffix)
* [`year`](mixins-date-based.md#django.views.generic.dates.YearMixin.year) [[`get_year()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year)]
* [`year_format`](mixins-date-based.md#django.views.generic.dates.YearMixin.year_format) [[`get_year_format()`](mixins-date-based.md#django.views.generic.dates.YearMixin.get_year_format)]

**Methods**

* [`as_view()`](base.md#django.views.generic.base.View.as_view)
* [`dispatch()`](base.md#django.views.generic.base.View.dispatch)
* `get()`
* [`get_context_data()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_context_data)
* [`get_next_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_next_day)
* [`get_next_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_next_month)
* [`get_object()`](mixins-single-object.md#django.views.generic.detail.SingleObjectMixin.get_object)
* [`get_previous_day()`](mixins-date-based.md#django.views.generic.dates.DayMixin.get_previous_day)
* [`get_previous_month()`](mixins-date-based.md#django.views.generic.dates.MonthMixin.get_previous_month)
* `head()`
* [`http_method_not_allowed()`](base.md#django.views.generic.base.View.http_method_not_allowed)
* [`render_to_response()`](mixins-simple.md#django.views.generic.base.TemplateResponseMixin.render_to_response)
* [`setup()`](base.md#django.views.generic.base.View.setup)

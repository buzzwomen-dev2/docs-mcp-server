# Built-in class-based views API

Class-based views API reference. For introductory material, see the
[Class-based views](../../topics/class-based-views/index.md) topic guide.

* [Base views](base.md)
  * [`View`](base.md#view)
  * [`TemplateView`](base.md#templateview)
  * [`RedirectView`](base.md#redirectview)
* [Generic display views](generic-display.md)
  * [`DetailView`](generic-display.md#detailview)
  * [`ListView`](generic-display.md#listview)
* [Generic editing views](generic-editing.md)
  * [`FormView`](generic-editing.md#formview)
  * [`CreateView`](generic-editing.md#createview)
  * [`UpdateView`](generic-editing.md#updateview)
  * [`DeleteView`](generic-editing.md#deleteview)
* [Generic date views](generic-date-based.md)
  * [`ArchiveIndexView`](generic-date-based.md#archiveindexview)
  * [`YearArchiveView`](generic-date-based.md#yeararchiveview)
  * [`MonthArchiveView`](generic-date-based.md#montharchiveview)
  * [`WeekArchiveView`](generic-date-based.md#weekarchiveview)
  * [`DayArchiveView`](generic-date-based.md#dayarchiveview)
  * [`TodayArchiveView`](generic-date-based.md#todayarchiveview)
  * [`DateDetailView`](generic-date-based.md#datedetailview)
* [Class-based views mixins](mixins.md)
  * [Simple mixins](mixins-simple.md)
    * [`ContextMixin`](mixins-simple.md#contextmixin)
    * [`TemplateResponseMixin`](mixins-simple.md#templateresponsemixin)
  * [Single object mixins](mixins-single-object.md)
    * [`SingleObjectMixin`](mixins-single-object.md#singleobjectmixin)
    * [`SingleObjectTemplateResponseMixin`](mixins-single-object.md#singleobjecttemplateresponsemixin)
  * [Multiple object mixins](mixins-multiple-object.md)
    * [`MultipleObjectMixin`](mixins-multiple-object.md#multipleobjectmixin)
    * [`MultipleObjectTemplateResponseMixin`](mixins-multiple-object.md#multipleobjecttemplateresponsemixin)
  * [Editing mixins](mixins-editing.md)
    * [`FormMixin`](mixins-editing.md#formmixin)
    * [`ModelFormMixin`](mixins-editing.md#modelformmixin)
    * [`ProcessFormView`](mixins-editing.md#processformview)
    * [`DeletionMixin`](mixins-editing.md#deletionmixin)
  * [Date-based mixins](mixins-date-based.md)
    * [`YearMixin`](mixins-date-based.md#yearmixin)
    * [`MonthMixin`](mixins-date-based.md#monthmixin)
    * [`DayMixin`](mixins-date-based.md#daymixin)
    * [`WeekMixin`](mixins-date-based.md#weekmixin)
    * [`DateMixin`](mixins-date-based.md#datemixin)
    * [`BaseDateListView`](mixins-date-based.md#basedatelistview)
* [Class-based generic views - flattened index](flattened-index.md)
  * [Simple generic views](flattened-index.md#simple-generic-views)
    * [`View`](flattened-index.md#view)
    * [`TemplateView`](flattened-index.md#templateview)
    * [`RedirectView`](flattened-index.md#redirectview)
  * [Detail Views](flattened-index.md#detail-views)
    * [`DetailView`](flattened-index.md#detailview)
  * [List Views](flattened-index.md#list-views)
    * [`ListView`](flattened-index.md#listview)
  * [Editing views](flattened-index.md#editing-views)
    * [`FormView`](flattened-index.md#formview)
    * [`CreateView`](flattened-index.md#createview)
    * [`UpdateView`](flattened-index.md#updateview)
    * [`DeleteView`](flattened-index.md#deleteview)
  * [Date-based views](flattened-index.md#date-based-views)
    * [`ArchiveIndexView`](flattened-index.md#archiveindexview)
    * [`YearArchiveView`](flattened-index.md#yeararchiveview)
    * [`MonthArchiveView`](flattened-index.md#montharchiveview)
    * [`WeekArchiveView`](flattened-index.md#weekarchiveview)
    * [`DayArchiveView`](flattened-index.md#dayarchiveview)
    * [`TodayArchiveView`](flattened-index.md#todayarchiveview)
    * [`DateDetailView`](flattened-index.md#datedetailview)

## Specification

Each request served by a class-based view has an independent state; therefore,
it is safe to store state variables on the instance (i.e., `self.foo = 3` is
a thread-safe operation).

A class-based view is deployed into a URL pattern using the
[`as_view()`](base.md#django.views.generic.base.View.as_view) classmethod:

```default
urlpatterns = [
    path("view/", MyView.as_view(size=42)),
]
```

Arguments passed into [`as_view()`](base.md#django.views.generic.base.View.as_view) will
be assigned onto the instance that is used to service a request. Using the
previous example, this means that every request on `MyView` is able to use
`self.size`. Arguments must correspond to attributes that already exist on
the class (return `True` on a `hasattr` check).

## Base vs Generic views

Base class-based views can be thought of as *parent* views, which can be
used by themselves or inherited from. They may not provide all the
capabilities required for projects, in which case there are Mixins which
extend what base views can do.

Django’s generic views are built off of those base views, and were developed
as a shortcut for common usage patterns such as displaying the details of an
object. They take certain common idioms and patterns found in view
development and abstract them so that you can quickly write common views of
data without having to repeat yourself.

Most generic views require the `queryset` key, which is a `QuerySet`
instance; see [Making queries](../../topics/db/queries.md) for more information about `QuerySet`
objects.

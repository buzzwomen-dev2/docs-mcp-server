# GeoDjango’s admin site

## `GISModelAdmin`

### *class* GISModelAdmin

#### gis_widget

The widget class to be used for
[`GeometryField`](model-api.md#django.contrib.gis.db.models.GeometryField). Defaults to
[`OSMWidget`](forms-api.md#django.contrib.gis.forms.widgets.OSMWidget).

#### gis_widget_kwargs

The keyword arguments that would be passed to the [`gis_widget`](#django.contrib.gis.admin.GISModelAdmin.gis_widget).
Defaults to an empty dictionary.

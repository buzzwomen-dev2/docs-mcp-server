# GeoDjango Forms API

GeoDjango provides some specialized form fields and widgets in order to
visually display and edit geolocalized data on a map. By default, they use
[OpenLayers](https://openlayers.org/)-powered maps, with a base WMS layer provided by [NASA](https://www.earthdata.nasa.gov/).

## Field arguments

In addition to the regular [form field arguments](../../forms/fields.md#core-field-arguments),
GeoDjango form fields take the following optional arguments.

### `srid`

#### Field.srid

This is the SRID code that the field value should be transformed to. For
example, if the map widget SRID is different from the SRID more generally
used by your application or database, the field will automatically convert
input values into that SRID.

### `geom_type`

#### Field.geom_type

You generally shouldn’t have to set or change that attribute which should
be set up depending on the field class. It matches the OpenGIS standard
geometry name.

## Form field classes

### `GeometryField`

### *class* GeometryField

### `PointField`

### *class* PointField

### `LineStringField`

### *class* LineStringField

### `PolygonField`

### *class* PolygonField

### `MultiPointField`

### *class* MultiPointField

### `MultiLineStringField`

### *class* MultiLineStringField

### `MultiPolygonField`

### *class* MultiPolygonField

### `GeometryCollectionField`

### *class* GeometryCollectionField

## Form widgets

GeoDjango form widgets allow you to display and edit geographic data on a
visual map.
Note that none of the currently available widgets supports 3D geometries, hence
geometry fields will fallback using a `Textarea` widget for such data.

### Widget attributes

GeoDjango widgets are template-based, so their attributes are mostly different
from other Django widget attributes.

#### BaseGeometryWidget.base_layer

#### Versionadded

A string that specifies the identifier for the default base map layer to be
used by the corresponding JavaScript map widget. It is passed as part of
the widget options when rendering, allowing the `MapWidget` to determine
which map tile provider or base layer to initialize (default is `None`).

#### BaseGeometryWidget.geom_type

The OpenGIS geometry type, generally set by the form field.

#### BaseGeometryWidget.map_srid

SRID code used by the map (default is 4326).

#### BaseGeometryWidget.display_raw

Boolean value specifying if a textarea input showing the serialized
representation of the current geometry is visible, mainly for debugging
purposes (default is `False`).

#### BaseGeometryWidget.supports_3d

Indicates if the widget supports edition of 3D data (default is `False`).

#### BaseGeometryWidget.template_name

The template used to render the map widget.

You can pass widget attributes in the same manner that for any other Django
widget. For example:

```default
from django.contrib.gis import forms


class MyGeoForm(forms.Form):
    point = forms.PointField(widget=forms.OSMWidget(attrs={"display_raw": True}))
```

### Widget classes

`BaseGeometryWidget`

### *class* BaseGeometryWidget

This is an abstract base widget containing the logic needed by subclasses.
You cannot directly use this widget for a geometry field.
Note that the rendering of GeoDjango widgets is based on a base layer name,
identified by the [`base_layer`](#django.contrib.gis.forms.widgets.BaseGeometryWidget.base_layer) class attribute.

`OpenLayersWidget`

### *class* OpenLayersWidget

This is the default widget used by all GeoDjango form fields. Attributes
are:

#### base_layer

#### Versionadded

`nasaWorldview`

#### template_name

`gis/openlayers.html`.

#### map_srid

`3857`

`OpenLayersWidget` and [`OSMWidget`](#django.contrib.gis.forms.widgets.OSMWidget) include the `ol.js` and
`ol.css` files hosted on the `cdn.jsdelivr.net` content-delivery
network. These files can be overridden by subclassing the widget and
setting the `js` and `css` properties of the inner `Media` class (see
[Assets as a static definition](../../../topics/forms/media.md#assets-as-a-static-definition)).

`OSMWidget`

### *class* OSMWidget

This widget specialized [`OpenLayersWidget`](#django.contrib.gis.forms.widgets.OpenLayersWidget) and uses an OpenStreetMap
base layer to display geographic objects on. Attributes are:

#### base_layer

#### Versionadded

`osm`

#### default_lat

#### default_lon

The default center latitude and longitude are `47` and `5`,
respectively, which is a location in eastern France.

#### default_zoom

The default map zoom is `12`.

The [`OpenLayersWidget`](#django.contrib.gis.forms.widgets.OpenLayersWidget) note about using external assets also applies
here. See also this [FAQ answer](https://help.openstreetmap.org/questions/10920/how-to-embed-a-map-in-my-https-site) about `https` access to map tiles.

#### Versionchanged
The `OSMWidget` no longer uses a custom template. Consequently, the
`gis/openlayers-osm.html` template was removed.

<a id="geometry-widgets-customization"></a>

### Customizing the base layer used in OpenLayers-based widgets

#### Versionadded

To customize the base layer displayed in OpenLayers-based geometry widgets,
define a new layer builder in a custom JavaScript file. For example:

```javascript
 MapWidget.layerBuilder.custom_layer_name = function () {
     // Return an OpenLayers layer instance.
     return new ol.layer.Tile({source: new ol.source.<ChosenSource>()});
 };
```

Then, subclass a standard geometry widget and set the `base_layer`:

```default
from django.contrib.gis.forms.widgets import OpenLayersWidget


class YourCustomWidget(OpenLayersWidget):
    base_layer = "custom_layer_name"

    class Media:
        js = ["path-to-file.js"]
```

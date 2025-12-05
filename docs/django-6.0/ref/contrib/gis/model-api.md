# GeoDjango Model API

This document explores the details of the GeoDjango Model API. Throughout this
section, we’ll be using the following geographic model of a [ZIP code](https://en.wikipedia.org/wiki/ZIP_code) and
of a [Digital Elevation Model](https://en.wikipedia.org/wiki/Digital_elevation_model) as our examples:

```default
from django.contrib.gis.db import models


class Zipcode(models.Model):
    code = models.CharField(max_length=5)
    poly = models.PolygonField()


class Elevation(models.Model):
    name = models.CharField(max_length=100)
    rast = models.RasterField()
```

## Spatial Field Types

Spatial fields consist of a series of geometry field types and one raster field
type. Each of the geometry field types correspond to the OpenGIS Simple
Features specification <sup>[1](#fnogc)</sup>. There is no such standard for raster data.

### `GeometryField`

### *class* GeometryField

The base class for geometry fields.

### `PointField`

### *class* PointField

Stores a [`Point`](geos.md#django.contrib.gis.geos.Point).

### `LineStringField`

### *class* LineStringField

Stores a [`LineString`](geos.md#django.contrib.gis.geos.LineString).

### `PolygonField`

### *class* PolygonField

Stores a [`Polygon`](geos.md#django.contrib.gis.geos.Polygon).

### `MultiPointField`

### *class* MultiPointField

Stores a [`MultiPoint`](geos.md#django.contrib.gis.geos.MultiPoint).

### `MultiLineStringField`

### *class* MultiLineStringField

Stores a [`MultiLineString`](geos.md#django.contrib.gis.geos.MultiLineString).

### `MultiPolygonField`

### *class* MultiPolygonField

Stores a [`MultiPolygon`](geos.md#django.contrib.gis.geos.MultiPolygon).

### `GeometryCollectionField`

### *class* GeometryCollectionField

Stores a [`GeometryCollection`](geos.md#django.contrib.gis.geos.GeometryCollection).

### `RasterField`

### *class* RasterField

Stores a [`GDALRaster`](gdal.md#django.contrib.gis.gdal.GDALRaster).

`RasterField` is currently only implemented for the PostGIS backend.

## Spatial Field Options

In addition to the regular [Field options](../../models/fields.md#common-model-field-options) available for
Django model fields, spatial fields have the following additional options.
All are optional.

### `srid`

#### BaseSpatialField.srid

Sets the SRID <sup>[2](#fnogcsrid)</sup> (Spatial Reference System Identity) of the geometry
field to the given value. Defaults to 4326 (also known as [WGS84](https://en.wikipedia.org/wiki/WGS84), units are
in degrees of longitude and latitude).

<a id="selecting-an-srid"></a>

#### Selecting an SRID

Choosing an appropriate SRID for your model is an important decision that the
developer should consider carefully. The SRID is an integer specifier that
corresponds to the projection system that will be used to interpret the data in
the spatial database. <sup>[3](#fnsrid)</sup>  Projection systems give the context to the
coordinates that specify a location. Although the details of [geodesy](https://en.wikipedia.org/wiki/Geodesy) are
beyond the scope of this documentation, the general problem is that the earth
is spherical and representations of the earth (e.g., paper maps, web maps) are
not.

Most people are familiar with using latitude and longitude to reference a
location on the earth’s surface. However, latitude and longitude are angles,
not distances. In other words, while the shortest path between two points on a
flat surface is a straight line, the shortest path between two points on a
curved surface (such as the earth) is an *arc* of a [great circle](https://en.wikipedia.org/wiki/Great_circle).
<sup>[4](#fnthematic)</sup>

Thus, additional computation is required to obtain distances in planar units
(e.g., kilometers and miles). Using a geographic coordinate system may
introduce complications for the developer later on. For example, SpatiaLite
does not have the capability to perform distance calculations between
geometries using geographic coordinate systems, e.g. constructing a query to
find all points within 5 miles of a county boundary stored as WGS84. <sup>[5](#fndist)</sup>

Portions of the earth’s surface may projected onto a two-dimensional, or
Cartesian, plane. Projected coordinate systems are especially convenient for
region-specific applications, e.g., if you know that your database will only
cover geometries in [North Kansas](https://spatialreference.org/ref/epsg/2796/), then you may consider using projection
system specific to that region. Moreover, projected coordinate systems are
defined in Cartesian units (such as meters or feet), easing distance
calculations.

#### NOTE
If you wish to perform arbitrary distance queries using non-point
geometries in WGS84 in PostGIS and you want decent performance, enable the
[`GeometryField.geography`](#django.contrib.gis.db.models.GeometryField.geography) keyword so that [geography database
type](#geography-type) is used instead.

Additional Resources:

* [spatialreference.org](https://spatialreference.org/): A Django-powered database of spatial reference
  systems.
* [The State Plane Coordinate System](https://web.archive.org/web/20080302095452/http://welcome.warnercnr.colostate.edu/class_info/nr502/lg3/datums_coordinates/spcs.html): A website covering the various
  projection systems used in the United States. Much of the U.S. spatial
  data encountered will be in one of these coordinate systems rather than
  in a geographic coordinate system such as WGS84.

### `spatial_index`

#### BaseSpatialField.spatial_index

Defaults to `True`. Creates a spatial index for the given geometry
field.

#### NOTE
This is different from the `db_index` field option because spatial
indexes are created in a different manner than regular database
indexes. Specifically, spatial indexes are typically created using
a variant of the R-Tree, while regular database indexes typically
use B-Trees.

<a id="geometry-field-options"></a>

## Geometry Field Options

There are additional options available for Geometry fields. All the following
options are optional.

### `dim`

#### GeometryField.dim

This option may be used for customizing the coordinate dimension of the
geometry field. By default, it is set to 2, for representing two-dimensional
geometries. For spatial backends that support it, it may be set to 3 for
three-dimensional support.

#### NOTE
At this time 3D support is limited to the PostGIS and SpatiaLite backends.

### `geography`

#### GeometryField.geography

If set to `True`, this option will create a database column of
type geography, rather than geometry. Please refer to the
[geography type](#geography-type) section below for more
details.

#### NOTE
Geography support is limited to PostGIS and will force the SRID to be 4326.

<a id="geography-type"></a>

#### Geography Type

The geography type provides native support for spatial features represented
with geographic coordinates (e.g., WGS84 longitude/latitude). <sup>[6](#fngeography)</sup>
Unlike the plane used by a geometry type, the geography type uses a spherical
representation of its data. Distance and measurement operations
performed on a geography column automatically employ great circle arc
calculations and return linear units. In other words, when `ST_Distance`
is called on two geographies, a value in meters is returned (as opposed
to degrees if called on a geometry column in WGS84).

Because geography calculations involve more mathematics, only a subset of the
PostGIS spatial lookups are available for the geography type. Practically,
this means that in addition to the [distance lookups](geoquerysets.md#distance-lookups)
only the following additional [spatial lookups](geoquerysets.md#spatial-lookups) are
available for geography columns:

* [`bboverlaps`](geoquerysets.md#std-fieldlookup-bboverlaps)
* [`coveredby`](geoquerysets.md#std-fieldlookup-coveredby)
* [`covers`](geoquerysets.md#std-fieldlookup-covers)
* [`intersects`](geoquerysets.md#std-fieldlookup-intersects)

If you need to use a spatial lookup or aggregate that doesn’t support the
geography type as input, you can use the
[`Cast`](../../models/database-functions.md#django.db.models.functions.Cast) database function to convert the
geography column to a geometry type in the query:

```default
from django.contrib.gis.db.models import PointField
from django.db.models.functions import Cast

Zipcode.objects.annotate(geom=Cast("geography_field", PointField())).filter(
    geom__within=poly
)
```

For more information, the PostGIS documentation contains a helpful section on
determining [when to use geography data type over geometry data type](https://postgis.net/docs/using_postgis_dbmanagement.html#PostGIS_GeographyVSGeometry).

### Footnotes

* <a id='fnogc'>**[1]**</a> OpenGIS Consortium, Inc., [Simple Feature Specification For SQL](https://www.ogc.org/standard/sfs/).
* <a id='fnogcsrid'>**[2]**</a> *See id.* at Ch. 2.3.8, p. 39 (Geometry Values and Spatial Reference Systems).
* <a id='fnsrid'>**[3]**</a> Typically, SRID integer corresponds to an EPSG ([European Petroleum Survey Group](https://epsg.org/)) identifier. However, it may also be associated with custom projections defined in spatial database’s spatial reference systems table.
* <a id='fnthematic'>**[4]**</a> Terry A. Slocum, Robert B. McMaster, Fritz C. Kessler, & Hugh H. Howard, *Thematic Cartography and Geographic Visualization* (Prentice Hall, 2nd edition), at Ch. 7.1.3.
* <a id='fndist'>**[5]**</a> This limitation does not apply to PostGIS.
* <a id='fngeography'>**[6]**</a> Please refer to the [PostGIS Geography Type](https://postgis.net/docs/using_postgis_dbmanagement.html#PostGIS_Geography) documentation for more details.

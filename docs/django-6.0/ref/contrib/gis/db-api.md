# GeoDjango Database API

<a id="spatial-backends"></a>

## Spatial Backends

GeoDjango currently provides the following spatial database backends:

* `django.contrib.gis.db.backends.postgis`
* `django.contrib.gis.db.backends.mysql`
* `django.contrib.gis.db.backends.oracle`
* `django.contrib.gis.db.backends.spatialite`

<a id="mysql-spatial-limitations"></a>

### MySQL Spatial Limitations

Django supports spatial functions operating on real geometries available in
modern MySQL versions. However, the spatial functions are not as rich as other
backends like PostGIS.

### Raster Support

`RasterField` is currently only implemented for the PostGIS backend. Spatial
lookups are available for raster fields, but spatial database functions and
aggregates aren’t implemented for raster fields.

## Creating and Saving Models with Geometry Fields

Here is an example of how to create a geometry object (assuming the `Zipcode`
model):

```pycon
>>> from zipcode.models import Zipcode
>>> z = Zipcode(code=77096, poly="POLYGON(( 10 10, 10 20, 20 20, 20 15, 10 10))")
>>> z.save()
```

[`GEOSGeometry`](geos.md#django.contrib.gis.geos.GEOSGeometry) objects may also be used to save
geometric models:

```pycon
>>> from django.contrib.gis.geos import GEOSGeometry
>>> poly = GEOSGeometry("POLYGON(( 10 10, 10 20, 20 20, 20 15, 10 10))")
>>> z = Zipcode(code=77096, poly=poly)
>>> z.save()
```

Moreover, if the `GEOSGeometry` is in a different coordinate system (has a
different SRID value) than that of the field, then it will be implicitly
transformed into the SRID of the model’s field, using the spatial database’s
transform procedure:

```pycon
>>> poly_3084 = GEOSGeometry(
...     "POLYGON(( 10 10, 10 20, 20 20, 20 15, 10 10))", srid=3084
... )  # SRID 3084 is 'NAD83(HARN) / Texas Centric Lambert Conformal'
>>> z = Zipcode(code=78212, poly=poly_3084)
>>> z.save()
>>> from django.db import connection
>>> print(
...     connection.queries[-1]["sql"]
... )  # printing the last SQL statement executed (requires DEBUG=True)
INSERT INTO "geoapp_zipcode" ("code", "poly") VALUES (78212, ST_Transform(ST_GeomFromWKB('\\001 ... ', 3084), 4326))
```

Thus, geometry parameters may be passed in using the `GEOSGeometry` object,
WKT (Well Known Text <sup>[1](#fnwkt)</sup>), HEXEWKB (PostGIS specific – a WKB geometry in
hexadecimal <sup>[2](#fnewkb)</sup>), and GeoJSON (see [**RFC 7946**](https://datatracker.ietf.org/doc/html/rfc7946.html)). Essentially, if the
input is not a `GEOSGeometry` object, the geometry field will attempt to
create a `GEOSGeometry` instance from the input.

For more information creating [`GEOSGeometry`](geos.md#django.contrib.gis.geos.GEOSGeometry)
objects, refer to the [GEOS tutorial](geos.md#geos-tutorial).

<a id="creating-and-saving-raster-models"></a>

## Creating and Saving Models with Raster Fields

When creating raster models, the raster field will implicitly convert the input
into a [`GDALRaster`](gdal.md#django.contrib.gis.gdal.GDALRaster) using lazy-evaluation.
The raster field will therefore accept any input that is accepted by the
[`GDALRaster`](gdal.md#django.contrib.gis.gdal.GDALRaster) constructor.

Here is an example of how to create a raster object from a raster file
`volcano.tif` (assuming the `Elevation` model):

```pycon
>>> from elevation.models import Elevation
>>> dem = Elevation(name="Volcano", rast="/path/to/raster/volcano.tif")
>>> dem.save()
```

[`GDALRaster`](gdal.md#django.contrib.gis.gdal.GDALRaster) objects may also be used to save
raster models:

```pycon
>>> from django.contrib.gis.gdal import GDALRaster
>>> rast = GDALRaster(
...     {
...         "width": 10,
...         "height": 10,
...         "name": "Canyon",
...         "srid": 4326,
...         "scale": [0.1, -0.1],
...         "bands": [{"data": range(100)}],
...     }
... )
>>> dem = Elevation(name="Canyon", rast=rast)
>>> dem.save()
```

Note that this equivalent to:

```pycon
>>> dem = Elevation.objects.create(
...     name="Canyon",
...     rast={
...         "width": 10,
...         "height": 10,
...         "name": "Canyon",
...         "srid": 4326,
...         "scale": [0.1, -0.1],
...         "bands": [{"data": range(100)}],
...     },
... )
```

<a id="spatial-lookups-intro"></a>

## Spatial Lookups

GeoDjango’s lookup types may be used with any manager method like
`filter()`, `exclude()`, etc. However, the lookup types unique to
GeoDjango are only available on spatial fields.

Filters on ‘normal’ fields (e.g. [`CharField`](../../models/fields.md#django.db.models.CharField))
may be chained with those on geographic fields. Geographic lookups accept
geometry and raster input on both sides and input types can be mixed freely.

The general structure of geographic lookups is described below. A complete
reference can be found in the [spatial lookup reference](geoquerysets.md#spatial-lookups).

### Geometry Lookups

Geographic queries with geometries take the following general form (assuming
the `Zipcode` model used in the [GeoDjango Model API](model-api.md)):

```text
>>> qs = Zipcode.objects.filter(<field>__<lookup_type>=<parameter>)
>>> qs = Zipcode.objects.exclude(...)
```

For example:

```pycon
>>> qs = Zipcode.objects.filter(poly__contains=pnt)
>>> qs = Elevation.objects.filter(poly__contains=rst)
```

In this case, `poly` is the geographic field,
[`contains`](geoquerysets.md#std-fieldlookup-gis-contains) is the spatial lookup type, `pnt` is the
parameter (which may be a [`GEOSGeometry`](geos.md#django.contrib.gis.geos.GEOSGeometry) object
or a string of GeoJSON , WKT, or HEXEWKB), and `rst` is a
[`GDALRaster`](gdal.md#django.contrib.gis.gdal.GDALRaster) object.

<a id="spatial-lookup-raster"></a>

### Raster Lookups

The raster lookup syntax is similar to the syntax for geometries. The only
difference is that a band index can be specified as additional input. If no
band index is specified, the first band is used by default (index `0`). In
that case the syntax is identical to the syntax for geometry lookups.

To specify the band index, an additional parameter can be specified on both
sides of the lookup. On the left hand side, the double underscore syntax is
used to pass a band index. On the right hand side, a tuple of the raster and
band index can be specified.

This results in the following general form for lookups involving rasters
(assuming the `Elevation` model used in the
[GeoDjango Model API](model-api.md)):

```text
>>> qs = Elevation.objects.filter(<field>__<lookup_type>=<parameter>)
>>> qs = Elevation.objects.filter(<field>__<band_index>__<lookup_type>=<parameter>)
>>> qs = Elevation.objects.filter(<field>__<lookup_type>=(<raster_input, <band_index>)
```

For example:

```pycon
>>> qs = Elevation.objects.filter(rast__contains=geom)
>>> qs = Elevation.objects.filter(rast__contains=rst)
>>> qs = Elevation.objects.filter(rast__1__contains=geom)
>>> qs = Elevation.objects.filter(rast__contains=(rst, 1))
>>> qs = Elevation.objects.filter(rast__1__contains=(rst, 1))
```

On the left hand side of the example, `rast` is the geographic raster field
and [`contains`](geoquerysets.md#std-fieldlookup-gis-contains) is the spatial lookup type. On the right
hand side, `geom` is a geometry input and `rst` is a
[`GDALRaster`](gdal.md#django.contrib.gis.gdal.GDALRaster) object. The band index defaults to
`0` in the first two queries and is set to `1` on the others.

While all spatial lookups can be used with raster objects on both sides, not
all underlying operators natively accept raster input. For cases where the
operator expects geometry input, the raster is automatically converted to a
geometry. It’s important to keep this in mind when interpreting the lookup
results.

The type of raster support is listed for all lookups in the [compatibility
table](#spatial-lookup-compatibility). Lookups involving rasters are currently
only available for the PostGIS backend.

<a id="distance-queries"></a>

## Distance Queries

### Introduction

Distance calculations with spatial data is tricky because, unfortunately, the
Earth is not flat. Some distance queries with fields in a geographic coordinate
system may have to be expressed differently because of limitations in PostGIS.
Please see the [Selecting an SRID](model-api.md#selecting-an-srid) section for more details.

<a id="distance-lookups-intro"></a>

### Distance Lookups

*Availability*: PostGIS, MariaDB, MySQL, Oracle, SpatiaLite, PGRaster (Native)

The following distance lookups are available:

* [`distance_lt`](geoquerysets.md#std-fieldlookup-distance_lt)
* [`distance_lte`](geoquerysets.md#std-fieldlookup-distance_lte)
* [`distance_gt`](geoquerysets.md#std-fieldlookup-distance_gt)
* [`distance_gte`](geoquerysets.md#std-fieldlookup-distance_gte)
* [`dwithin`](geoquerysets.md#std-fieldlookup-dwithin) (except MariaDB and MySQL)

#### NOTE
For *measuring*, rather than querying on distances, use the
[`Distance`](functions.md#django.contrib.gis.db.models.functions.Distance) function.

Distance lookups take a tuple parameter comprising:

1. A geometry or raster to base calculations from; and
2. A number or [`Distance`](measure.md#django.contrib.gis.measure.Distance) object containing
   the distance.

If a [`Distance`](measure.md#django.contrib.gis.measure.Distance) object is used,
it may be expressed in any units (the SQL generated will use units
converted to those of the field); otherwise, numeric parameters are assumed
to be in the units of the field.

#### NOTE
In PostGIS, `ST_Distance_Sphere` does *not* limit the geometry types
geographic distance queries are performed with. <sup>[3](#fndistsphere15)</sup>
However, these queries may take a long time, as great-circle distances must
be calculated on the fly for *every* row in the query. This is because the
spatial index on traditional geometry fields cannot be used.

For much better performance on WGS84 distance queries, consider using
[geography columns](model-api.md#geography-type) in your database instead because
they are able to use their spatial index in distance queries.
You can tell GeoDjango to use a geography column by setting
`geography=True` in your field definition.

For example, let’s say we have a `SouthTexasCity` model (from the
[GeoDjango distance tests](https://github.com/django/django/blob/main/tests/gis_tests/distapp/models.py) ) on a
*projected* coordinate system valid for cities in southern Texas:

```default
from django.contrib.gis.db import models


class SouthTexasCity(models.Model):
    name = models.CharField(max_length=30)
    # A projected coordinate system (only valid for South Texas!)
    # is used, units are in meters.
    point = models.PointField(srid=32140)
```

Then distance queries may be performed as follows:

```pycon
>>> from django.contrib.gis.geos import GEOSGeometry
>>> from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
>>> from geoapp.models import SouthTexasCity
# Distances will be calculated from this point, which does not have to be projected.
>>> pnt = GEOSGeometry("POINT(-96.876369 29.905320)", srid=4326)
# If numeric parameter, units of field (meters in this case) are assumed.
>>> qs = SouthTexasCity.objects.filter(point__distance_lte=(pnt, 7000))
# Find all Cities within 7 km, > 20 miles away, and > 100 chains away (an obscure unit)
>>> qs = SouthTexasCity.objects.filter(point__distance_lte=(pnt, D(km=7)))
>>> qs = SouthTexasCity.objects.filter(point__distance_gte=(pnt, D(mi=20)))
>>> qs = SouthTexasCity.objects.filter(point__distance_gte=(pnt, D(chain=100)))
```

Raster queries work the same way by replacing the geometry field `point` with
a raster field, or the `pnt` object with a raster object, or both. To specify
the band index of a raster input on the right hand side, a 3-tuple can be
passed to the lookup as follows:

```pycon
>>> qs = SouthTexasCity.objects.filter(point__distance_gte=(rst, 2, D(km=7)))
```

Where the band with index 2 (the third band) of the raster `rst` would be
used for the lookup.

<a id="compatibility-table"></a>

## Compatibility Tables

<a id="spatial-lookup-compatibility"></a>

### Spatial Lookups

The following table provides a summary of what spatial lookups are available
for each spatial database backend. The PostGIS Raster (PGRaster) lookups are
divided into the three categories described in the [raster lookup details](#spatial-lookup-raster): native support `N`, bilateral native support `B`,
and geometry conversion support `C`.

| Lookup Type                                                              | PostGIS   | Oracle    | MariaDB      | MySQL <sup>[4](#id9)</sup>   | SpatiaLite   | PGRaster   |
|--------------------------------------------------------------------------|-----------|-----------|--------------|------------------------------|--------------|------------|
| [`bbcontains`](geoquerysets.md#std-fieldlookup-bbcontains)               | X         |           | X            | X                            | X            | N          |
| [`bboverlaps`](geoquerysets.md#std-fieldlookup-bboverlaps)               | X         |           | X            | X                            | X            | N          |
| [`contained`](geoquerysets.md#std-fieldlookup-contained)                 | X         |           | X            | X                            | X            | N          |
| [`contains`](geoquerysets.md#std-fieldlookup-gis-contains)               | X         | X         | X            | X                            | X            | B          |
| [`contains_properly`](geoquerysets.md#std-fieldlookup-contains_properly) | X         |           |              |                              |              | B          |
| [`coveredby`](geoquerysets.md#std-fieldlookup-coveredby)                 | X         | X         | X (≥ 12.0.1) | X                            | X            | B          |
| [`covers`](geoquerysets.md#std-fieldlookup-covers)                       | X         | X         |              | X                            | X            | B          |
| [`crosses`](geoquerysets.md#std-fieldlookup-crosses)                     | X         |           | X            | X                            | X            | C          |
| [`disjoint`](geoquerysets.md#std-fieldlookup-disjoint)                   | X         | X         | X            | X                            | X            | B          |
| [`distance_gt`](geoquerysets.md#std-fieldlookup-distance_gt)             | X         | X         | X            | X                            | X            | N          |
| [`distance_gte`](geoquerysets.md#std-fieldlookup-distance_gte)           | X         | X         | X            | X                            | X            | N          |
| [`distance_lt`](geoquerysets.md#std-fieldlookup-distance_lt)             | X         | X         | X            | X                            | X            | N          |
| [`distance_lte`](geoquerysets.md#std-fieldlookup-distance_lte)           | X         | X         | X            | X                            | X            | N          |
| [`dwithin`](geoquerysets.md#std-fieldlookup-dwithin)                     | X         | X         |              |                              | X            | B          |
| [`equals`](geoquerysets.md#std-fieldlookup-equals)                       | X         | X         | X            | X                            | X            | C          |
| [`exact`](geoquerysets.md#std-fieldlookup-same_as)                       | X         | X         | X            | X                            | X            | B          |
| [`geom_type`](geoquerysets.md#std-fieldlookup-geom_type)                 | X         | X (≥ 23c) | X            | X                            | X            |            |
| [`intersects`](geoquerysets.md#std-fieldlookup-intersects)               | X         | X         | X            | X                            | X            | B          |
| [`isempty`](geoquerysets.md#std-fieldlookup-isempty)                     | X         |           |              |                              | X            |            |
| [`isvalid`](geoquerysets.md#std-fieldlookup-isvalid)                     | X         | X         | X (≥ 12.0.1) | X                            | X            |            |
| [`num_dimensions`](geoquerysets.md#std-fieldlookup-num_dimensions)       | X         |           |              |                              | X            |            |
| [`overlaps`](geoquerysets.md#std-fieldlookup-overlaps)                   | X         | X         | X            | X                            | X            | B          |
| [`relate`](geoquerysets.md#std-fieldlookup-relate)                       | X         | X         | X            |                              | X            | C          |
| [`same_as`](geoquerysets.md#std-fieldlookup-same_as)                     | X         | X         | X            | X                            | X            | B          |
| [`touches`](geoquerysets.md#std-fieldlookup-touches)                     | X         | X         | X            | X                            | X            | B          |
| [`within`](geoquerysets.md#std-fieldlookup-within)                       | X         | X         | X            | X                            | X            | B          |
| [`left`](geoquerysets.md#std-fieldlookup-left)                           | X         |           |              |                              |              | C          |
| [`right`](geoquerysets.md#std-fieldlookup-right)                         | X         |           |              |                              |              | C          |
| [`overlaps_left`](geoquerysets.md#std-fieldlookup-overlaps_left)         | X         |           |              |                              |              | B          |
| [`overlaps_right`](geoquerysets.md#std-fieldlookup-overlaps_right)       | X         |           |              |                              |              | B          |
| [`overlaps_above`](geoquerysets.md#std-fieldlookup-overlaps_above)       | X         |           |              |                              |              | C          |
| [`overlaps_below`](geoquerysets.md#std-fieldlookup-overlaps_below)       | X         |           |              |                              |              | C          |
| [`strictly_above`](geoquerysets.md#std-fieldlookup-strictly_above)       | X         |           |              |                              |              | C          |
| [`strictly_below`](geoquerysets.md#std-fieldlookup-strictly_below)       | X         |           |              |                              |              | C          |

<a id="database-functions-compatibility"></a>

### Database functions

The following table provides a summary of what geography-specific database
functions are available on each spatial backend.

| Function                                                                                   | PostGIS   | Oracle    | MariaDB      | MySQL   | SpatiaLite        |
|--------------------------------------------------------------------------------------------|-----------|-----------|--------------|---------|-------------------|
| [`Area`](functions.md#django.contrib.gis.db.models.functions.Area)                         | X         | X         | X            | X       | X                 |
| [`AsGeoJSON`](functions.md#django.contrib.gis.db.models.functions.AsGeoJSON)               | X         | X         | X            | X       | X                 |
| [`AsGML`](functions.md#django.contrib.gis.db.models.functions.AsGML)                       | X         | X         |              |         | X                 |
| [`AsKML`](functions.md#django.contrib.gis.db.models.functions.AsKML)                       | X         |           |              |         | X                 |
| [`AsSVG`](functions.md#django.contrib.gis.db.models.functions.AsSVG)                       | X         |           |              |         | X                 |
| [`AsWKB`](functions.md#django.contrib.gis.db.models.functions.AsWKB)                       | X         | X         | X            | X       | X                 |
| [`AsWKT`](functions.md#django.contrib.gis.db.models.functions.AsWKT)                       | X         | X         | X            | X       | X                 |
| [`Azimuth`](functions.md#django.contrib.gis.db.models.functions.Azimuth)                   | X         |           |              |         | X (LWGEOM/RTTOPO) |
| [`BoundingCircle`](functions.md#django.contrib.gis.db.models.functions.BoundingCircle)     | X         | X         |              |         | X (≥ 5.1)         |
| [`Centroid`](functions.md#django.contrib.gis.db.models.functions.Centroid)                 | X         | X         | X            | X       | X                 |
| [`ClosestPoint`](functions.md#django.contrib.gis.db.models.functions.ClosestPoint)         | X         |           |              |         | X                 |
| [`Difference`](functions.md#django.contrib.gis.db.models.functions.Difference)             | X         | X         | X            | X       | X                 |
| [`Distance`](functions.md#django.contrib.gis.db.models.functions.Distance)                 | X         | X         | X            | X       | X                 |
| [`Envelope`](functions.md#django.contrib.gis.db.models.functions.Envelope)                 | X         | X         | X            | X       | X                 |
| [`ForcePolygonCW`](functions.md#django.contrib.gis.db.models.functions.ForcePolygonCW)     | X         |           |              |         | X                 |
| [`FromWKB`](functions.md#django.contrib.gis.db.models.functions.FromWKB)                   | X         | X         | X            | X       | X                 |
| [`FromWKT`](functions.md#django.contrib.gis.db.models.functions.FromWKT)                   | X         | X         | X            | X       | X                 |
| [`GeoHash`](functions.md#django.contrib.gis.db.models.functions.GeoHash)                   | X         |           | X (≥ 12.0.1) | X       | X (LWGEOM/RTTOPO) |
| [`GeometryDistance`](functions.md#django.contrib.gis.db.models.functions.GeometryDistance) | X         |           |              |         |                   |
| [`GeometryType`](functions.md#django.contrib.gis.db.models.functions.GeometryType)         | X         | X (≥ 23c) | X            | X       | X                 |
| [`Intersection`](functions.md#django.contrib.gis.db.models.functions.Intersection)         | X         | X         | X            | X       | X                 |
| [`IsEmpty`](functions.md#django.contrib.gis.db.models.functions.IsEmpty)                   | X         |           |              |         | X                 |
| [`IsValid`](functions.md#django.contrib.gis.db.models.functions.IsValid)                   | X         | X         | X (≥ 12.0.1) | X       | X                 |
| [`Length`](functions.md#django.contrib.gis.db.models.functions.Length)                     | X         | X         | X            | X       | X                 |
| [`LineLocatePoint`](functions.md#django.contrib.gis.db.models.functions.LineLocatePoint)   | X         |           |              |         | X                 |
| [`MakeValid`](functions.md#django.contrib.gis.db.models.functions.MakeValid)               | X         |           |              |         | X (LWGEOM/RTTOPO) |
| [`MemSize`](functions.md#django.contrib.gis.db.models.functions.MemSize)                   | X         |           |              |         |                   |
| [`NumDimensions`](functions.md#django.contrib.gis.db.models.functions.NumDimensions)       | X         |           |              |         | X                 |
| [`NumGeometries`](functions.md#django.contrib.gis.db.models.functions.NumGeometries)       | X         | X         | X            | X       | X                 |
| [`NumPoints`](functions.md#django.contrib.gis.db.models.functions.NumPoints)               | X         | X         | X            | X       | X                 |
| [`Perimeter`](functions.md#django.contrib.gis.db.models.functions.Perimeter)               | X         | X         |              |         | X                 |
| [`PointOnSurface`](functions.md#django.contrib.gis.db.models.functions.PointOnSurface)     | X         | X         | X            |         | X                 |
| [`Reverse`](functions.md#django.contrib.gis.db.models.functions.Reverse)                   | X         | X         |              |         | X                 |
| [`Rotate`](functions.md#django.contrib.gis.db.models.functions.Rotate)                     | X         |           |              |         |                   |
| [`Scale`](functions.md#django.contrib.gis.db.models.functions.Scale)                       | X         |           |              |         | X                 |
| [`SnapToGrid`](functions.md#django.contrib.gis.db.models.functions.SnapToGrid)             | X         |           |              |         | X                 |
| [`SymDifference`](functions.md#django.contrib.gis.db.models.functions.SymDifference)       | X         | X         | X            | X       | X                 |
| [`Transform`](functions.md#django.contrib.gis.db.models.functions.Transform)               | X         | X         |              |         | X                 |
| [`Translate`](functions.md#django.contrib.gis.db.models.functions.Translate)               | X         |           |              |         | X                 |
| [`Union`](functions.md#django.contrib.gis.db.models.functions.Union)                       | X         | X         | X            | X       | X                 |

### Aggregate Functions

The following table provides a summary of what GIS-specific aggregate functions
are available on each spatial backend.

| Aggregate                                                           | PostGIS   | Oracle   | MariaDB      | MySQL        | SpatiaLite   |
|---------------------------------------------------------------------|-----------|----------|--------------|--------------|--------------|
| [`Collect`](geoquerysets.md#django.contrib.gis.db.models.Collect)   | X         |          | X (≥ 12.0.1) | X (≥ 8.0.24) | X            |
| [`Extent`](geoquerysets.md#django.contrib.gis.db.models.Extent)     | X         | X        |              |              | X            |
| [`Extent3D`](geoquerysets.md#django.contrib.gis.db.models.Extent3D) | X         |          |              |              |              |
| [`MakeLine`](geoquerysets.md#django.contrib.gis.db.models.MakeLine) | X         |          |              |              | X            |
| [`Union`](geoquerysets.md#django.contrib.gis.db.models.Union)       | X         | X        |              |              | X            |

### Footnotes

* <a id='fnwkt'>**[1]**</a> *See* Open Geospatial Consortium, Inc., [OpenGIS Simple Feature Specification For SQL](https://portal.ogc.org/files/?artifact_id=829), Document 99-049 (May 5, 1999), at  Ch. 3.2.5, p. 3-11 (SQL Textual Representation of Geometry).
* <a id='fnewkb'>**[2]**</a> *See* [PostGIS EWKB, EWKT and Canonical Forms](https://postgis.net/docs/using_postgis_dbmanagement.html#EWKB_EWKT), PostGIS documentation at Ch. 4.1.2.
* <a id='fndistsphere15'>**[3]**</a> *See* [PostGIS documentation](https://postgis.net/docs/ST_DistanceSphere.html) on `ST_DistanceSphere`.
* <a id='id9'>**[4]**</a> Refer [MySQL Spatial Limitations](#mysql-spatial-limitations) section for more details.

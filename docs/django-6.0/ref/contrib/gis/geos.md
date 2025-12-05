# GEOS API

<a id="geos-overview"></a>

## Background

### What is GEOS?

[GEOS](https://libgeos.org/) stands for **Geometry Engine - Open Source**,
and is a C++ library, ported from the  [Java Topology Suite](https://sourceforge.net/projects/jts-topo-suite/). GEOS
implements the OpenGIS [Simple Features for SQL](https://www.ogc.org/standard/sfs/) spatial predicate functions
and spatial operators. GEOS, now an OSGeo project, was initially developed and
maintained by [Refractions Research](http://www.refractions.net/) of Victoria, Canada.

### Features

GeoDjango implements a high-level Python wrapper for the GEOS library, its
features include:

* A BSD-licensed interface to the GEOS geometry routines, implemented purely
  in Python using `ctypes`.
* Loosely-coupled to GeoDjango. For example, [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) objects
  may be used outside of a Django project/application. In other words,
  no need to have [`DJANGO_SETTINGS_MODULE`](../../../topics/settings.md#envvar-DJANGO_SETTINGS_MODULE) set or use a database, etc.
* Mutability: [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) objects may be modified.
* Cross-platform tested.

<a id="geos-tutorial"></a>

## Tutorial

This section contains a brief introduction and tutorial to using
[`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) objects.

### Creating a Geometry

[`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) objects may be created in a few ways. The first is
to simply instantiate the object on some spatial input – the following
are examples of creating the same geometry from WKT, HEX, WKB, and GeoJSON:

```pycon
>>> from django.contrib.gis.geos import GEOSGeometry
>>> pnt = GEOSGeometry("POINT(5 23)")  # WKT
>>> pnt = GEOSGeometry("010100000000000000000014400000000000003740")  # HEX
>>> pnt = GEOSGeometry(
...     memoryview(
...         b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x007@"
...     )
... )  # WKB
>>> pnt = GEOSGeometry(
...     '{ "type": "Point", "coordinates": [ 5.000000, 23.000000 ] }'
... )  # GeoJSON
```

Another option is to use the constructor for the specific geometry type
that you wish to create. For example, a [`Point`](#django.contrib.gis.geos.Point) object may be
created by passing in the X and Y coordinates into its constructor:

```pycon
>>> from django.contrib.gis.geos import Point
>>> pnt = Point(5, 23)
```

All these constructors take the keyword argument `srid`. For example:

```pycon
>>> from django.contrib.gis.geos import GEOSGeometry, LineString, Point
>>> print(GEOSGeometry("POINT (0 0)", srid=4326))
SRID=4326;POINT (0 0)
>>> print(LineString((0, 0), (1, 1), srid=4326))
SRID=4326;LINESTRING (0 0, 1 1)
>>> print(Point(0, 0, srid=32140))
SRID=32140;POINT (0 0)
```

Finally, there is the [`fromfile()`](#django.contrib.gis.geos.fromfile) factory method which returns a
[`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) object from a file:

```pycon
>>> from django.contrib.gis.geos import fromfile
>>> pnt = fromfile("/path/to/pnt.wkt")
>>> pnt = fromfile(open("/path/to/pnt.wkt"))
```

<a id="geos-exceptions-in-logfile"></a>

### Geometries are Pythonic

[`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) objects are ‘Pythonic’, in other words components may
be accessed, modified, and iterated over using standard Python conventions.
For example, you can iterate over the coordinates in a [`Point`](#django.contrib.gis.geos.Point):

```pycon
>>> pnt = Point(5, 23)
>>> [coord for coord in pnt]
[5.0, 23.0]
```

With any geometry object, the [`GEOSGeometry.coords`](#django.contrib.gis.geos.GEOSGeometry.coords) property
may be used to get the geometry coordinates as a Python tuple:

```pycon
>>> pnt.coords
(5.0, 23.0)
```

You can get/set geometry components using standard Python indexing
techniques. However, what is returned depends on the geometry type
of the object. For example, indexing on a [`LineString`](#django.contrib.gis.geos.LineString)
returns a coordinate tuple:

```pycon
>>> from django.contrib.gis.geos import LineString
>>> line = LineString((0, 0), (0, 50), (50, 50), (50, 0), (0, 0))
>>> line[0]
(0.0, 0.0)
>>> line[-2]
(50.0, 0.0)
```

Whereas indexing on a [`Polygon`](#django.contrib.gis.geos.Polygon) will return the ring
(a [`LinearRing`](#django.contrib.gis.geos.LinearRing) object) corresponding to the index:

```pycon
>>> from django.contrib.gis.geos import Polygon
>>> poly = Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0)))
>>> poly[0]
<LinearRing object at 0x1044395b0>
>>> poly[0][-2]  # second-to-last coordinate of external ring
(50.0, 0.0)
```

In addition, coordinates/components of the geometry may added or modified,
just like a Python list:

```pycon
>>> line[0] = (1.0, 1.0)
>>> line.pop()
(0.0, 0.0)
>>> line.append((1.0, 1.0))
>>> line.coords
((1.0, 1.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (1.0, 1.0))
```

Geometries support set-like operators:

```pycon
>>> from django.contrib.gis.geos import LineString
>>> ls1 = LineString((0, 0), (2, 2))
>>> ls2 = LineString((1, 1), (3, 3))
>>> print(ls1 | ls2)  # equivalent to `ls1.union(ls2)`
MULTILINESTRING ((0 0, 1 1), (1 1, 2 2), (2 2, 3 3))
>>> print(ls1 & ls2)  # equivalent to `ls1.intersection(ls2)`
LINESTRING (1 1, 2 2)
>>> print(ls1 - ls2)  # equivalent to `ls1.difference(ls2)`
LINESTRING(0 0, 1 1)
>>> print(ls1 ^ ls2)  # equivalent to `ls1.sym_difference(ls2)`
MULTILINESTRING ((0 0, 1 1), (2 2, 3 3))
```

## Geometry Objects

### `GEOSGeometry`

### *class* GEOSGeometry(geo_input, srid=None)

* **Parameters:**
  * **geo_input** – Geometry input value (string or [`memoryview`](https://docs.python.org/3/library/stdtypes.html#memoryview))
  * **srid** ([*int*](https://docs.python.org/3/library/functions.html#int)) – spatial reference identifier

This is the base class for all GEOS geometry objects. It initializes on the
given `geo_input` argument, and then assumes the proper geometry subclass
(e.g., `GEOSGeometry('POINT(1 1)')` will create a [`Point`](#django.contrib.gis.geos.Point) object).

The `srid` parameter, if given, is set as the SRID of the created geometry if
`geo_input` doesn’t have an SRID. If different SRIDs are provided through the
`geo_input` and `srid` parameters, `ValueError` is raised:

```pycon
>>> from django.contrib.gis.geos import GEOSGeometry
>>> GEOSGeometry("POINT EMPTY", srid=4326).ewkt
'SRID=4326;POINT EMPTY'
>>> GEOSGeometry("SRID=4326;POINT EMPTY", srid=4326).ewkt
'SRID=4326;POINT EMPTY'
>>> GEOSGeometry("SRID=1;POINT EMPTY", srid=4326)
Traceback (most recent call last):
...
ValueError: Input geometry already has SRID: 1.
```

The following input formats, along with their corresponding Python types,
are accepted:

| Format                                                            | Input Type   |
|-------------------------------------------------------------------|--------------|
| WKT / EWKT                                                        | `str`        |
| HEX / HEXEWKB                                                     | `str`        |
| WKB / EWKB                                                        | `memoryview` |
| [**GeoJSON**](https://datatracker.ietf.org/doc/html/rfc7946.html) | `str`        |

For the GeoJSON format, the SRID is set based on the `crs` member. If `crs`
isn’t provided, the SRID defaults to 4326.

#### *classmethod* GEOSGeometry.from_gml(gml_string)

Constructs a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) from the given GML string.

#### Properties

#### GEOSGeometry.coords

Returns the coordinates of the geometry as a tuple.

#### GEOSGeometry.dims

Returns the dimension of the geometry:

* `0` for [`Point`](#django.contrib.gis.geos.Point)s and [`MultiPoint`](#django.contrib.gis.geos.MultiPoint)s
* `1` for [`LineString`](#django.contrib.gis.geos.LineString)s and [`MultiLineString`](#django.contrib.gis.geos.MultiLineString)s
* `2` for [`Polygon`](#django.contrib.gis.geos.Polygon)s and [`MultiPolygon`](#django.contrib.gis.geos.MultiPolygon)s
* `-1` for empty [`GeometryCollection`](#django.contrib.gis.geos.GeometryCollection)s
* the maximum dimension of its elements for non-empty
  [`GeometryCollection`](#django.contrib.gis.geos.GeometryCollection)s

#### GEOSGeometry.empty

Returns whether or not the set of points in the geometry is empty.

#### GEOSGeometry.geom_type

Returns a string corresponding to the type of geometry. For example:

```pycon
>>> pnt = GEOSGeometry("POINT(5 23)")
>>> pnt.geom_type
'Point'
```

#### GEOSGeometry.geom_typeid

Returns the GEOS geometry type identification number. The following table
shows the value for each geometry type:

| Geometry                                                            |   ID |
|---------------------------------------------------------------------|------|
| [`Point`](#django.contrib.gis.geos.Point)                           |    0 |
| [`LineString`](#django.contrib.gis.geos.LineString)                 |    1 |
| [`LinearRing`](#django.contrib.gis.geos.LinearRing)                 |    2 |
| [`Polygon`](#django.contrib.gis.geos.Polygon)                       |    3 |
| [`MultiPoint`](#django.contrib.gis.geos.MultiPoint)                 |    4 |
| [`MultiLineString`](#django.contrib.gis.geos.MultiLineString)       |    5 |
| [`MultiPolygon`](#django.contrib.gis.geos.MultiPolygon)             |    6 |
| [`GeometryCollection`](#django.contrib.gis.geos.GeometryCollection) |    7 |

#### GEOSGeometry.num_coords

Returns the number of coordinates in the geometry.

#### GEOSGeometry.num_geom

Returns the number of geometries in this geometry. In other words, will
return 1 on anything but geometry collections.

#### GEOSGeometry.hasz

Returns a boolean indicating whether the geometry has the Z dimension.

#### GEOSGeometry.hasm

#### Versionadded

Returns a boolean indicating whether the geometry has the M dimension.
Requires GEOS 3.12.

#### GEOSGeometry.ring

Returns a boolean indicating whether the geometry is a `LinearRing`.

#### GEOSGeometry.simple

Returns a boolean indicating whether the geometry is ‘simple’. A geometry
is simple if and only if it does not intersect itself (except at boundary
points). For example, a [`LineString`](#django.contrib.gis.geos.LineString) object is not simple if it
intersects itself. Thus, [`LinearRing`](#django.contrib.gis.geos.LinearRing) and [`Polygon`](#django.contrib.gis.geos.Polygon) objects
are always simple because they cannot intersect themselves, by definition.

#### GEOSGeometry.valid

Returns a boolean indicating whether the geometry is valid.

#### GEOSGeometry.valid_reason

Returns a string describing the reason why a geometry is invalid.

#### GEOSGeometry.srid

Property that may be used to retrieve or set the SRID associated with the
geometry. For example:

```pycon
>>> pnt = Point(5, 23)
>>> print(pnt.srid)
None
>>> pnt.srid = 4326
>>> pnt.srid
4326
```

#### Output Properties

The properties in this section export the [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) object into
a different. This output may be in the form of a string, buffer, or even
another object.

#### GEOSGeometry.ewkt

Returns the “extended” Well-Known Text of the geometry. This representation
is specific to PostGIS and is a superset of the OGC WKT standard. <sup>[1](#fnogc)</sup>
Essentially the SRID is prepended to the WKT representation, for example
`SRID=4326;POINT(5 23)`.

#### NOTE
The output from this property does not include the 3dm, 3dz, and 4d
information that PostGIS supports in its EWKT representations.

#### GEOSGeometry.hex

Returns the WKB of this Geometry in hexadecimal form. Please note
that the SRID value is not included in this representation
because it is not a part of the OGC specification (use the
[`GEOSGeometry.hexewkb`](#django.contrib.gis.geos.GEOSGeometry.hexewkb) property instead).

#### GEOSGeometry.hexewkb

Returns the EWKB of this Geometry in hexadecimal form. This is an
extension of the WKB specification that includes the SRID value
that are a part of this geometry.

#### GEOSGeometry.json

Returns the GeoJSON representation of the geometry. Note that the result is
not a complete GeoJSON structure but only the `geometry` key content of a
GeoJSON structure. See also [GeoJSON Serializer](serializers.md).

#### GEOSGeometry.geojson

Alias for [`GEOSGeometry.json`](#django.contrib.gis.geos.GEOSGeometry.json).

#### GEOSGeometry.kml

Returns a [KML](https://developers.google.com/kml/documentation/) (Keyhole Markup Language) representation of the
geometry. This should only be used for geometries with an SRID of
4326 (WGS84), but this restriction is not enforced.

#### GEOSGeometry.ogr

Returns an [`OGRGeometry`](gdal.md#django.contrib.gis.gdal.OGRGeometry) object
corresponding to the GEOS geometry.

<a id="wkb"></a>

#### GEOSGeometry.wkb

Returns the WKB (Well-Known Binary) representation of this Geometry
as a Python buffer. SRID value is not included, use the
[`GEOSGeometry.ewkb`](#django.contrib.gis.geos.GEOSGeometry.ewkb) property instead.

<a id="ewkb"></a>

#### GEOSGeometry.ewkb

Return the EWKB representation of this Geometry as a Python buffer.
This is an extension of the WKB specification that includes any SRID
value that are a part of this geometry.

#### GEOSGeometry.wkt

Returns the Well-Known Text of the geometry (an OGC standard).

#### Spatial Predicate Methods

All of the following spatial predicate methods take another
[`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) instance (`other`) as a parameter, and
return a boolean.

#### GEOSGeometry.contains(other)

Returns `True` if [`other.within(this)`](#django.contrib.gis.geos.GEOSGeometry.within)
returns `True`.

#### GEOSGeometry.covers(other)

Returns `True` if this geometry covers the specified geometry.

The `covers` predicate has the following equivalent definitions:

* Every point of the other geometry is a point of this geometry.
* The [DE-9IM](https://en.wikipedia.org/wiki/DE-9IM) Intersection Matrix for the two geometries is
  `T*****FF*`, `*T****FF*`, `***T**FF*`, or `****T*FF*`.

If either geometry is empty, returns `False`.

This predicate is similar to [`GEOSGeometry.contains()`](#django.contrib.gis.geos.GEOSGeometry.contains), but is more
inclusive (i.e. returns `True` for more cases). In particular, unlike
[`contains()`](#django.contrib.gis.geos.GEOSGeometry.contains) it does not distinguish between points in
the boundary and in the interior of geometries. For most situations,
`covers()` should be preferred to [`contains()`](#django.contrib.gis.geos.GEOSGeometry.contains). As an
added benefit, `covers()` is more amenable to optimization and hence
should outperform [`contains()`](#django.contrib.gis.geos.GEOSGeometry.contains).

#### GEOSGeometry.crosses(other)

Returns `True` if the DE-9IM intersection matrix for the two Geometries
is `T*T******` (for a point and a curve,a point and an area or a line
and an area) `0********` (for two curves).

#### GEOSGeometry.disjoint(other)

Returns `True` if the DE-9IM intersection matrix for the two geometries
is `FF*FF****`.

#### GEOSGeometry.equals(other)

Returns `True` if the DE-9IM intersection matrix for the two geometries
is `T*F**FFF*`.

#### GEOSGeometry.equals_exact(other, tolerance=0)

Returns true if the two geometries are exactly equal, up to a
specified tolerance. The `tolerance` value should be a floating
point number representing the error tolerance in the comparison, e.g.,
`poly1.equals_exact(poly2, 0.001)` will compare equality to within
one thousandth of a unit.

#### GEOSGeometry.equals_identical(other)

Returns `True` if the two geometries are point-wise equivalent by
checking that the structure, ordering, and values of all vertices are
identical in all dimensions. `NaN` values are considered to be equal to
other `NaN` values. Requires GEOS 3.12.

#### GEOSGeometry.intersects(other)

Returns `True` if [`GEOSGeometry.disjoint()`](#django.contrib.gis.geos.GEOSGeometry.disjoint) is `False`.

#### GEOSGeometry.overlaps(other)

Returns true if the DE-9IM intersection matrix for the two geometries
is `T*T***T**` (for two points or two surfaces) `1*T***T**`
(for two curves).

#### GEOSGeometry.relate_pattern(other, pattern)

Returns `True` if the elements in the DE-9IM intersection matrix for this
geometry and the other matches the given `pattern` – a string of nine
characters from the alphabet: {`T`, `F`, `*`, `0`}.

#### GEOSGeometry.touches(other)

Returns `True` if the DE-9IM intersection matrix for the two geometries
is `FT*******`, `F**T*****` or `F***T****`.

#### GEOSGeometry.within(other)

Returns `True` if the DE-9IM intersection matrix for the two geometries
is `T*F**F***`.

#### Topological Methods

#### GEOSGeometry.buffer(width, quadsegs=8)

Returns a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) that represents all points whose distance
from this geometry is less than or equal to the given `width`. The
optional `quadsegs` keyword sets the number of segments used to
approximate a quarter circle (defaults is 8).

#### GEOSGeometry.buffer_with_style(width, quadsegs=8, end_cap_style=1, join_style=1, mitre_limit=5.0)

Same as [`buffer()`](#django.contrib.gis.geos.GEOSGeometry.buffer), but allows customizing the style of the buffer.

* `end_cap_style` can be round (`1`), flat (`2`), or square (`3`).
* `join_style` can be round (`1`), mitre (`2`), or bevel (`3`).
* Mitre ratio limit (`mitre_limit`) only affects mitered join style.

#### GEOSGeometry.difference(other)

Returns a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) representing the points making up this
geometry that do not make up other.

#### GEOSGeometry.interpolate(distance)

#### GEOSGeometry.interpolate_normalized(distance)

Given a distance (float), returns the point (or closest point) within the
geometry ([`LineString`](#django.contrib.gis.geos.LineString) or [`MultiLineString`](#django.contrib.gis.geos.MultiLineString)) at that
distance. The normalized version takes the distance as a float between 0
(origin) and 1 (endpoint).

Reverse of [`GEOSGeometry.project()`](#django.contrib.gis.geos.GEOSGeometry.project).

#### GEOSGeometry.intersection(other)

Returns a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) representing the points shared by this
geometry and other.

#### GEOSGeometry.project(point)

#### GEOSGeometry.project_normalized(point)

Returns the distance (float) from the origin of the geometry
([`LineString`](#django.contrib.gis.geos.LineString) or [`MultiLineString`](#django.contrib.gis.geos.MultiLineString)) to the point projected on
the geometry (that is to a point of the line the closest to the given
point). The normalized version returns the distance as a float between 0
(origin) and 1 (endpoint).

Reverse of [`GEOSGeometry.interpolate()`](#django.contrib.gis.geos.GEOSGeometry.interpolate).

#### GEOSGeometry.relate(other)

Returns the DE-9IM intersection matrix (a string) representing the
topological relationship between this geometry and the other.

#### GEOSGeometry.simplify(tolerance=0.0, preserve_topology=False)

Returns a new [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry), simplified to the specified tolerance
using the Douglas-Peucker algorithm. A higher tolerance value implies
fewer points in the output. If no tolerance is provided, it defaults to 0.

By default, this function does not preserve topology. For example,
[`Polygon`](#django.contrib.gis.geos.Polygon) objects can be split, be collapsed into lines, or
disappear. [`Polygon`](#django.contrib.gis.geos.Polygon) holes can be created or disappear, and lines
may cross. By specifying `preserve_topology=True`, the result will have
the same dimension and number of components as the input; this is
significantly slower, however.

#### GEOSGeometry.sym_difference(other)

Returns a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) combining the points in this geometry
not in other, and the points in other not in this geometry.

#### GEOSGeometry.union(other)

Returns a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) representing all the points in this
geometry and the other.

#### Topological Properties

#### GEOSGeometry.boundary

Returns the boundary as a newly allocated Geometry object.

#### GEOSGeometry.centroid

Returns a [`Point`](#django.contrib.gis.geos.Point) object representing the geometric center of
the geometry. The point is not guaranteed to be on the interior
of the geometry.

#### GEOSGeometry.convex_hull

Returns the smallest [`Polygon`](#django.contrib.gis.geos.Polygon) that contains all the points in
the geometry.

#### GEOSGeometry.envelope

Returns a [`Polygon`](#django.contrib.gis.geos.Polygon) that represents the bounding envelope of
this geometry. Note that it can also return a [`Point`](#django.contrib.gis.geos.Point) if the input
geometry is a point.

#### GEOSGeometry.point_on_surface

Computes and returns a [`Point`](#django.contrib.gis.geos.Point) guaranteed to be on the interior
of this geometry.

#### GEOSGeometry.unary_union

Computes the union of all the elements of this geometry.

The result obeys the following contract:

* Unioning a set of [`LineString`](#django.contrib.gis.geos.LineString)s has the effect of fully noding
  and dissolving the linework.
* Unioning a set of [`Polygon`](#django.contrib.gis.geos.Polygon)s will always return a
  [`Polygon`](#django.contrib.gis.geos.Polygon) or [`MultiPolygon`](#django.contrib.gis.geos.MultiPolygon) geometry (unlike
  [`GEOSGeometry.union()`](#django.contrib.gis.geos.GEOSGeometry.union), which may return geometries of lower
  dimension if a topology collapse occurs).

#### Other Properties & Methods

#### GEOSGeometry.area

This property returns the area of the Geometry.

#### GEOSGeometry.extent

This property returns the extent of this geometry as a 4-tuple,
consisting of `(xmin, ymin, xmax, ymax)`.

#### GEOSGeometry.clone()

This method returns a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) that is a clone of the
original.

#### GEOSGeometry.distance(geom)

Returns the distance between the closest points on this geometry and the
given `geom` (another [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) object).

#### NOTE
GEOS distance calculations are  linear – in other words, GEOS does not
perform a spherical calculation even if the SRID specifies a geographic
coordinate system.

#### GEOSGeometry.length

Returns the length of this geometry (e.g., 0 for a [`Point`](#django.contrib.gis.geos.Point),
the length of a [`LineString`](#django.contrib.gis.geos.LineString), or the circumference of
a [`Polygon`](#django.contrib.gis.geos.Polygon)).

#### GEOSGeometry.prepared

Returns a GEOS `PreparedGeometry` for the contents of this geometry.
`PreparedGeometry` objects are optimized for the contains, intersects,
covers, crosses, disjoint, overlaps, touches and within operations. Refer
to the [Prepared Geometries](#prepared-geometries) documentation for more information.

#### GEOSGeometry.srs

Returns a [`SpatialReference`](gdal.md#django.contrib.gis.gdal.SpatialReference) object
corresponding to the SRID of the geometry or `None`.

#### GEOSGeometry.transform(ct, clone=False)

Transforms the geometry according to the given coordinate transformation
parameter (`ct`), which may be an integer SRID, spatial reference WKT
string, a PROJ string, a [`SpatialReference`](gdal.md#django.contrib.gis.gdal.SpatialReference)
object, or a [`CoordTransform`](gdal.md#django.contrib.gis.gdal.CoordTransform) object. By
default, the geometry is transformed in-place and nothing is returned.
However if the `clone` keyword is set, then the geometry is not modified
and a transformed clone of the geometry is returned instead.

#### NOTE
Raises [`GEOSException`](#django.contrib.gis.geos.GEOSException) if GDAL is not
available or if the geometry’s SRID is `None` or less than 0. It
doesn’t impose any constraints on the geometry’s SRID if called with a
[`CoordTransform`](gdal.md#django.contrib.gis.gdal.CoordTransform) object.

#### GEOSGeometry.make_valid()

Returns a valid [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) equivalent, trying not to lose any of
the input vertices. If the geometry is already valid, it is returned
untouched. This is similar to the
[`MakeValid`](functions.md#django.contrib.gis.db.models.functions.MakeValid) database
function.

#### GEOSGeometry.normalize(clone=False)

Converts this geometry to canonical form. If the `clone` keyword is set,
then the geometry is not modified and a normalized clone of the geometry is
returned instead:

```pycon
>>> g = MultiPoint(Point(0, 0), Point(2, 2), Point(1, 1))
>>> print(g)
MULTIPOINT (0 0, 2 2, 1 1)
>>> g.normalize()
>>> print(g)
MULTIPOINT (2 2, 1 1, 0 0)
```

### `Point`

### *class* Point(x=None, y=None, z=None, srid=None)

`Point` objects are instantiated using arguments that represent the
component coordinates of the point or with a single sequence coordinates.
For example, the following are equivalent:

```pycon
>>> pnt = Point(5, 23)
>>> pnt = Point([5, 23])
```

Empty `Point` objects may be instantiated by passing no arguments or an
empty sequence. The following are equivalent:

```pycon
>>> pnt = Point()
>>> pnt = Point([])
```

### `LineString`

### *class* LineString(\*args, \*\*kwargs)

`LineString` objects are instantiated using arguments that are either a
sequence of coordinates or [`Point`](#django.contrib.gis.geos.Point) objects. For example, the
following are equivalent:

```pycon
>>> ls = LineString((0, 0), (1, 1))
>>> ls = LineString(Point(0, 0), Point(1, 1))
```

In addition, `LineString` objects may also be created by passing in a
single sequence of coordinate or [`Point`](#django.contrib.gis.geos.Point) objects:

```pycon
>>> ls = LineString(((0, 0), (1, 1)))
>>> ls = LineString([Point(0, 0), Point(1, 1)])
```

Empty `LineString` objects may be instantiated by passing no arguments
or an empty sequence. The following are equivalent:

```pycon
>>> ls = LineString()
>>> ls = LineString([])
```

#### closed

Returns whether or not this `LineString` is closed.

### `LinearRing`

### *class* LinearRing(\*args, \*\*kwargs)

`LinearRing` objects are constructed in the exact same way as
[`LineString`](#django.contrib.gis.geos.LineString) objects, however the coordinates must be *closed*, in
other words, the first coordinates must be the same as the last
coordinates. For example:

```pycon
>>> ls = LinearRing((0, 0), (0, 1), (1, 1), (0, 0))
```

Notice that `(0, 0)` is the first and last coordinate – if they were not
equal, an error would be raised.

#### is_counterclockwise

Returns whether this `LinearRing` is counterclockwise.

### `Polygon`

### *class* Polygon(\*args, \*\*kwargs)

`Polygon` objects may be instantiated by passing in parameters that
represent the rings of the polygon. The parameters must either be
[`LinearRing`](#django.contrib.gis.geos.LinearRing) instances, or a sequence that may be used to construct
a [`LinearRing`](#django.contrib.gis.geos.LinearRing):

```pycon
>>> ext_coords = ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))
>>> int_coords = ((0.4, 0.4), (0.4, 0.6), (0.6, 0.6), (0.6, 0.4), (0.4, 0.4))
>>> poly = Polygon(ext_coords, int_coords)
>>> poly = Polygon(LinearRing(ext_coords), LinearRing(int_coords))
```

#### *classmethod* from_bbox(bbox)

Returns a polygon object from the given bounding-box, a 4-tuple
comprising `(xmin, ymin, xmax, ymax)`.

#### num_interior_rings

Returns the number of interior rings in this geometry.

<a id="geos-geometry-collections"></a>

## Geometry Collections

### `MultiPoint`

### *class* MultiPoint(\*args, \*\*kwargs)

`MultiPoint` objects may be instantiated by passing in [`Point`](#django.contrib.gis.geos.Point)
objects as arguments, or a single sequence of [`Point`](#django.contrib.gis.geos.Point) objects:

```pycon
>>> mp = MultiPoint(Point(0, 0), Point(1, 1))
>>> mp = MultiPoint((Point(0, 0), Point(1, 1)))
```

### `MultiLineString`

### *class* MultiLineString(\*args, \*\*kwargs)

`MultiLineString` objects may be instantiated by passing in
[`LineString`](#django.contrib.gis.geos.LineString) objects as arguments, or a single sequence of
[`LineString`](#django.contrib.gis.geos.LineString) objects:

```pycon
>>> ls1 = LineString((0, 0), (1, 1))
>>> ls2 = LineString((2, 2), (3, 3))
>>> mls = MultiLineString(ls1, ls2)
>>> mls = MultiLineString([ls1, ls2])
```

#### merged

Returns a [`LineString`](#django.contrib.gis.geos.LineString) representing the line merge of
all the components in this `MultiLineString`.

#### closed

Returns `True` if and only if all elements are closed.

### `MultiPolygon`

### *class* MultiPolygon(\*args, \*\*kwargs)

`MultiPolygon` objects may be instantiated by passing [`Polygon`](#django.contrib.gis.geos.Polygon)
objects as arguments, or a single sequence of [`Polygon`](#django.contrib.gis.geos.Polygon) objects:

```pycon
>>> p1 = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
>>> p2 = Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))
>>> mp = MultiPolygon(p1, p2)
>>> mp = MultiPolygon([p1, p2])
```

### `GeometryCollection`

### *class* GeometryCollection(\*args, \*\*kwargs)

`GeometryCollection` objects may be instantiated by passing in other
[`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) as arguments, or a single sequence of
[`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) objects:

```pycon
>>> poly = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
>>> gc = GeometryCollection(Point(0, 0), MultiPoint(Point(0, 0), Point(1, 1)), poly)
>>> gc = GeometryCollection((Point(0, 0), MultiPoint(Point(0, 0), Point(1, 1)), poly))
```

<a id="prepared-geometries"></a>

## Prepared Geometries

In order to obtain a prepared geometry, access the
[`GEOSGeometry.prepared`](#django.contrib.gis.geos.GEOSGeometry.prepared) property. Once you have a `PreparedGeometry`
instance its spatial predicate methods, listed below, may be used with other
`GEOSGeometry` objects. An operation with a prepared geometry can be orders
of magnitude faster – the more complex the geometry that is prepared, the
larger the speedup in the operation. For more information, please consult the
[GEOS wiki page on prepared geometries](https://trac.osgeo.org/geos/wiki/PreparedGeometry).

For example:

```pycon
>>> from django.contrib.gis.geos import Point, Polygon
>>> poly = Polygon.from_bbox((0, 0, 5, 5))
>>> prep_poly = poly.prepared
>>> prep_poly.contains(Point(2.5, 2.5))
True
```

### `PreparedGeometry`

### *class* PreparedGeometry

All methods on `PreparedGeometry` take an `other` argument, which
must be a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) instance.

#### contains(other)

#### contains_properly(other)

#### covers(other)

#### crosses(other)

#### disjoint(other)

#### intersects(other)

#### overlaps(other)

#### touches(other)

#### within(other)

## Geometry Factories

### fromfile(file_h)

* **Parameters:**
  **file_h** (a Python `file` object or a string path to the file) – input file that contains spatial data
* **Return type:**
  a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) corresponding to the spatial data in the
  file

Example:

```pycon
>>> from django.contrib.gis.geos import fromfile
>>> g = fromfile("/home/bob/geom.wkt")
```

### fromstr(string, srid=None)

* **Parameters:**
  * **string** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – string that contains spatial data
  * **srid** ([*int*](https://docs.python.org/3/library/functions.html#int)) – spatial reference identifier
* **Return type:**
  a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) corresponding to the spatial data in the
  string

`fromstr(string, srid)` is equivalent to
[`GEOSGeometry(string, srid)`](#django.contrib.gis.geos.GEOSGeometry).

Example:

```pycon
>>> from django.contrib.gis.geos import fromstr
>>> pnt = fromstr("POINT(-90.5 29.5)", srid=4326)
```

## I/O Objects

### Reader Objects

The reader I/O classes return a [`GEOSGeometry`](#django.contrib.gis.geos.GEOSGeometry) instance from the WKB
and/or WKT input given to their `read(geom)` method.

### *class* WKBReader

Example:

```pycon
>>> from django.contrib.gis.geos import WKBReader
>>> wkb_r = WKBReader()
>>> wkb_r.read("0101000000000000000000F03F000000000000F03F")
<Point object at 0x103a88910>
```

### *class* WKTReader

Example:

```pycon
>>> from django.contrib.gis.geos import WKTReader
>>> wkt_r = WKTReader()
>>> wkt_r.read("POINT(1 1)")
<Point object at 0x103a88b50>
```

### Writer Objects

All writer objects have a `write(geom)` method that returns either the
WKB or WKT of the given geometry. In addition, [`WKBWriter`](#django.contrib.gis.geos.WKBWriter) objects
also have properties that may be used to change the byte order, and or
include the SRID value (in other words, EWKB).

### *class* WKBWriter(dim=2)

`WKBWriter` provides the most control over its output. By default it
returns OGC-compliant WKB when its `write` method is called. However,
it has properties that allow for the creation of EWKB, a superset of the
WKB standard that includes additional information. See the
[`WKBWriter.outdim`](#django.contrib.gis.geos.WKBWriter.outdim) documentation for more details about the `dim`
argument.

#### write(geom)

Returns the WKB of the given geometry as a Python `buffer` object.
Example:

```pycon
>>> from django.contrib.gis.geos import Point, WKBWriter
>>> pnt = Point(1, 1)
>>> wkb_w = WKBWriter()
>>> wkb_w.write(pnt)
<read-only buffer for 0x103a898f0, size -1, offset 0 at 0x103a89930>
```

#### write_hex(geom)

Returns WKB of the geometry in hexadecimal. Example:

```pycon
>>> from django.contrib.gis.geos import Point, WKBWriter
>>> pnt = Point(1, 1)
>>> wkb_w = WKBWriter()
>>> wkb_w.write_hex(pnt)
'0101000000000000000000F03F000000000000F03F'
```

#### byteorder

This property may be set to change the byte-order of the geometry
representation.

|   Byteorder Value | Description                                       |
|-------------------|---------------------------------------------------|
|                 0 | Big Endian (e.g., compatible with RISC systems)   |
|                 1 | Little Endian (e.g., compatible with x86 systems) |

Example:

```pycon
>>> from django.contrib.gis.geos import Point, WKBWriter
>>> wkb_w = WKBWriter()
>>> pnt = Point(1, 1)
>>> wkb_w.write_hex(pnt)
'0101000000000000000000F03F000000000000F03F'
>>> wkb_w.byteorder = 0
'00000000013FF00000000000003FF0000000000000'
```

#### outdim

This property may be set to change the output dimension of the geometry
representation. In other words, if you have a 3D geometry then set to 3
so that the Z value is included in the WKB.

|   Outdim Value | Description                 |
|----------------|-----------------------------|
|              2 | The default, output 2D WKB. |
|              3 | Output 3D WKB.              |

Example:

```pycon
>>> from django.contrib.gis.geos import Point, WKBWriter
>>> wkb_w = WKBWriter()
>>> wkb_w.outdim
2
>>> pnt = Point(1, 1, 1)
>>> wkb_w.write_hex(pnt)  # By default, no Z value included:
'0101000000000000000000F03F000000000000F03F'
>>> wkb_w.outdim = 3  # Tell writer to include Z values
>>> wkb_w.write_hex(pnt)
'0101000080000000000000F03F000000000000F03F000000000000F03F'
```

#### srid

Set this property with a boolean to indicate whether the SRID of the
geometry should be included with the WKB representation. Example:

```pycon
>>> from django.contrib.gis.geos import Point, WKBWriter
>>> wkb_w = WKBWriter()
>>> pnt = Point(1, 1, srid=4326)
>>> wkb_w.write_hex(pnt)  # By default, no SRID included:
'0101000000000000000000F03F000000000000F03F'
>>> wkb_w.srid = True  # Tell writer to include SRID
>>> wkb_w.write_hex(pnt)
'0101000020E6100000000000000000F03F000000000000F03F'
```

### *class* WKTWriter(dim=2, trim=False, precision=None)

This class allows outputting the WKT representation of a geometry. See the
[`WKBWriter.outdim`](#django.contrib.gis.geos.WKBWriter.outdim), [`trim`](#django.contrib.gis.geos.WKTWriter.trim), and [`precision`](#django.contrib.gis.geos.WKTWriter.precision) attributes
for details about the constructor arguments.

#### write(geom)

Returns the WKT of the given geometry. Example:

```pycon
>>> from django.contrib.gis.geos import Point, WKTWriter
>>> pnt = Point(1, 1)
>>> wkt_w = WKTWriter()
>>> wkt_w.write(pnt)
'POINT (1.0000000000000000 1.0000000000000000)'
```

#### outdim

See [`WKBWriter.outdim`](#django.contrib.gis.geos.WKBWriter.outdim).

#### trim

This property is used to enable or disable trimming of
unnecessary decimals.

```pycon
>>> from django.contrib.gis.geos import Point, WKTWriter
>>> pnt = Point(1, 1)
>>> wkt_w = WKTWriter()
>>> wkt_w.trim
False
>>> wkt_w.write(pnt)
'POINT (1.0000000000000000 1.0000000000000000)'
>>> wkt_w.trim = True
>>> wkt_w.write(pnt)
'POINT (1 1)'
```

#### precision

This property controls the rounding precision of coordinates;
if set to `None` rounding is disabled.

```pycon
>>> from django.contrib.gis.geos import Point, WKTWriter
>>> pnt = Point(1.44, 1.66)
>>> wkt_w = WKTWriter()
>>> print(wkt_w.precision)
None
>>> wkt_w.write(pnt)
'POINT (1.4399999999999999 1.6599999999999999)'
>>> wkt_w.precision = 0
>>> wkt_w.write(pnt)
'POINT (1 2)'
>>> wkt_w.precision = 1
>>> wkt_w.write(pnt)
'POINT (1.4 1.7)'
```

### Footnotes

* <a id='fnogc'>**[1]**</a> *See* [PostGIS EWKB, EWKT and Canonical Forms](https://postgis.net/docs/using_postgis_dbmanagement.html#EWKB_EWKT), PostGIS documentation at Ch. 4.1.2.

## Settings

<a id="std-setting-GEOS_LIBRARY_PATH"></a>

### `GEOS_LIBRARY_PATH`

A string specifying the location of the GEOS C library. Typically,
this setting is only used if the GEOS C library is in a non-standard
location (e.g., `/home/bob/lib/libgeos_c.so`).

#### NOTE
The setting must be the *full* path to the **C** shared library; in
other words you want to use `libgeos_c.so`, not `libgeos.so`.

## Exceptions

### *exception* GEOSException

The base GEOS exception, indicates a GEOS-related error.

# GIS QuerySet API Reference

<a id="spatial-lookups"></a>

## Spatial Lookups

The spatial lookups in this section are available for [`GeometryField`](model-api.md#django.contrib.gis.db.models.GeometryField)
and [`RasterField`](model-api.md#django.contrib.gis.db.models.RasterField).

For an introduction, see the [spatial lookups introduction](db-api.md#spatial-lookups-intro). For an overview of what lookups are
compatible with a particular spatial backend, refer to the
[spatial lookup compatibility table](db-api.md#spatial-lookup-compatibility).

### Lookups with rasters

All examples in the reference below are given for geometry fields and inputs,
but the lookups can be used the same way with rasters on both sides. Whenever
a lookup doesn’t support raster input, the input is automatically
converted to a geometry where necessary using the [ST_Polygon](https://postgis.net/docs/RT_ST_Polygon.html) function. See also the
[introduction to raster lookups](db-api.md#spatial-lookup-raster).

The database operators used by the lookups can be divided into three
categories:

- Native raster support `N`: the operator accepts rasters natively on both
  sides of the lookup, and raster input can be mixed with geometry inputs.
- Bilateral raster support `B`: the operator supports rasters only if both
  sides of the lookup receive raster inputs. Raster data is automatically
  converted to geometries for mixed lookups.
- Geometry conversion support `C`. The lookup does not have native raster
  support, all raster data is automatically converted to geometries.

The examples below show the SQL equivalent for the lookups in the different
types of raster support. The same pattern applies to all spatial lookups.

| Case   | Lookup                       | SQL Equivalent                                        |
|--------|------------------------------|-------------------------------------------------------|
| N, B   | `rast__contains=rst`         | `ST_Contains(rast, rst)`                              |
| N, B   | `rast__1__contains=(rst, 2)` | `ST_Contains(rast, 1, rst, 2)`                        |
| B, C   | `rast__contains=geom`        | `ST_Contains(ST_Polygon(rast), geom)`                 |
| B, C   | `rast__1__contains=geom`     | `ST_Contains(ST_Polygon(rast, 1), geom)`              |
| B, C   | `poly__contains=rst`         | `ST_Contains(poly, ST_Polygon(rst))`                  |
| B, C   | `poly__contains=(rst, 1)`    | `ST_Contains(poly, ST_Polygon(rst, 1))`               |
| C      | `rast__crosses=rst`          | `ST_Crosses(ST_Polygon(rast), ST_Polygon(rst))`       |
| C      | `rast__1__crosses=(rst, 2)`  | `ST_Crosses(ST_Polygon(rast, 1), ST_Polygon(rst, 2))` |
| C      | `rast__crosses=geom`         | `ST_Crosses(ST_Polygon(rast), geom)`                  |
| C      | `poly__crosses=rst`          | `ST_Crosses(poly, ST_Polygon(rst))`                   |

Spatial lookups with rasters are only supported for PostGIS backends
(denominated as PGRaster in this section).

<a id="std-fieldlookup-bbcontains"></a>

### `bbcontains`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Contain.html), MariaDB, MySQL,
SpatiaLite, PGRaster (Native)

Tests if the geometry or raster field’s bounding box completely contains the
lookup geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__bbcontains=geom)
```

| Backend    | SQL Equivalent            |
|------------|---------------------------|
| PostGIS    | `poly ~ geom`             |
| MariaDB    | `MBRContains(poly, geom)` |
| MySQL      | `MBRContains(poly, geom)` |
| SpatiaLite | `MbrContains(poly, geom)` |

<a id="std-fieldlookup-bboverlaps"></a>

### `bboverlaps`

*Availability*: [PostGIS](https://postgis.net/docs/geometry_overlaps.html),
MariaDB, MySQL, SpatiaLite, PGRaster (Native)

Tests if the geometry field’s bounding box overlaps the lookup geometry’s
bounding box.

Example:

```default
Zipcode.objects.filter(poly__bboverlaps=geom)
```

| Backend    | SQL Equivalent            |
|------------|---------------------------|
| PostGIS    | `poly && geom`            |
| MariaDB    | `MBROverlaps(poly, geom)` |
| MySQL      | `MBROverlaps(poly, geom)` |
| SpatiaLite | `MbrOverlaps(poly, geom)` |

<a id="std-fieldlookup-contained"></a>

### `contained`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Contained.html), MariaDB, MySQL,
SpatiaLite, PGRaster (Native)

Tests if the geometry field’s bounding box is completely contained by the
lookup geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__contained=geom)
```

| Backend    | SQL Equivalent          |
|------------|-------------------------|
| PostGIS    | `poly @ geom`           |
| MariaDB    | `MBRWithin(poly, geom)` |
| MySQL      | `MBRWithin(poly, geom)` |
| SpatiaLite | `MbrWithin(poly, geom)` |

<a id="std-fieldlookup-gis-contains"></a>

### `contains`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Contains.html),
Oracle, MariaDB, MySQL, SpatiaLite, PGRaster (Bilateral)

Tests if the geometry field spatially contains the lookup geometry.

Example:

```default
Zipcode.objects.filter(poly__contains=geom)
```

| Backend    | SQL Equivalent             |
|------------|----------------------------|
| PostGIS    | `ST_Contains(poly, geom)`  |
| Oracle     | `SDO_CONTAINS(poly, geom)` |
| MariaDB    | `ST_Contains(poly, geom)`  |
| MySQL      | `ST_Contains(poly, geom)`  |
| SpatiaLite | `Contains(poly, geom)`     |

<a id="std-fieldlookup-contains_properly"></a>

### `contains_properly`

*Availability*: [PostGIS](https://postgis.net/docs/ST_ContainsProperly.html), PGRaster (Bilateral)

Returns true if the lookup geometry intersects the interior of the
geometry field, but not the boundary (or exterior).

Example:

```default
Zipcode.objects.filter(poly__contains_properly=geom)
```

| Backend   | SQL Equivalent                    |
|-----------|-----------------------------------|
| PostGIS   | `ST_ContainsProperly(poly, geom)` |

<a id="std-fieldlookup-coveredby"></a>

### `coveredby`

*Availability*: [PostGIS](https://postgis.net/docs/ST_CoveredBy.html),
Oracle, MariaDB, MySQL, PGRaster (Bilateral), SpatiaLite

Tests if no point in the geometry field is outside the lookup geometry.
<sup>[3](#fncovers)</sup>

Example:

```default
Zipcode.objects.filter(poly__coveredby=geom)
```

| Backend    | SQL Equivalent              |
|------------|-----------------------------|
| PostGIS    | `ST_CoveredBy(poly, geom)`  |
| Oracle     | `SDO_COVEREDBY(poly, geom)` |
| MariaDB    | `MBRCoveredBy(poly, geom)`  |
| MySQL      | `MBRCoveredBy(poly, geom)`  |
| SpatiaLite | `CoveredBy(poly, geom)`     |

#### Versionchanged
MariaDB 12.0.1+ support was added.

<a id="std-fieldlookup-covers"></a>

### `covers`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Covers.html),
Oracle, MySQL, PGRaster (Bilateral), SpatiaLite

Tests if no point in the lookup geometry is outside the geometry field.
<sup>[3](#fncovers)</sup>

Example:

```default
Zipcode.objects.filter(poly__covers=geom)
```

| Backend    | SQL Equivalent           |
|------------|--------------------------|
| PostGIS    | `ST_Covers(poly, geom)`  |
| Oracle     | `SDO_COVERS(poly, geom)` |
| MySQL      | `MBRCovers(poly, geom)`  |
| SpatiaLite | `Covers(poly, geom)`     |

<a id="std-fieldlookup-crosses"></a>

### `crosses`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Crosses.html),
MariaDB, MySQL, SpatiaLite, PGRaster (Conversion)

Tests if the geometry field spatially crosses the lookup geometry.

Example:

```default
Zipcode.objects.filter(poly__crosses=geom)
```

| Backend    | SQL Equivalent           |
|------------|--------------------------|
| PostGIS    | `ST_Crosses(poly, geom)` |
| MariaDB    | `ST_Crosses(poly, geom)` |
| MySQL      | `ST_Crosses(poly, geom)` |
| SpatiaLite | `Crosses(poly, geom)`    |

<a id="std-fieldlookup-disjoint"></a>

### `disjoint`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Disjoint.html),
Oracle, MariaDB, MySQL, SpatiaLite, PGRaster (Bilateral)

Tests if the geometry field is spatially disjoint from the lookup geometry.

Example:

```default
Zipcode.objects.filter(poly__disjoint=geom)
```

| Backend    | SQL Equivalent                                  |
|------------|-------------------------------------------------|
| PostGIS    | `ST_Disjoint(poly, geom)`                       |
| Oracle     | `SDO_GEOM.RELATE(poly, 'DISJOINT', geom, 0.05)` |
| MariaDB    | `ST_Disjoint(poly, geom)`                       |
| MySQL      | `ST_Disjoint(poly, geom)`                       |
| SpatiaLite | `Disjoint(poly, geom)`                          |

<a id="std-fieldlookup-equals"></a>

### `equals`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Equals.html),
Oracle, MariaDB, MySQL, SpatiaLite, PGRaster (Conversion)

Tests if the geometry field is spatially equal to the lookup geometry.

Example:

```default
Zipcode.objects.filter(poly__equals=geom)
```

| Backend    | SQL Equivalent          |
|------------|-------------------------|
| PostGIS    | `ST_Equals(poly, geom)` |
| Oracle     | `SDO_EQUAL(poly, geom)` |
| MariaDB    | `ST_Equals(poly, geom)` |
| MySQL      | `ST_Equals(poly, geom)` |
| SpatiaLite | `Equals(poly, geom)`    |

<a id="std-fieldlookup-exact-noindex"></a>

<a id="std-fieldlookup-same_as"></a>

### `exact`, `same_as`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Same.html),
Oracle, MariaDB, MySQL, SpatiaLite, PGRaster (Bilateral)

Tests if the geometry field is “equal” to the lookup geometry. On Oracle,
MySQL, and SpatiaLite, it tests spatial equality, while on PostGIS it tests
equality of bounding boxes.

Example:

```default
Zipcode.objects.filter(poly=geom)
```

| Backend    | SQL Equivalent          |
|------------|-------------------------|
| PostGIS    | `poly ~= geom`          |
| Oracle     | `SDO_EQUAL(poly, geom)` |
| MariaDB    | `ST_Equals(poly, geom)` |
| MySQL      | `ST_Equals(poly, geom)` |
| SpatiaLite | `Equals(poly, geom)`    |

<a id="std-fieldlookup-intersects"></a>

### `intersects`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Intersects.html),
Oracle, MariaDB, MySQL, SpatiaLite, PGRaster (Bilateral)

Tests if the geometry field spatially intersects the lookup geometry.

Example:

```default
Zipcode.objects.filter(poly__intersects=geom)
```

| Backend    | SQL Equivalent                        |
|------------|---------------------------------------|
| PostGIS    | `ST_Intersects(poly, geom)`           |
| Oracle     | `SDO_OVERLAPBDYINTERSECT(poly, geom)` |
| MariaDB    | `ST_Intersects(poly, geom)`           |
| MySQL      | `ST_Intersects(poly, geom)`           |
| SpatiaLite | `Intersects(poly, geom)`              |

<a id="std-fieldlookup-isempty"></a>

### `isempty`

*Availability*: [PostGIS](https://postgis.net/docs/ST_IsEmpty.html),
SpatiaLite

Tests if the geometry is empty.

Example:

```default
Zipcode.objects.filter(poly__isempty=True)
```

#### Versionchanged
SpatiaLite support was added.

<a id="std-fieldlookup-isvalid"></a>

### `isvalid`

*Availability*: MariaDB, MySQL,
[PostGIS](https://postgis.net/docs/ST_IsValid.html), Oracle, SpatiaLite

Tests if the geometry is valid.

Example:

```default
Zipcode.objects.filter(poly__isvalid=True)
```

| Backend                             | SQL Equivalent                                                 |
|-------------------------------------|----------------------------------------------------------------|
| MariaDB, MySQL, PostGIS, SpatiaLite | `ST_IsValid(poly)`                                             |
| Oracle                              | `SDO_GEOM.VALIDATE_GEOMETRY_WITH_CONTEXT(poly, 0.05) = 'TRUE'` |

#### Versionchanged
MariaDB 12.0.1+ support was added.

<a id="std-fieldlookup-geom_type"></a>

### `geom_type`

#### Versionadded

*Availability*: [PostGIS](https://postgis.net/docs/GeometryType.html),
Oracle 23c+, MariaDB, MySQL, SpatiaLite

Returns the geometry type of the geometry field.

Example:

```default
Zipcode.objects.filter(poly__geom_type="POLYGON")
```

| Backend    | SQL Equivalent                 |
|------------|--------------------------------|
| PostGIS    | `GeometryType(geom)`           |
| MariaDB    | `ST_GeometryType(geom)`        |
| MySQL      | `ST_GeometryType(geom)`        |
| Oracle     | `SDO_GEOMETRY.GET_GTYPE(geom)` |
| SpatiaLite | `GeometryType(geom)`           |

<a id="std-fieldlookup-num_dimensions"></a>

### `num_dimensions`

#### Versionadded

*Availability*: [PostGIS](https://postgis.net/docs/ST_NDims.html),
SpatiaLite

Returns the number of dimensions used by the geometry.

Example:

```default
Zipcode.objects.filter(geom__num_dimensions=3)
```

| Backend             | SQL Equivalent   |
|---------------------|------------------|
| PostGIS, SpatiaLite | `ST_NDims(geom)` |

<a id="std-fieldlookup-overlaps"></a>

### `overlaps`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Overlaps.html),
Oracle, MariaDB, MySQL, SpatiaLite, PGRaster (Bilateral)

Tests if the geometry field spatially overlaps the lookup geometry.

| Backend    | SQL Equivalent             |
|------------|----------------------------|
| PostGIS    | `ST_Overlaps(poly, geom)`  |
| Oracle     | `SDO_OVERLAPS(poly, geom)` |
| MariaDB    | `ST_Overlaps(poly, geom)`  |
| MySQL      | `ST_Overlaps(poly, geom)`  |
| SpatiaLite | `Overlaps(poly, geom)`     |

<a id="std-fieldlookup-relate"></a>

### `relate`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Relate.html),
MariaDB, Oracle, SpatiaLite, PGRaster (Conversion)

Tests if the geometry field is spatially related to the lookup geometry by the
values given in the given pattern. This lookup requires a tuple parameter,
`(geom, pattern)`; the form of `pattern` will depend on the spatial
backend:

#### MariaDB, PostGIS, and SpatiaLite

On these spatial backends the intersection pattern is a string comprising nine
characters, which  define intersections between  the interior, boundary, and
exterior of the geometry field and the lookup geometry. The intersection
pattern matrix may only use the following characters: `1`, `2`, `T`,
`F`, or `*`. This lookup type allows users to “fine tune” a specific
geometric relationship consistent with the DE-9IM model. <sup>[1](#fnde9im)</sup>

Geometry example:

```default
# A tuple lookup parameter is used to specify the geometry and
# the intersection pattern (the pattern here is for 'contains').
Zipcode.objects.filter(poly__relate=(geom, "T*T***FF*"))
```

PostGIS and MariaDB SQL equivalent:

```sql
SELECT ... WHERE ST_Relate(poly, geom, 'T*T***FF*')
```

SpatiaLite SQL equivalent:

```sql
SELECT ... WHERE Relate(poly, geom, 'T*T***FF*')
```

Raster example:

```default
Zipcode.objects.filter(poly__relate=(rast, 1, "T*T***FF*"))
Zipcode.objects.filter(rast__2__relate=(rast, 1, "T*T***FF*"))
```

PostGIS SQL equivalent:

```sql
SELECT ... WHERE ST_Relate(poly, ST_Polygon(rast, 1), 'T*T***FF*')
SELECT ... WHERE ST_Relate(ST_Polygon(rast, 2), ST_Polygon(rast, 1), 'T*T***FF*')
```

#### Oracle

Here the relation pattern is comprised of at least one of the nine relation
strings: `TOUCH`, `OVERLAPBDYDISJOINT`, `OVERLAPBDYINTERSECT`,
`EQUAL`, `INSIDE`, `COVEREDBY`, `CONTAINS`, `COVERS`, `ON`, and
`ANYINTERACT`. Multiple strings may be combined with the logical Boolean
operator OR, for example, `'inside+touch'`. <sup>[2](#fnsdorelate)</sup>  The relation
strings are case-insensitive.

Example:

```default
Zipcode.objects.filter(poly__relate=(geom, "anyinteract"))
```

Oracle SQL equivalent:

```sql
SELECT ... WHERE SDO_RELATE(poly, geom, 'anyinteract')
```

<a id="std-fieldlookup-touches"></a>

### `touches`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Touches.html),
Oracle, MariaDB, MySQL, SpatiaLite

Tests if the geometry field spatially touches the lookup geometry.

Example:

```default
Zipcode.objects.filter(poly__touches=geom)
```

| Backend    | SQL Equivalent           |
|------------|--------------------------|
| PostGIS    | `ST_Touches(poly, geom)` |
| MariaDB    | `ST_Touches(poly, geom)` |
| MySQL      | `ST_Touches(poly, geom)` |
| Oracle     | `SDO_TOUCH(poly, geom)`  |
| SpatiaLite | `Touches(poly, geom)`    |

<a id="std-fieldlookup-within"></a>

### `within`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Within.html),
Oracle, MariaDB, MySQL, SpatiaLite, PGRaster (Bilateral)

Tests if the geometry field is spatially within the lookup geometry.

Example:

```default
Zipcode.objects.filter(poly__within=geom)
```

| Backend    | SQL Equivalent           |
|------------|--------------------------|
| PostGIS    | `ST_Within(poly, geom)`  |
| MariaDB    | `ST_Within(poly, geom)`  |
| MySQL      | `ST_Within(poly, geom)`  |
| Oracle     | `SDO_INSIDE(poly, geom)` |
| SpatiaLite | `Within(poly, geom)`     |

<a id="std-fieldlookup-left"></a>

### `left`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Left.html),
PGRaster (Conversion)

Tests if the geometry field’s bounding box is strictly to the left of the
lookup geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__left=geom)
```

PostGIS equivalent:

```sql
SELECT ... WHERE poly << geom
```

<a id="std-fieldlookup-right"></a>

### `right`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Right.html),
PGRaster (Conversion)

Tests if the geometry field’s bounding box is strictly to the right of the
lookup geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__right=geom)
```

PostGIS equivalent:

```sql
SELECT ... WHERE poly >> geom
```

<a id="std-fieldlookup-overlaps_left"></a>

### `overlaps_left`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Overleft.html), PGRaster (Bilateral)

Tests if the geometry field’s bounding box overlaps or is to the left of the
lookup geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__overlaps_left=geom)
```

PostGIS equivalent:

```sql
SELECT ... WHERE poly &< geom
```

<a id="std-fieldlookup-overlaps_right"></a>

### `overlaps_right`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Overright.html), PGRaster (Bilateral)

Tests if the geometry field’s bounding box overlaps or is to the right of the
lookup geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__overlaps_right=geom)
```

PostGIS equivalent:

```sql
SELECT ... WHERE poly &> geom
```

<a id="std-fieldlookup-overlaps_above"></a>

### `overlaps_above`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Overabove.html), PGRaster (Conversion)

Tests if the geometry field’s bounding box overlaps or is above the lookup
geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__overlaps_above=geom)
```

PostGIS equivalent:

```sql
SELECT ... WHERE poly |&> geom
```

<a id="std-fieldlookup-overlaps_below"></a>

### `overlaps_below`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Overbelow.html), PGRaster (Conversion)

Tests if the geometry field’s bounding box overlaps or is below the lookup
geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__overlaps_below=geom)
```

PostGIS equivalent:

```sql
SELECT ... WHERE poly &<| geom
```

<a id="std-fieldlookup-strictly_above"></a>

### `strictly_above`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Above.html),
PGRaster (Conversion)

Tests if the geometry field’s bounding box is strictly above the lookup
geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__strictly_above=geom)
```

PostGIS equivalent:

```sql
SELECT ... WHERE poly |>> geom
```

<a id="std-fieldlookup-strictly_below"></a>

### `strictly_below`

*Availability*: [PostGIS](https://postgis.net/docs/ST_Geometry_Below.html),
PGRaster (Conversion)

Tests if the geometry field’s bounding box is strictly below the lookup
geometry’s bounding box.

Example:

```default
Zipcode.objects.filter(poly__strictly_below=geom)
```

PostGIS equivalent:

```sql
SELECT ... WHERE poly <<| geom
```

<a id="distance-lookups"></a>

## Distance Lookups

*Availability*: PostGIS, Oracle, MariaDB, MySQL, SpatiaLite, PGRaster (Native)

For an overview on performing distance queries, please refer to
the [distance queries introduction](db-api.md#distance-queries).

Distance lookups take the following form:

```text
<field>__<distance lookup>=(<geometry/raster>, <distance value>[, "spheroid"])
<field>__<distance lookup>=(<raster>, <band_index>, <distance value>[, "spheroid"])
<field>__<band_index>__<distance lookup>=(<raster>, <band_index>, <distance value>[, "spheroid"])
```

The value passed into a distance lookup is a tuple; the first two
values are mandatory, and are the geometry to calculate distances to,
and a distance value (either a number in units of the field, a
[`Distance`](measure.md#django.contrib.gis.measure.Distance) object, or a [query
expression](../../models/expressions.md)). To pass a band index to the lookup, use
a 3-tuple where the second entry is the band index.

On every distance lookup except [`dwithin`](#std-fieldlookup-dwithin), an optional element,
`'spheroid'`, may be included to use the more accurate spheroid distance
calculation functions on fields with a geodetic coordinate system.

On PostgreSQL, the `'spheroid'` option uses [ST_DistanceSpheroid](https://postgis.net/docs/ST_Distance_Spheroid.html) instead of
[ST_DistanceSphere](https://postgis.net/docs/ST_DistanceSphere.html). The
simpler [ST_Distance](https://postgis.net/docs/ST_Distance.html) function is
used with projected coordinate systems. Rasters are converted to geometries for
spheroid based lookups.

<a id="std-fieldlookup-distance_gt"></a>

### `distance_gt`

Returns models where the distance to the geometry field from the lookup
geometry is greater than the given distance value.

Example:

```default
Zipcode.objects.filter(poly__distance_gt=(geom, D(m=5)))
```

| Backend    | SQL Equivalent                                   |
|------------|--------------------------------------------------|
| PostGIS    | `ST_Distance/ST_Distance_Sphere(poly, geom) > 5` |
| MariaDB    | `ST_Distance(poly, geom) > 5`                    |
| MySQL      | `ST_Distance(poly, geom) > 5`                    |
| Oracle     | `SDO_GEOM.SDO_DISTANCE(poly, geom, 0.05) > 5`    |
| SpatiaLite | `Distance(poly, geom) > 5`                       |

<a id="std-fieldlookup-distance_gte"></a>

### `distance_gte`

Returns models where the distance to the geometry field from the lookup
geometry is greater than or equal to the given distance value.

Example:

```default
Zipcode.objects.filter(poly__distance_gte=(geom, D(m=5)))
```

| Backend    | SQL Equivalent                                    |
|------------|---------------------------------------------------|
| PostGIS    | `ST_Distance/ST_Distance_Sphere(poly, geom) >= 5` |
| MariaDB    | `ST_Distance(poly, geom) >= 5`                    |
| MySQL      | `ST_Distance(poly, geom) >= 5`                    |
| Oracle     | `SDO_GEOM.SDO_DISTANCE(poly, geom, 0.05) >= 5`    |
| SpatiaLite | `Distance(poly, geom) >= 5`                       |

<a id="std-fieldlookup-distance_lt"></a>

### `distance_lt`

Returns models where the distance to the geometry field from the lookup
geometry is less than the given distance value.

Example:

```default
Zipcode.objects.filter(poly__distance_lt=(geom, D(m=5)))
```

| Backend    | SQL Equivalent                                   |
|------------|--------------------------------------------------|
| PostGIS    | `ST_Distance/ST_Distance_Sphere(poly, geom) < 5` |
| MariaDB    | `ST_Distance(poly, geom) < 5`                    |
| MySQL      | `ST_Distance(poly, geom) < 5`                    |
| Oracle     | `SDO_GEOM.SDO_DISTANCE(poly, geom, 0.05) < 5`    |
| SpatiaLite | `Distance(poly, geom) < 5`                       |

<a id="std-fieldlookup-distance_lte"></a>

### `distance_lte`

Returns models where the distance to the geometry field from the lookup
geometry is less than or equal to the given distance value.

Example:

```default
Zipcode.objects.filter(poly__distance_lte=(geom, D(m=5)))
```

| Backend    | SQL Equivalent                                    |
|------------|---------------------------------------------------|
| PostGIS    | `ST_Distance/ST_Distance_Sphere(poly, geom) <= 5` |
| MariaDB    | `ST_Distance(poly, geom) <= 5`                    |
| MySQL      | `ST_Distance(poly, geom) <= 5`                    |
| Oracle     | `SDO_GEOM.SDO_DISTANCE(poly, geom, 0.05) <= 5`    |
| SpatiaLite | `Distance(poly, geom) <= 5`                       |

<a id="std-fieldlookup-dwithin"></a>

### `dwithin`

Returns models where the distance to the geometry field from the lookup
geometry are within the given distance from one another. Note that you can only
provide [`Distance`](measure.md#django.contrib.gis.measure.Distance) objects if the targeted
geometries are in a projected system. For geographic geometries, you should use
units of the geometry field (e.g. degrees for `WGS84`) .

Example:

```default
Zipcode.objects.filter(poly__dwithin=(geom, D(m=5)))
```

| Backend    | SQL Equivalent                       |
|------------|--------------------------------------|
| PostGIS    | `ST_DWithin(poly, geom, 5)`          |
| Oracle     | `SDO_WITHIN_DISTANCE(poly, geom, 5)` |
| SpatiaLite | `PtDistWithin(poly, geom, 5)`        |

<a id="gis-aggregation-functions"></a>

### Aggregate Functions

Django provides some GIS-specific aggregate functions. For details on how to
use these aggregate functions, see [the topic guide on aggregation](../../../topics/db/aggregation.md).

| Keyword Argument   | Description                                                                                                                                                                                                                                                                                        |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `tolerance`        | This keyword is for Oracle only. It is for the<br/>tolerance value used by the `SDOAGGRTYPE`<br/>procedure; the  [Oracle documentation](https://docs.oracle.com/en/database/oracle/oracle-database/21/spatl/spatial-concepts.html#GUID-CE10AB14-D5EA-43BA-A647-DAC9EEF41EE6) has more<br/>details. |

Example:

```pycon
>>> from django.contrib.gis.db.models import Extent, Union
>>> WorldBorder.objects.aggregate(Extent("mpoly"), Union("mpoly"))
```

#### `Collect`

### *class* Collect(geo_field, filter=None)

*Availability*: [PostGIS](https://postgis.net/docs/ST_Collect.html),
MariaDB, MySQL, SpatiaLite

Returns a `GEOMETRYCOLLECTION` or a `MULTI` geometry object from the
geometry column. This is analogous to a simplified version of the
[`Union`](#django.contrib.gis.db.models.Union) aggregate, except it can be several orders of magnitude faster
than performing a union because it rolls up geometries into a collection or
multi object, not caring about dissolving boundaries.

#### Versionchanged
MariaDB 12.0.1+ support was added.

#### `Extent`

### *class* Extent(geo_field, filter=None)

*Availability*: [PostGIS](https://postgis.net/docs/ST_Extent.html),
Oracle, SpatiaLite

Returns the extent of all `geo_field` in the `QuerySet` as a 4-tuple,
comprising the lower left coordinate and the upper right coordinate.

Example:

```pycon
>>> qs = City.objects.filter(name__in=("Houston", "Dallas")).aggregate(Extent("poly"))
>>> print(qs["poly__extent"])
(-96.8016128540039, 29.7633724212646, -95.3631439208984, 32.782058715820)
```

#### `Extent3D`

### *class* Extent3D(geo_field, filter=None)

*Availability*: [PostGIS](https://postgis.net/docs/ST_3DExtent.html)

Returns the 3D extent of all `geo_field` in the `QuerySet` as a 6-tuple,
comprising the lower left coordinate and upper right coordinate (each with x,
y, and z coordinates).

Example:

```pycon
>>> qs = City.objects.filter(name__in=("Houston", "Dallas")).aggregate(Extent3D("poly"))
>>> print(qs["poly__extent3d"])
(-96.8016128540039, 29.7633724212646, 0, -95.3631439208984, 32.782058715820, 0)
```

#### `MakeLine`

### *class* MakeLine(geo_field, filter=None)

*Availability*: [PostGIS](https://postgis.net/docs/ST_MakeLine.html),
SpatiaLite

Returns a `LineString` constructed from the point field geometries in the
`QuerySet`. Currently, ordering the queryset has no effect.

Example:

```pycon
>>> qs = City.objects.filter(name__in=("Houston", "Dallas")).aggregate(MakeLine("poly"))
>>> print(qs["poly__makeline"])
LINESTRING (-95.3631510000000020 29.7633739999999989, -96.8016109999999941 32.7820570000000018)
```

#### `Union`

### *class* Union(geo_field, filter=None)

*Availability*: [PostGIS](https://postgis.net/docs/ST_Union.html),
Oracle, SpatiaLite

This method returns a [`GEOSGeometry`](geos.md#django.contrib.gis.geos.GEOSGeometry) object
comprising the union of every geometry in the queryset. Please note that use of
`Union` is processor intensive and may take a significant amount of time on
large querysets.

#### NOTE
If the computation time for using this method is too expensive, consider
using [`Collect`](#django.contrib.gis.db.models.Collect) instead.

Example:

```pycon
>>> u = Zipcode.objects.aggregate(Union(poly))  # This may take a long time.
>>> u = Zipcode.objects.filter(poly__within=bbox).aggregate(
...     Union(poly)
... )  # A more sensible approach.
```

### Footnotes

* <a id='fnde9im'>**[1]**</a> *See* [OpenGIS Simple Feature Specification For SQL](https://portal.ogc.org/files/?artifact_id=829), at Ch. 2.1.13.2, p. 2-13 (The Dimensionally Extended Nine-Intersection Model).
* <a id='fnsdorelate'>**[2]**</a> *See* [SDO_RELATE documentation](https://docs.oracle.com/en/database/oracle/oracle-database/18/spatl/spatial-operators-reference.html#GUID-97C17C18-F05E-49B4-BE11-E89B972E2A02), from the Oracle Spatial and Graph Developer’s Guide.
* <a id='fncovers'>**[3]**</a> For an explanation of this routine, read [Quirks of the “Contains” Spatial Predicate](https://lin-ear-th-inking.blogspot.com/2007/06/subtleties-of-ogc-covers-spatial.html) by Martin Davis (a PostGIS developer).

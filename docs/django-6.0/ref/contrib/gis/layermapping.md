# `LayerMapping` data import utility

The [`LayerMapping`](#django.contrib.gis.utils.LayerMapping) class provides a way to map the contents of
vector spatial data files (e.g. shapefiles) into GeoDjango models.

This utility grew out of the author’s personal needs to eliminate
the code repetition that went into pulling geometries and fields out of
a vector layer, converting to another coordinate system (e.g. WGS84), and
then inserting into a GeoDjango model.

#### NOTE
Use of [`LayerMapping`](#django.contrib.gis.utils.LayerMapping) requires GDAL.

#### WARNING
GIS data sources, like shapefiles, may be very large. If you find that
[`LayerMapping`](#django.contrib.gis.utils.LayerMapping) is using too much memory, set [`DEBUG`](../../settings.md#std-setting-DEBUG) to
`False` in your settings. When [`DEBUG`](../../settings.md#std-setting-DEBUG) is set to `True`,
Django [automatically logs](../../../faq/models.md#faq-see-raw-sql-queries) *every* SQL
query – and when SQL statements contain geometries, this may consume more
memory than is typical.

## Example

1. You need a GDAL-supported data source, like a shapefile (here we’re using
   a simple polygon shapefile, `test_poly.shp`, with three features):

```pycon
>>> from django.contrib.gis.gdal import DataSource
>>> ds = DataSource("test_poly.shp")
>>> layer = ds[0]
>>> print(layer.fields)  # Exploring the fields in the layer, we only want the 'str' field.
['float', 'int', 'str']
>>> print(len(layer))  # getting the number of features in the layer (should be 3)
3
>>> print(layer.geom_type)  # Should be 'Polygon'
Polygon
>>> print(layer.srs)  # WGS84 in WKT
GEOGCS["GCS_WGS_1984",
    DATUM["WGS_1984",
        SPHEROID["WGS_1984",6378137,298.257223563]],
    PRIMEM["Greenwich",0],
    UNIT["Degree",0.017453292519943295]]
```

1. Now we define our corresponding Django model (make sure to use
   [`migrate`](../../django-admin.md#django-admin-migrate)):
   ```default
   from django.contrib.gis.db import models


   class TestGeo(models.Model):
       name = models.CharField(max_length=25)  # corresponds to the 'str' field
       poly = models.PolygonField(srid=4269)  # we want our model in a different SRID

       def __str__(self):
           return "Name: %s" % self.name
   ```
2. Use [`LayerMapping`](#django.contrib.gis.utils.LayerMapping) to extract all the features and place them in the
   database:

```pycon
>>> from django.contrib.gis.utils import LayerMapping
>>> from geoapp.models import TestGeo
>>> mapping = {
...     "name": "str",  # The 'name' model field maps to the 'str' layer field.
...     "poly": "POLYGON",  # For geometry fields use OGC name.
... }  # The mapping is a dictionary
>>> lm = LayerMapping(TestGeo, "test_poly.shp", mapping)
>>> lm.save(verbose=True)  # Save the layermap, imports the data.
Saved: Name: 1
Saved: Name: 2
Saved: Name: 3
```

Here, [`LayerMapping`](#django.contrib.gis.utils.LayerMapping) transformed the three geometries from the shapefile
in their original spatial reference system (WGS84) to the spatial reference
system of the GeoDjango model (NAD83). If no spatial reference system is
defined for the layer, use the `source_srs` keyword with a
[`SpatialReference`](gdal.md#django.contrib.gis.gdal.SpatialReference) object to specify one.

## `LayerMapping` API

### *class* LayerMapping(model, data_source, mapping, layer=0, source_srs=None, encoding=None, transaction_mode='commit_on_success', transform=True, unique=True, using='default')

The following are the arguments and keywords that may be used during
instantiation of `LayerMapping` objects.

| Argument      | Description                                                                                                                                                                                                                                                                                   |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `model`       | The geographic model, *not* an instance.                                                                                                                                                                                                                                                      |
| `data_source` | The path to the OGR-supported data source file<br/>(e.g., a shapefile). Also accepts<br/>[`django.contrib.gis.gdal.DataSource`](gdal.md#django.contrib.gis.gdal.DataSource) instances.                                                                                                        |
| `mapping`     | A dictionary: keys are strings corresponding to<br/>the model field, and values correspond to<br/>string field names for the OGR feature, or if the<br/>model field is a geographic then it should<br/>correspond to the OGR geometry type,<br/>e.g., `'POINT'`, `'LINESTRING'`, `'POLYGON'`. |

| Keyword Arguments   |                                                                                                                                                                                                                                                                                                  |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `layer`             | The index of the layer to use from the Data Source<br/>(defaults to 0)                                                                                                                                                                                                                           |
| `source_srs`        | Use this to specify the source SRS manually (for<br/>example, some shapefiles don’t come with a `'.prj'`<br/>file). An integer SRID, WKT or PROJ strings, and<br/>[`django.contrib.gis.gdal.SpatialReference`](gdal.md#django.contrib.gis.gdal.SpatialReference)<br/>objects are accepted.       |
| `encoding`          | Specifies the character set encoding of the strings<br/>in the OGR data source. For example, `'latin-1'`,<br/>`'utf-8'`, and `'cp437'` are all valid encoding<br/>parameters.                                                                                                                    |
| `transaction_mode`  | May be `'commit_on_success'` (default) or<br/>`'autocommit'`.                                                                                                                                                                                                                                    |
| `transform`         | Setting this to False will disable coordinate<br/>transformations. In other words, geometries will<br/>be inserted into the database unmodified from their<br/>original state in the data source.                                                                                                |
| `unique`            | Setting this to the name, or a tuple of names,<br/>from the given  model will create models unique<br/>only to the given name(s). Geometries from<br/>each feature will be added into the collection<br/>associated with the unique model. Forces<br/>the transaction mode to be `'autocommit'`. |
| `using`             | Sets the database to use when importing spatial data.<br/>Default is `'default'`.                                                                                                                                                                                                                |

### `save()` Keyword Arguments

#### LayerMapping.save(verbose=False, fid_range=False, step=False, progress=False, silent=False, stream=sys.stdout, strict=False)

The `save()` method also accepts keywords. These keywords are
used for controlling output logging, error handling, and for importing
specific feature ranges.

| Save Keyword Arguments   | Description                                                                                                                                                                                                                                                                                                                                    |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `fid_range`              | May be set with a slice or tuple of<br/>(begin, end) feature ID’s to map from<br/>the data source. In other words, this<br/>keyword enables the user to selectively<br/>import a subset range of features in the<br/>geographic data source.                                                                                                   |
| `progress`               | When this keyword is set, status information<br/>will be printed giving the number of features<br/>processed and successfully saved. By default,<br/>progress information will be printed every 1000<br/>features processed, however, this default may<br/>be overridden by setting this keyword with an<br/>integer for the desired interval. |
| `silent`                 | By default, non-fatal error notifications are<br/>printed to `sys.stdout`, but this keyword may<br/>be set to disable these notifications.                                                                                                                                                                                                     |
| `step`                   | If set with an integer, transactions will<br/>occur at every step interval. For example, if<br/>`step=1000`, a commit would occur after the<br/>1,000th feature, the 2,000th feature etc.                                                                                                                                                      |
| `stream`                 | Status information will be written to this file<br/>handle. Defaults to using `sys.stdout`, but<br/>any object with a `write` method is supported.                                                                                                                                                                                             |
| `strict`                 | Execution of the model mapping will cease upon<br/>the first error encountered. The default value<br/>(`False`)<br/>behavior is to attempt to continue.                                                                                                                                                                                        |
| `verbose`                | If set, information will be printed<br/>subsequent to each model save<br/>executed on the database.                                                                                                                                                                                                                                            |

## Troubleshooting

### Running out of memory

As noted in the warning at the top of this section, Django stores all SQL
queries when `DEBUG=True`. Set `DEBUG=False` in your settings, and this
should stop excessive memory use when running `LayerMapping` scripts.

### MySQL: `max_allowed_packet` error

If you encounter the following error when using `LayerMapping` and MySQL:

```pytb
OperationalError: (1153, "Got a packet bigger than 'max_allowed_packet' bytes")
```

Then the solution is to increase the value of the `max_allowed_packet`
setting in your MySQL configuration. For example, the default value may
be something low like one megabyte – the setting may be modified in MySQL’s
configuration file (`my.cnf`) in the `[mysqld]` section:

```ini
max_allowed_packet = 10M
```

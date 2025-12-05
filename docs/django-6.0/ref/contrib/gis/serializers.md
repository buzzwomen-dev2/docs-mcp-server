# `GeoJSON` Serializer

GeoDjango provides a specific serializer for the [GeoJSON](https://geojson.org/) format. See
[Serializing Django objects](../../../topics/serialization.md) for more information on serialization.

The `geojson` serializer is not meant for round-tripping data, as it has no
deserializer equivalent. For example, you cannot use [`loaddata`](../../django-admin.md#django-admin-loaddata) to
reload the output produced by this serializer. If you plan to reload the
outputted data, use the plain [json serializer](../../../topics/serialization.md#serialization-formats-json) instead.

In addition to the options of the `json` serializer, the `geojson`
serializer accepts the following additional option when it is called by
`serializers.serialize()`:

* `geometry_field`: A string containing the name of a geometry field to use
  for the `geometry` key of the GeoJSON feature. This is only needed when you
  have a model with more than one geometry field and you don’t want to use the
  first defined geometry field (by default, the first geometry field is
  picked).
* `id_field`: A string containing the name of a field to use for the `id`
  key of the GeoJSON feature. By default, the primary key of objects is used.
* `srid`: The SRID to use for the `geometry` content. Defaults to 4326
  (WGS 84).

The [fields](../../../topics/serialization.md#subset-of-fields) option can be used to limit fields that
will be present in the `properties` key, as it works with all other
serializers.

Example:

```default
from django.core.serializers import serialize
from my_app.models import City

serialize("geojson", City.objects.all(), geometry_field="point", fields=["name"])
```

Would output:

```default
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": 1,
            "geometry": {"type": "Point", "coordinates": [-87.650175, 41.850385]},
            "properties": {"name": "Chicago"},
        }
    ],
}
```

When the `fields` parameter is not specified, the `geojson` serializer adds
a `pk` key to the `properties` dictionary with the primary key of the
object as the value.

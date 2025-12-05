# Geographic Feeds

GeoDjango has its own [`Feed`](#django.contrib.gis.feeds.Feed) subclass that may embed location
information in RSS/Atom feeds formatted according to either the [Simple
GeoRSS](https://www.ogc.org/standard/georss/) or [W3C Geo](https://www.w3.org/2003/01/geo/) standards. Because GeoDjango’s syndication API is a
superset of Django’s, please consult [Django’s syndication documentation](../syndication.md) for details on general usage.

## Example

## API Reference

### `Feed` Subclass

### *class* Feed

In addition to methods provided by the
[`django.contrib.syndication.views.Feed`](../syndication.md#django.contrib.syndication.views.Feed) base class, GeoDjango’s
`Feed` class provides the following overrides. Note that these overrides
may be done in multiple ways:

```default
from django.contrib.gis.feeds import Feed


class MyFeed(Feed):
    # First, as a class attribute.
    geometry = ...
    item_geometry = ...

    # Also a function with no arguments
    def geometry(self): ...

    def item_geometry(self): ...

    # And as a function with a single argument
    def geometry(self, obj): ...

    def item_geometry(self, item): ...
```

#### geometry(obj)

Takes the object returned by `get_object()` and returns the *feed’s*
geometry. Typically this is a `GEOSGeometry` instance, or can be a tuple
to represent a point or a box. For example:

```default
class ZipcodeFeed(Feed):
    def geometry(self, obj):
        # Can also return: `obj.poly`, and `obj.poly.centroid`.
        return obj.poly.extent  # tuple like: (X0, Y0, X1, Y1).
```

#### item_geometry(item)

Set this to return the geometry for each *item* in the feed. This can be a
`GEOSGeometry` instance, or a tuple that represents a point coordinate or
bounding box. For example:

```default
class ZipcodeFeed(Feed):
    def item_geometry(self, obj):
        # Returns the polygon.
        return obj.poly
```

### `SyndicationFeed` Subclasses

The following [`django.utils.feedgenerator.SyndicationFeed`](../../utils.md#django.utils.feedgenerator.SyndicationFeed) subclasses
are available:

### *class* GeoRSSFeed

### *class* GeoAtom1Feed

### *class* W3CGeoFeed

#### NOTE
[W3C Geo](https://www.w3.org/2003/01/geo/) formatted feeds only support
[`PointField`](model-api.md#django.contrib.gis.db.models.PointField) geometries.

# Measurement Objects

The [`django.contrib.gis.measure`](#module-django.contrib.gis.measure) module contains objects that allow
for convenient representation of distance and area units of measure. <sup>[1](#id3)</sup>
Specifically, it implements two objects, [`Distance`](#django.contrib.gis.measure.Distance) and
[`Area`](#django.contrib.gis.measure.Area) – both of which may be accessed via the
[`D`](#django.contrib.gis.measure.D) and [`A`](#django.contrib.gis.measure.A) convenience aliases, respectively.

## Example

[`Distance`](#django.contrib.gis.measure.Distance) objects may be instantiated using a keyword argument
indicating the context of the units. In the example below, two different
distance objects are instantiated in units of kilometers (`km`) and miles
(`mi`):

```pycon
>>> from django.contrib.gis.measure import D, Distance
>>> d1 = Distance(km=5)
>>> print(d1)
5.0 km
>>> d2 = D(mi=5)  # `D` is an alias for `Distance`
>>> print(d2)
5.0 mi
```

For conversions, access the preferred unit attribute to get a converted
distance quantity:

```pycon
>>> print(d1.mi)  # Converting 5 kilometers to miles
3.10685596119
>>> print(d2.km)  # Converting 5 miles to kilometers
8.04672
```

Moreover, arithmetic operations may be performed between the distance
objects:

```pycon
>>> print(d1 + d2)  # Adding 5 miles to 5 kilometers
13.04672 km
>>> print(d2 - d1)  # Subtracting 5 kilometers from 5 miles
1.89314403881 mi
```

Two [`Distance`](#django.contrib.gis.measure.Distance) objects multiplied together will yield an [`Area`](#django.contrib.gis.measure.Area)
object, which uses squared units of measure:

```pycon
>>> a = d1 * d2  # Returns an Area object.
>>> print(a)
40.2336 sq_km
```

To determine what the attribute abbreviation of a unit is, the `unit_attname`
class method may be used:

```pycon
>>> print(Distance.unit_attname("US Survey Foot"))
survey_ft
>>> print(Distance.unit_attname("centimeter"))
cm
```

<a id="supported-units"></a>

## Supported units

| Unit Attribute                  | Full name or alias(es)               |
|---------------------------------|--------------------------------------|
| `km`                            | Kilometre, Kilometer                 |
| `mi`                            | Mile                                 |
| `m`                             | Meter, Metre                         |
| `yd`                            | Yard                                 |
| `ft`                            | Foot, Foot (International)           |
| `survey_ft`                     | U.S. Foot, US survey foot            |
| `inch`                          | Inches                               |
| `cm`                            | Centimeter                           |
| `mm`                            | Millimetre, Millimeter               |
| `um`                            | Micrometer, Micrometre               |
| `british_ft`                    | British foot (Sears 1922)            |
| `british_yd`                    | British yard (Sears 1922)            |
| `british_chain_sears`           | British chain (Sears 1922)           |
| `indian_yd`                     | Indian yard, Yard (Indian)           |
| `sears_yd`                      | Yard (Sears)                         |
| `clarke_ft`                     | Clarke’s Foot                        |
| `chain`                         | Chain                                |
| `chain_benoit`                  | Chain (Benoit)                       |
| `chain_sears`                   | Chain (Sears)                        |
| `british_chain_benoit`          | British chain (Benoit 1895 B)        |
| `british_chain_sears_truncated` | British chain (Sears 1922 truncated) |
| `gold_coast_ft`                 | Gold Coast foot                      |
| `link`                          | Link                                 |
| `link_benoit`                   | Link (Benoit)                        |
| `link_sears`                    | Link (Sears)                         |
| `clarke_link`                   | Clarke’s link                        |
| `fathom`                        | Fathom                               |
| `rod`                           | Rod                                  |
| `furlong`                       | Furlong, Furrow Long                 |
| `nm`                            | Nautical Mile                        |
| `nm_uk`                         | Nautical Mile (UK)                   |
| `german_m`                      | German legal metre                   |

#### NOTE
[`Area`](#django.contrib.gis.measure.Area) attributes are the same as [`Distance`](#django.contrib.gis.measure.Distance) attributes,
except they are prefixed with `sq_` (area units are square in nature).
For example, `Area(sq_m=2)` creates an [`Area`](#django.contrib.gis.measure.Area) object
representing two square meters.

In addition to unit with the `sq_` prefix, the following units are also
supported on [`Area`](#django.contrib.gis.measure.Area):

| Unit Attribute   | Full name or alias(es)   |
|------------------|--------------------------|
| `ha`             | Hectare                  |

## Measurement API

### `Distance`

### *class* Distance(\*\*kwargs)

To initialize a distance object, pass in a keyword corresponding to the
desired [unit attribute name](#supported-units) set with desired
value. For example, the following creates a distance object representing 5
miles:

```pycon
>>> dist = Distance(mi=5)
```

#### \_\_getattr_\_(unit_att)

Returns the distance value in units corresponding to the given unit
attribute. For example:

```pycon
>>> print(dist.km)
8.04672
```

#### *classmethod* unit_attname(unit_name)

Returns the distance unit attribute name for the given full unit name. For
example:

```pycon
>>> Distance.unit_attname("Mile")
'mi'
```

### *class* D

Alias for [`Distance`](#django.contrib.gis.measure.Distance) class.

### `Area`

### *class* Area(\*\*kwargs)

To initialize an area object, pass in a keyword corresponding to the
desired [unit attribute name](#supported-units) set with desired
value. For example, the following creates an area object representing 5
square miles:

```pycon
>>> a = Area(sq_mi=5)
```

#### \_\_getattr_\_(unit_att)

Returns the area value in units corresponding to the given unit attribute.
For example:

```pycon
>>> print(a.sq_km)
12.949940551680001
```

#### *classmethod* unit_attname(unit_name)

Returns the area unit attribute name for the given full unit name. For
example:

```pycon
>>> Area.unit_attname("Kilometer")
'sq_km'
```

### *class* A

Alias for [`Area`](#django.contrib.gis.measure.Area) class.

### Footnotes

* <a id='id3'>**[1]**</a> [Robert Coup](https://koordinates.com/) is the initial author of the measure objects, and was inspired by Brian Beck’s work in [geopy](https://github.com/geopy/geopy/) and Geoff Biggs’ PhD work on dimensioned units for robotics.

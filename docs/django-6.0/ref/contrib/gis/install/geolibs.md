# Installing Geospatial libraries

<a id="geolibs-list"></a>

## Geospatial libraries

GeoDjango uses and/or provides interfaces for the following open source
geospatial libraries:

| Program                                          | Description                         | Required                         | Supported Versions                                  |
|--------------------------------------------------|-------------------------------------|----------------------------------|-----------------------------------------------------|
| [GEOS](../geos.md#geos-overview)                 | Geometry Engine Open Source         | Yes                              | 3.14, 3.13, 3.12, 3.11, 3.10, 3.9                   |
| [PROJ](https://proj.org/)                        | Cartographic Projections library    | Yes (PostgreSQL and SQLite only) | 9.x, 8.x, 7.x, 6.x                                  |
| [GDAL](../gdal.md#gdal-overview)                 | Geospatial Data Abstraction Library | Yes                              | 3.12, 3.11, 3.10, 3.9, 3.8, 3.7, 3.6, 3.5, 3.4, 3.3 |
| [GeoIP](../geoip2.md#geoip2-overview)            | IP-based geolocation library        | No                               | 2                                                   |
| [PostGIS](https://postgis.net/)                  | Spatial extensions for PostgreSQL   | Yes (PostgreSQL only)            | 3.6, 3.5, 3.4, 3.3, 3.2                             |
| [SpatiaLite](https://www.gaia-gis.it/gaia-sins/) | Spatial extensions for SQLite       | Yes (SQLite only)                | 5.1, 5.0, 4.3                                       |

Note that older or more recent versions of these libraries *may* also work
totally fine with GeoDjango. Your mileage may vary.

<!-- Libs release dates:
GEOS 3.9.0 2020-12-14
GEOS 3.10.0 2021-10-20
GEOS 3.11.0 2022-07-01
GEOS 3.12.0 2023-06-27
GEOS 3.13.0 2024-09-06
GEOS 3.14.0 2025-08-21
GDAL 3.3.0 2021-05-03
GDAL 3.4.0 2021-11-04
GDAL 3.5.0 2022-05-13
GDAL 3.6.0 2022-11-03
GDAL 3.7.0 2023-05-10
GDAL 3.8.0 2023-11-13
GDAL 3.9.0 2024-05-10
GDAL 3.10.0 2024-11-06
GDAL 3.11.0 2025-05-09
GDAL 3.12.0 2025-11-07
PostGIS 3.2.0 2021-12-18
PostGIS 3.3.0 2022-08-27
PostGIS 3.4.0 2023-08-15
PostGIS 3.5.0 2024-09-25
PostGIS 3.6.0 2025-09-02
PROJ 9.0.0 2022-03-01
PROJ 8.0.0 2021-03-01
PROJ 8.0.0 2021-03-01
PROJ 7.0.0 2020-02-25
PROJ 6.0.0 2019-02-26
SpatiaLite 4.3.0 2015-09-07
SpatiaLite 5.0.0 2020-08-23
SpatiaLite 5.1.0 2023-08-04 -->

#### NOTE
The GeoDjango interfaces to GEOS, GDAL, and GeoIP may be used
independently of Django. In other words, no database or settings file
required – import them as normal from [`django.contrib.gis`](../index.md#module-django.contrib.gis).

On Debian/Ubuntu, you are advised to install the following packages which will
install, directly or by dependency, the required geospatial libraries:

```console
$ sudo apt-get install binutils libproj-dev gdal-bin
```

Please also consult platform-specific instructions if you are on [macOS](index.md#macos)
or [Windows](index.md#windows).

<a id="build-from-source"></a>

## Building from source

When installing from source on UNIX and GNU/Linux systems, please follow
the installation instructions carefully, and install the libraries in the
given order. If using MySQL or Oracle as the spatial database, only GEOS
is required.

#### NOTE
On Linux platforms, it may be necessary to run the `ldconfig` command
after installing each library. For example:

```shell
$ sudo make install
$ sudo ldconfig
```

#### NOTE
macOS users must install [Xcode](https://developer.apple.com/xcode/) in order to compile software from source.

<a id="geosbuild"></a>

### GEOS

GEOS is a C++ library for performing geometric operations, and is the default
internal geometry representation used by GeoDjango (it’s behind the “lazy”
geometries). Specifically, the C API library is called (e.g., `libgeos_c.so`)
directly from Python using ctypes.

First, download GEOS from the GEOS website and untar the source archive:

```shell
$ wget https://download.osgeo.org/geos/geos-X.Y.Z.tar.bz2
$ tar xjf geos-X.Y.Z.tar.bz2
```

Then step into the GEOS directory, create a `build` folder, and step into
it:

```shell
$ cd geos-X.Y.Z
$ mkdir build
$ cd build
```

Then build and install the package:

```shell
$ cmake -DCMAKE_BUILD_TYPE=Release ..
$ cmake --build .
$ sudo cmake --build . --target install
```

#### Troubleshooting

##### Can’t find GEOS library

When GeoDjango can’t find GEOS, this error is raised:

```text
ImportError: Could not find the GEOS library (tried "geos_c"). Try setting GEOS_LIBRARY_PATH in your settings.
```

The most common solution is to properly configure your [Library environment settings](index.md#libsettings) *or*
set [GEOS_LIBRARY_PATH](#geoslibrarypath) in your settings.

If using a binary package of GEOS (e.g., on Ubuntu), you may need to
[Install binutils](index.md#binutils).

<a id="geoslibrarypath"></a>

##### `GEOS_LIBRARY_PATH`

If your GEOS library is in a non-standard location, or you don’t want to
modify the system’s library path then the [`GEOS_LIBRARY_PATH`](../geos.md#std-setting-GEOS_LIBRARY_PATH)
setting may be added to your Django settings file with the full path to the
GEOS C library. For example:

```shell
GEOS_LIBRARY_PATH = '/home/bob/local/lib/libgeos_c.so'
```

#### NOTE
The setting must be the *full* path to the **C** shared library; in
other words you want to use `libgeos_c.so`, not `libgeos.so`.

See also [My logs are filled with GEOS-related errors](../geos.md#geos-exceptions-in-logfile).

<a id="proj4"></a>

### PROJ

[PROJ](https://proj.org/) is a library for converting geospatial data to different coordinate
reference systems.

First, download the PROJ source code:

```shell
$ wget https://download.osgeo.org/proj/proj-X.Y.Z.tar.gz
```

… and datum shifting files (download `proj-datumgrid-X.Y.tar.gz` for
PROJ < 7.x) <sup>[1](#id8)</sup>:

```shell
$ wget https://download.osgeo.org/proj/proj-data-X.Y.tar.gz
```

Next, untar the source code archive, and extract the datum shifting files in
the `data` subdirectory. This must be done *prior* to configuration:

```shell
$ tar xzf proj-X.Y.Z.tar.gz
$ cd proj-X.Y.Z/data
$ tar xzf ../../proj-data-X.Y.tar.gz
$ cd ../..
```

For PROJ 9.x and greater, releases only support builds using `CMake` (see
[PROJ RFC-7](https://proj.org/community/rfc/rfc-7.html#rfc7)).

To build with `CMake` ensure your system meets the [build requirements](https://proj.org/install.html#build-requirements).
Then create a `build` folder in the PROJ directory, and step into it:

```shell
$ cd proj-X.Y.Z
$ mkdir build
$ cd build
```

Finally, configure, make and install PROJ:

```shell
$ cmake ..
$ cmake --build .
$ sudo cmake --build . --target install
```

<a id="gdalbuild"></a>

### GDAL

[GDAL](https://gdal.org/) is an excellent open source geospatial library that has support for
reading most vector and raster spatial data formats. Currently, GeoDjango only
supports [GDAL’s vector data](../gdal.md#gdal-vector-data) capabilities <sup>[2](#id9)</sup>.
[GEOS](#geosbuild) and [PROJ](#proj4) should be installed prior to building GDAL.

First download the latest GDAL release version and untar the archive:

```shell
$ wget https://download.osgeo.org/gdal/X.Y.Z/gdal-X.Y.Z.tar.gz
$ tar xzf gdal-X.Y.Z.tar.gz
```

For GDAL 3.6.x and greater, releases only support builds using `CMake`. To
build with `CMake` create a `build` folder in the GDAL directory, and step
into it:

```shell
$ cd gdal-X.Y.Z
$ mkdir build
$ cd build
```

Finally, configure, make and install GDAL:

```shell
$ cmake -DCMAKE_BUILD_TYPE=Release ..
$ cmake --build .
$ sudo cmake --build . --target install
```

If you have any problems, please see the troubleshooting section below for
suggestions and solutions.

<a id="gdaltrouble"></a>

#### Troubleshooting

##### Can’t find GDAL library

When GeoDjango can’t find the GDAL library, configure your [Library environment settings](index.md#libsettings)
*or* set [GDAL_LIBRARY_PATH](#gdallibrarypath) in your settings.

<a id="gdallibrarypath"></a>

##### `GDAL_LIBRARY_PATH`

If your GDAL library is in a non-standard location, or you don’t want to
modify the system’s library path then the [`GDAL_LIBRARY_PATH`](../gdal.md#std-setting-GDAL_LIBRARY_PATH)
setting may be added to your Django settings file with the full path to
the GDAL library. For example:

```shell
GDAL_LIBRARY_PATH = '/home/sue/local/lib/libgdal.so'
```

### Footnotes

* <a id='id8'>**[1]**</a> The datum shifting files are needed for converting data to and from certain projections. For example, the PROJ string for the [Google projection (900913 or 3857)](https://spatialreference.org/ref/epsg/3857/) requires the `null` grid file only included in the extra datum shifting files. It is easier to install the shifting files now, then to have debug a problem caused by their absence later.
* <a id='id9'>**[2]**</a> Specifically, GeoDjango provides support for the [OGR](https://gdal.org/user/vector_data_model.html) library, a component of GDAL.

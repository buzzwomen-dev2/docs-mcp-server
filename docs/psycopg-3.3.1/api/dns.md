# `_dns` – DNS resolution utilities

This module contains a few experimental utilities to interact with the DNS
server before performing a connection.

#### WARNING
This module is experimental and its interface could change in the future,
without warning or respect for the version scheme. It is provided here to
allow experimentation before making it more stable.

#### WARNING
This module depends on the [dnspython](https://dnspython.readthedocs.io/) package. The package is currently
not installed automatically as a Psycopg dependency and must be installed
manually:

```sh
$ pip install "dnspython >= 2.1"
```

### psycopg._dns.resolve_srv(params)

Apply SRV DNS lookup as defined in [**RFC 2782**](https://datatracker.ietf.org/doc/html/rfc2782.html).

* **Parameters:**
  **params** (`dict`) – The input parameters, for instance as returned by
  [`conninfo_to_dict()`](conninfo.md#psycopg.conninfo.conninfo_to_dict).
* **Returns:**
  An updated list of connection parameters.

For every host defined in the `params["host"]` list (comma-separated),
perform SRV lookup if the host is in the form `_Service._Proto.Target`.
If lookup is successful, return a params dict with hosts and ports replaced
with the looked-up entries.

Raise [`OperationalError`](errors.md#psycopg.OperationalError) if no lookup is successful and no host
(looked up or unchanged) could be returned.

In addition to the rules defined by RFC 2782 about the host name pattern,
perform SRV lookup also if the the port is the string `SRV` (case
insensitive).

#### WARNING
This is an experimental functionality.

#### NOTE
One possible way to use this function automatically is to subclass
[`Connection`](connections.md#psycopg.Connection), extending the
[`_get_connection_params()`](#psycopg.Connection._get_connection_params) method:

```default
import psycopg._dns  # not imported automatically

class SrvCognizantConnection(psycopg.Connection):
    @classmethod
    def _get_connection_params(cls, conninfo, **kwargs):
        params = super()._get_connection_params(conninfo, **kwargs)
        params = psycopg._dns.resolve_srv(params)
        return params

# The name will be resolved to db1.example.com
cnn = SrvCognizantConnection.connect("host=_postgres._tcp.db.psycopg.org")
```

### *async* psycopg._dns.resolve_srv_async(params)

Async equivalent of [`resolve_srv()`](#psycopg._dns.resolve_srv).

#### *classmethod* Connection.\_get_connection_params(conninfo: [str](https://docs.python.org/3/library/stdtypes.html#str), \*\*kwargs: [Any](https://docs.python.org/3/library/typing.html#typing.Any)) → [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)]

Manipulate connection parameters before connecting.

#### WARNING
This is an experimental method.

This method is a subclass hook allowing to manipulate the connection
parameters before performing the connection. Make sure to call the
`super()` implementation before further manipulation of the arguments:

```default
@classmethod
def _get_connection_params(cls, conninfo, **kwargs):
    params = super()._get_connection_params(conninfo, **kwargs)
    # do something with the params
    return params
```

#### *async classmethod* AsyncConnection.\_get_connection_params(conninfo: [str](https://docs.python.org/3/library/stdtypes.html#str), \*\*kwargs: [Any](https://docs.python.org/3/library/typing.html#typing.Any)) → [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str) | [int](https://docs.python.org/3/library/functions.html#int) | [None](https://docs.python.org/3/library/constants.html#None)]

Manipulate connection parameters before connecting.

#### WARNING
This is an experimental method.

### *async* psycopg._dns.resolve_hostaddr_async(params)

Perform async DNS lookup of the hosts and return a new params dict.

#### Deprecated
Deprecated since version 3.1: The use of this function is not necessary anymore, because
[`psycopg.AsyncConnection.connect()`](connections.md#psycopg.AsyncConnection.connect) performs non-blocking name
resolution automatically.

* **Parameters:**
  **params** (`dict`) – The input parameters, for instance as returned by
  [`conninfo_to_dict()`](conninfo.md#psycopg.conninfo.conninfo_to_dict).

If a `host` param is present but not `hostname`, resolve the host
addresses dynamically.

The function may change the input `host`, `hostname`, `port` to allow
connecting without further DNS lookups, eventually removing hosts that are
not resolved, keeping the lists of hosts and ports consistent.

Raise [`OperationalError`](errors.md#psycopg.OperationalError) if connection is not possible (e.g. no
host resolve, inconsistent lists length).

See [the PostgreSQL docs](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS) for explanation of how these params are used,
and how they support multiple entries.

#### WARNING
Before psycopg 3.1, this function doesn’t handle the `/etc/hosts` file.

#### NOTE
Starting from psycopg 3.1, a similar operation is performed
automatically by `AsyncConnection._get_connection_params()`, so this
function is unneeded.

In psycopg 3.0, one possible way to use this function automatically is
to subclass [`AsyncConnection`](connections.md#psycopg.AsyncConnection), extending the
[`_get_connection_params()`](#psycopg.AsyncConnection._get_connection_params) method:

```default
import psycopg._dns  # not imported automatically

class AsyncDnsConnection(psycopg.AsyncConnection):
    @classmethod
    async def _get_connection_params(cls, conninfo, **kwargs):
        params = await super()._get_connection_params(conninfo, **kwargs)
        params = await psycopg._dns.resolve_hostaddr_async(params)
        return params
```

# How to make a psycopg release

- Check if there is a new version or [libpq](https://www.postgresql.org/ftp/source/) or [OpenSSL](https://www.openssl.org/source/); in such case
  update `LIBPQ_VERSION` and/or `OPENSSL_VERSION` in
  `.github/workflows/packages-bin.yml`.
- Check if there is a new [cibuildwheel release](https://github.com/pypa/cibuildwheel/releases); if so, upgrade it in
  `.github/workflows/packages-bin.yml`.
- Use `tools/bump_version.py` to upgrade package version numbers.
- Push to GitHub to run [the tests workflow](https://github.com/psycopg/psycopg/actions/workflows/tests.yml).
- Build the packages by triggering manually the ones requested among:
  - [Source packages](https://github.com/psycopg/psycopg/actions/workflows/packages-src.yml)
  - [Binary packages](https://github.com/psycopg/psycopg/actions/workflows/packages-bin.yml)
  - [Pool packages](https://github.com/psycopg/psycopg/actions/workflows/packages-pool.yml)
- Delete the `wheelhouse` directory if there is one.
- If all packages were built ok, push the new tag created by `bump_version.py`:
  ```default
  git push --tags
  ```
- Download the `artifacts.zip` package from the last Packages workflow run.
- Unpack the packages in the wheelhouse dir:
  ```default
  mkdir -p wheelhouse
  cd wheelhouse
  unzip ~/Downloads/artifact.zip
  ```
- If the package is a testing one, upload it on TestPyPI with:
  ```default
  $ twine upload -r testpypi *
  ```
- If the package is stable, omit `-r testpypi`:
  ```default
  $ twine upload *
  ```
- Run `tools/bump_version.py -l dev` to bump to the next dev version.

## When a new PostgreSQL major version is released

- Add the new version to `tools/update_errors.py` and run the script to add
  new error classes.
- If the script above found any change, document the version added at the
  bottom of `docs/api/errors.rst`.
- Run the script `tools/update_oids.py` to add new oids. Use `-h` to get
  an example docker command line to run a server locally.
- Check if there are new enum values to include in:
  - `psycopg_c/psycopg_c/pq/libpq.pxd`;
  - `psycopg/psycopg/pq/_enums.py`.
- Include the new version in GitHub Actions test and package grids.
- Bump `PG_VERSION` in the `macos` job of
  - `.github/workflows/packages-bin.yml`.
  - `.github/workflows/tests.yml`.
- Update the documented versions in:
  - `docs/basic/install.rst`;
  - `content/features/contents.lr` in the psycopg-website repository.

### Adding new libpq wrapper methods

The `psycopg.pq` module is a thin wrapper around the libpq, only doing the
minimal work to make the library somewhat Pythonic (e.g. converting types and
raising exceptions instead of returning error values).

When new functionalities are added to the libpq we often want to expose them
to Python (either to allow Python users to use them directly or to build new
features on top of them). The procedure touches several files, in order to
add function wrappers to both the Python and the C implementation of the
libpq, to the objects interfaces and every object implementing them, and
eventually to bubble up to some Python object.

It is polite to add new top-level objects interfaces (such as
`connection.info` or `Capabilities` only on minor releases (3.x), but if
we need to add a libpq function wrapper to solve an issue we can do it in a
bugfix release, without documenting it (e.g. `PQconnectionUsedGSSAPI` was
added in 3.2.10 but only advertised in 3.3).

You can use [PR 1140](https://github.com/psycopg/psycopg/pull/1140/) as a reference for the work to do (code, tests,
documentation). In this MR, the changes in the first commit are suitable to
introduce a new function in a bugfix release, the second commit changes make
the new functionality public.

## When a new Python major version is released

- Add the new version to the relevant test matrices in
  `.github/workflows/tests.yml` and `.github/workflows/packages-bin.yml`.
- Update `docs/basic/install.rst` with the correct range of supported Python
  versions.
- Add the `Programming Language :: Python :: 3.<X>` classifier to
  `psycopg/pyproject.toml`, `psycopg_c/pyproject.toml`, and
  `psycopg_pool/pyproject.toml`.

## When dropping end-of-life Python versions

- Update project metadata, `requires-python` and (maybe) package dependencies
  in `pyproject.toml` files of the corresponding `psycopg` directories.
- Update GitHub Actions workflow files in the `.github/workflows/` directory,
  e.g., `tests.yml`, `.3rd-party-tests.yml`, `packages-bin.yml`.
- Bump versions in the `tests/constraints.txt` file if it is necessary.
- bump `build-system.requires` in `*/pyproject.toml`. Install the packages
  with `pip install ./psycopg*/` and check eventual warnings.
- You may grep throughout the project for occurrences of a version to be dropped.
  However, favouring smaller pull requests is convenient and easy to review.
  An example for grepping `end-of-life` Python 3.8:
  ```default
  git grep -E -e '\b3\.8\b' -e '\b(cp)?38\b' -e '\b3, 8\b'
  git grep -E -e '\b3\.9\b' -e '\b(cp)?39\b' -e '\b3, 9\b'
  ```
- Consider using [pyupgrade](https://pypi.org/project/pyupgrade/) with `--py3NN-plus` in order to refresh syntax
  to Python 3.NN (the new minimum supported version).

Examples:

- [PR #977](https://github.com/psycopg/psycopg/pull/977)

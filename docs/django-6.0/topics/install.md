# How to install Django

This document will get you up and running with Django.

## Install Python

Django is a Python web framework. See [What Python version can I use with Django?](../faq/install.md#faq-python-version-support) for
details.

Get the latest version of Python at [https://www.python.org/downloads/](https://www.python.org/downloads/) or with
your operating system’s package manager.

## Install Apache and `mod_wsgi`

If you just want to experiment with Django, skip ahead to the next
section; Django includes a lightweight web server you can use for
testing, so you won’t need to set up Apache until you’re ready to
deploy Django in production.

If you want to use Django on a production site, use [Apache](https://httpd.apache.org/) with
[mod_wsgi](https://modwsgi.readthedocs.io/en/develop/). mod_wsgi operates in one of two modes: embedded
mode or daemon mode. In embedded mode, mod_wsgi is similar to
mod_perl – it embeds Python within Apache and loads Python code into
memory when the server starts. Code stays in memory throughout the
life of an Apache process, which leads to significant performance
gains over other server arrangements. In daemon mode, mod_wsgi spawns
an independent daemon process that handles requests. The daemon
process can run as a different user than the web server, possibly
leading to improved security. The daemon process can be restarted
without restarting the entire Apache web server, possibly making
refreshing your codebase more seamless. Consult the mod_wsgi
documentation to determine which mode is right for your setup. Make
sure you have Apache installed with the mod_wsgi module activated.
Django will work with any version of Apache that supports mod_wsgi.

See [How to use Django with mod_wsgi](../howto/deployment/wsgi/modwsgi.md)
for information on how to configure mod_wsgi once you have it
installed.

If you can’t use mod_wsgi for some reason, fear not: Django supports many other
deployment options. One is [uWSGI](../howto/deployment/wsgi/uwsgi.md); it
works very well with [nginx](https://nginx.org/). Additionally, Django follows the WSGI spec
([**PEP 3333**](https://peps.python.org/pep-3333/)), which allows it to run on a variety of server platforms.

<a id="database-installation"></a>

## Get your database running

If you plan to use Django’s database API functionality, you’ll need to make
sure a database server is running. Django supports many different database
servers and is officially supported with [PostgreSQL](https://www.postgresql.org/), [MariaDB](https://mariadb.org/), [MySQL](https://www.mysql.com/), [Oracle](https://www.oracle.com/)
and [SQLite](https://www.sqlite.org/).

If you are developing a small project or something you don’t plan to deploy in
a production environment, SQLite is generally the best option as it doesn’t
require running a separate server. However, SQLite has many differences from
other databases, so if you are working on something substantial, it’s
recommended to develop with the same database that you plan on using in
production.

In addition to the officially supported databases, there are [backends
provided by 3rd parties](../ref/databases.md#third-party-notes) that allow you to use other
databases with Django.

To use another database other than SQLite, you’ll need to make sure that the
appropriate Python database bindings are installed:

* If you’re using PostgreSQL, you’ll need the [psycopg](https://www.psycopg.org/psycopg3/) or [psycopg2](https://www.psycopg.org/)
  package. Refer to the [PostgreSQL notes](../ref/databases.md#postgresql-notes) for further
  details.
* If you’re using MySQL or MariaDB, you’ll need a [DB API driver](../ref/databases.md#mysql-db-api-drivers) like `mysqlclient`. See [notes for the MySQL
  backend](../ref/databases.md#mysql-notes) for details.
* If you’re using SQLite you might want to read the [SQLite backend notes](../ref/databases.md#sqlite-notes).
* If you’re using Oracle, you’ll need to install [oracledb](https://oracle.github.io/python-oracledb/), but please read the
  [notes for the Oracle backend](../ref/databases.md#oracle-notes) for details regarding
  supported versions of both Oracle and `oracledb`.
* If you’re using an unofficial 3rd party backend, please consult the
  documentation provided for any additional requirements.

And ensure that the following keys in the `'default'` item of the
[`DATABASES`](../ref/settings.md#std-setting-DATABASES) dictionary match your database connection settings:

* [`ENGINE`](../ref/settings.md#std-setting-DATABASE-ENGINE) – Either
  `'django.db.backends.sqlite3'`,
  `'django.db.backends.postgresql'`,
  `'django.db.backends.mysql'`, or
  `'django.db.backends.oracle'`. Other backends are [also available](../ref/databases.md#third-party-notes).
* [`NAME`](../ref/settings.md#std-setting-NAME) – The name of your database. If you’re using SQLite, the
  database will be a file on your computer. In that case, `NAME` should be
  the full absolute path, including the filename of that file. You don’t need
  to create anything beforehand; the database file will be created
  automatically when needed. The default value, `BASE_DIR / 'db.sqlite3'`,
  will store the file in your project directory.

If you plan to use Django’s `manage.py migrate` command to automatically
create database tables for your models (after first installing Django and
creating a project), you’ll need to ensure that Django has permission to create
and alter tables in the database you’re using; if you plan to manually create
the tables, you can grant Django `SELECT`, `INSERT`, `UPDATE` and
`DELETE` permissions. After creating a database user with these permissions,
you’ll specify the details in your project’s settings file, see
[`DATABASES`](../ref/settings.md#std-setting-DATABASES) for details.

If you’re using Django’s [testing framework](testing/index.md) to
test database queries, Django will need permission to create a test database.

<a id="install-django-code"></a>

## Install the Django code

Installation instructions are slightly different depending on whether you’re
installing a distribution-specific package, downloading the latest official
release, or fetching the latest development version.

<a id="installing-official-release"></a>

### Installing an official release with `pip`

This is the recommended way to install Django.

1. Install [pip](https://pip.pypa.io/). The easiest is to use the [standalone pip installer](https://pip.pypa.io/en/latest/installation/). If your
   distribution already has `pip` installed, you might need to update it if
   it’s outdated. If it’s outdated, you’ll know because installation won’t
   work.
2. Take a look at [venv](https://docs.python.org/3/tutorial/venv.html). This tool provides
   isolated Python environments, which are more practical than installing
   packages systemwide. It also allows installing packages without
   administrator privileges. The [contributing tutorial](../intro/contributing.md) walks through how to create a virtual environment.
3. After you’ve created and activated a virtual environment, enter the command:
   ```console
   $ python -m pip install Django
   ```

<a id="installing-distribution-package"></a>

### Installing a distribution-specific package

Check the [distribution specific notes](../misc/distributions.md) to see if
your platform/distribution provides official Django packages/installers.
Distribution-provided packages will typically allow for automatic installation
of dependencies and supported upgrade paths; however, these packages will
rarely contain the latest release of Django.

<a id="installing-development-version"></a>

### Installing the development version

If you’d like to be able to update your Django code occasionally with the
latest bug fixes and improvements, follow these instructions:

1. Make sure that you have [Git](https://git-scm.com/) installed and that you can run its commands
   from a shell. (Enter `git help` at a shell prompt to test this.)
2. Check out Django’s main development branch like so:
   ```console
   $ git clone https://github.com/django/django.git
   ```

   This will create a directory `django` in your current directory.
3. Make sure that the Python interpreter can load Django’s code. The most
   convenient way to do this is to use a virtual environment and [pip](https://pip.pypa.io/). The
   [contributing tutorial](../intro/contributing.md) walks through how to
   create a virtual environment.
4. After setting up and activating the virtual environment, run the following
   command:
   ```console
   $ python -m pip install -e django/
   ```

   This will make Django’s code importable, and will also make the
   `django-admin` utility command available. In other words, you’re all
   set!

When you want to update your copy of the Django source code, run the command
`git pull` from within the `django` directory. When you do this, Git will
download any changes.

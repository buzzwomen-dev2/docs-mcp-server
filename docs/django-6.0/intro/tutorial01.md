# Writing your first Django app, part 1

Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a basic
poll application.

It’ll consist of two parts:

* A public site that lets people view polls and vote in them.
* An admin site that lets you add, change, and delete polls.

We’ll assume you have [Django installed](install.md) already. You can
tell Django is installed and which version by running the following command
in a shell prompt (indicated by the $ prefix):

```console
$ python -m django --version
```

If Django is installed, you should see the version of your installation. If it
isn’t, you’ll get an error telling “No module named django”.

This tutorial is written for Django 6.1, which supports Python 3.12 and
later. If the Django version doesn’t match, you can refer to the tutorial for
your version of Django by using the version switcher at the bottom right corner
of this page, or update Django to the newest version. If you’re using an older
version of Python, check [What Python version can I use with Django?](../faq/install.md#faq-python-version-support) to find a compatible
version of Django.

## Creating a project

If this is your first time using Django, you’ll have to take care of some
initial setup. Namely, you’ll need to auto-generate some code that establishes
a Django [project](../glossary.md#term-project) – a collection of settings for an instance of Django,
including database configuration, Django-specific options and
application-specific settings.

From the command line, `cd` into a directory where you’d like to store your
code and run the following command to bootstrap a new Django project:

```console
$ django-admin startproject mysite djangotutorial
```

This will create a directory `djangotutorial` with a project called
`mysite` inside. The directory name doesn’t matter to Django; you can rename
it to anything you like. If it didn’t work, see
[Problems running django-admin](../faq/troubleshooting.md#troubleshooting-django-admin).

#### NOTE
You’ll need to avoid naming projects after built-in Python or Django
components. In particular, this means you should avoid using names like
`django` (which will conflict with Django itself) or `test` (which
conflicts with a built-in Python package).

Let’s look at what [`startproject`](../ref/django-admin.md#django-admin-startproject) created:

```text
djangotutorial/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py
```

These files are:

* `manage.py`: A command-line utility that lets you interact with this
  Django project in various ways. You can read all the details about
  `manage.py` in [django-admin and manage.py](../ref/django-admin.md).
* `mysite/`: A directory that is the actual Python package for your
  project. Its name is the Python package name you’ll need to use to import
  anything inside it (e.g. `mysite.urls`).
* `mysite/__init__.py`: An empty file that tells Python that this
  directory should be considered a Python package. If you’re a Python beginner,
  read [more about packages](https://docs.python.org/3/tutorial/modules.html#tut-packages) in the official Python docs.
* `mysite/settings.py`: Settings/configuration for this Django
  project. [Django settings](../topics/settings.md) will tell you all about how settings
  work.
* `mysite/urls.py`: The URL declarations for this Django project; a
  “table of contents” of your Django-powered site. You can read more about
  URLs in [URL dispatcher](../topics/http/urls.md).
* `mysite/asgi.py`: An entry-point for ASGI-compatible web servers to
  serve your project. See [How to deploy with ASGI](../howto/deployment/asgi/index.md) for more details.
* `mysite/wsgi.py`: An entry-point for WSGI-compatible web servers to
  serve your project. See [How to deploy with WSGI](../howto/deployment/wsgi/index.md) for more details.

## The development server

Let’s verify your Django project works. Change into the `djangotutorial`
directory, if you haven’t already, and run the following commands:

```console
$ python manage.py runserver
```

You’ll see the following output on the command line:

```default
Performing system checks...

System check identified no issues (0 silenced).

You have unapplied migrations; your app may not work properly until they are
applied. Run 'python manage.py migrate' to apply them.

December 04, 2025 - 15:50:53
Django version 6.1, using settings 'mysite.settings'
Starting development server at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
Quit the server with CONTROL-C.

WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead.
For more information on production servers see: [https://docs.djangoproject.com/en/](https://docs.djangoproject.com/en/)6.1/howto/deployment/
```

#### NOTE
Ignore the warning about unapplied database migrations for now; we’ll deal
with the database shortly.

Now that the server’s running, visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) with your web
browser. You’ll see a “Congratulations!” page, with a rocket taking off.
It worked!

You’ve started the Django development server, a lightweight web server written
purely in Python. We’ve included this with Django so you can develop things
rapidly, without having to deal with configuring a production server – such as
Apache – until you’re ready for production.

Now’s a good time to note: **don’t** use this server in anything resembling a
production environment. It’s intended only for use while developing. (We’re in
the business of making web frameworks, not web servers.)

(To serve the site on a different port, see the [`runserver`](../ref/django-admin.md#django-admin-runserver)
reference.)

## Creating the Polls app

Now that your environment – a “project” – is set up, you’re set to start
doing work.

Each application you write in Django consists of a Python package that follows
a certain convention. Django comes with a utility that automatically generates
the basic directory structure of an app, so you can focus on writing code
rather than creating directories.

Your apps can live anywhere in your [Python path](https://docs.python.org/3/tutorial/modules.html#tut-searchpath). In
this tutorial, we’ll create our poll app inside the `djangotutorial` folder.

To create your app, make sure you’re in the same directory as `manage.py`
and type this command:

```console
$ python manage.py startapp polls
```

That’ll create a directory `polls`, which is laid out like this:

```text
polls/
    __init__.py
    admin.py
    apps.py
    migrations/
        __init__.py
    models.py
    tests.py
    views.py
```

This directory structure will house the poll application.

## Write your first view

Let’s write the first view. Open the file `polls/views.py`
and put the following Python code in it:

```python
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
```

This is the most basic view possible in Django. To access it in a browser, we
need to map it to a URL - and for this we need to define a URL configuration,
or “URLconf” for short. These URL configurations are defined inside each
Django app, and they are Python files named `urls.py`.

To define a URLconf for the `polls` app, create a file `polls/urls.py`
with the following content:

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
```

Your app directory should now look like:

```text
polls/
    __init__.py
    admin.py
    apps.py
    migrations/
        __init__.py
    models.py
    tests.py
    urls.py
    views.py
```

The next step is to configure the root URLconf in the `mysite` project to
include the URLconf defined in `polls.urls`. To do this, add an import for
`django.urls.include` in `mysite/urls.py` and insert an
[`include()`](../ref/urls.md#django.urls.include) in the `urlpatterns` list, so you have:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
]
```

The [`path()`](../ref/urls.md#django.urls.path) function expects at least two arguments:
`route` and `view`.
The [`include()`](../ref/urls.md#django.urls.include) function allows referencing other URLconfs.
Whenever Django encounters [`include()`](../ref/urls.md#django.urls.include), it chops off whatever
part of the URL matched up to that point and sends the remaining string to the
included URLconf for further processing.

The idea behind [`include()`](../ref/urls.md#django.urls.include) is to make it easy to
plug-and-play URLs. Since polls are in their own URLconf
(`polls/urls.py`), they can be placed under “/polls/”, or under
“/fun_polls/”, or under “/content/polls/”, or any other path root, and the
app will still work.

You have now wired an `index` view into the URLconf. Verify it’s working with
the following command:

```console
$ python manage.py runserver
```

Go to [http://localhost:8000/polls/](http://localhost:8000/polls/) in your browser, and you should see the
text “*Hello, world. You’re at the polls index.*”, which you defined in the
`index` view.

When you’re comfortable with the basic request and response flow, read
[part 2 of this tutorial](tutorial02.md) to start working with the
database.

The documentation in this tree is in plain text files and can be viewed using
any text file viewer.

It uses [ReST](https://docutils.sourceforge.io/rst.html) (reStructuredText), and the [Sphinx](https://www.sphinx-doc.org/) documentation system.
This allows it to be built into other forms for easier viewing and browsing.

To create an HTML version of the docs:

* Install Sphinx (using `python -m pip install Sphinx` or some other method).
* In this docs/ directory, type `make html` (or `make.bat html` on
  Windows) at a shell prompt.

The documentation in `_build/html/index.html` can then be viewed in a web
browser.

.. _contributing:

Contributing
############

.. contents::
   :depth: 3
   :local:

Running the Tests
*****************

The Juicer test suite is invoked via the Makefile. The following is an
example of how to run the ``ci`` target manually.

This will install dependencies within an isolated Python `virtualenv
<https://virtualenv.pypa.io/en/latest/>`_. In addition to running our
tests, `PEP8 <http://www.python.org/dev/peps/pep-0008>`_ style
formatting is also checked.


.. showterm:: 7b5f8d42ba021511e627e


Once the command ``make ci`` exits and returns control to the shell we
can scroll up a few lines and review the results of our unit tests and
code-coverage report (move your cursor over the window above and
scroll up/down to see for yourself).


Running Juicer Locally
**********************
Once the ``ci`` Makefile target has been ran, we can enter the python
virtual environment and run ``juicer`` by running the highlighted
commands in the following block.

.. code-block:: console
   :linenos:
   :emphasize-lines: 2, 5

   [~/juicer] 23:30:27  (master)
   $ . juicerenv/bin/activate

   [~/juicer] 23:30:41  (master)
   $ juicer -h
   usage: juicer [-h] [-q] [-v] [-V] {cart,rpm,repo,role,user,hello} ...

   manage pulp and release carts

   optional arguments:
     -h, --help            show this help message and exit
     -q, --quiet           show no output
     -v, --verbose         show verbose output
     -V, --version         show program's version number and exit

   commands:
     'juicer COMMAND -h' for individual help topics

     {cart,rpm,repo,role,user,hello}
     cart                cart operations
     rpm                 rpm operations
     repo                repo operations
     role                role operations
     user                user operations
     hello               test your connection to the pulp server

Code Style and Formatting
*************************

Please conform to :pep:`0008` for code formatting. This specification
outlines the style that is required for patches.

Your code must follow this (or note why it can't) before patches will
be accepted. There is one consistent exception to this rule:

**E501**
   Line too long

   The ``pep8`` tests for juicer include a ``--ignore`` option to
   automatically exclude **E501** errors from the tests.

Argument and Command Style
**************************

Arguments should be expressed as they are in the following
example. Usage strings are all lower case except for argument metavars
which are in caps. Description strings are all lower case.

.. code:: bash

   $ juicer cart create -h
   usage: juicer cart create CARTNAME [-r REPONAME ITEM ... [-r REPONAME ITEM ...]] [-h]

   positional arguments:
   CARTNAME              cart name

   optional arguments:
    -h, --help            show this help message and exit
    -r REPONAME [ITEM ...]
                          destination repo name, items

Output should read as a garden variety sentence.

.. code::

   $ juicer cart create test -r test-repo ~/rpmbuild/RPMS/noarch/*
   Saved cart 'test'


Documentation
*************

I assume you came here to learn how to update the project
documentation?

Hello, you have just become my new best friend. I think we're going to
get along really well together.


Section Headers
===============

When marking up section headers please refer to the `HEADERS
<https://github.com/abutcher/juicer/blob/master/docsite/HEADERS>`_
file in the ``docsite`` directory. This file shows the order we apply
section header markup. Please follow it exactly, doing so will help us
avoid silly rendering errors.

.. literalinclude:: ../HEADERS
   :language: ini


Word Wrapping
=============

**Please do** word-wrap your documentation contributions! In **emacs**
this is as simple as pressing ``M-q`` in a paragraph you want to
auto-word-wrap (the emacs function is called ``fill-paragraph``. You
can run it manually with ``M-x fill-paragraph <RET>`` if you prefer.

If you use **vi(m)**, then I'm sorry. I cannot assist you with your
word-wrapping needs a this time. Please feel free to submit a pull
request to update these docs with vi(m) automatic word-wrapping
instructions!

Fear not -- pull-requests won't be rejected just because they aren't
word-wrapped. You just earn major karma with us if you word-wrap your
contributions :-). Thanks!


Building The Docs
=================

So you want to build the documentation locally? Aren't you in luck, I
think that's a surpurb idea as well. Building the docs is a fairly
straight-forward process. All you **may** have to do is install some
requirements first:

From **yum:**

* ``python-sphinx``
* ``python-sphinx_rtd_theme``

Optionally, you may install these requirements from **pip:**

* ``Sphinx``
* ``sphinx_rtd_theme``

Once you have the requirements installed you can attempt to build the
documentation from source

* Switch into the ``docsite`` directory and run ``make html``:

.. code:: bash

   $ cd ./docsite
   $ make html
   sphinx-build -b html -d build/doctrees   source build/html
   Making output directory...
   Running Sphinx v1.1.3
   loading pickled environment... not yet created
   building [html]: targets for 3 source files that are out of date
   updating environment: 3 added, 0 changed, 0 removed
   reading sources... [100%] index
   looking for now-outdated files... none found
   pickling environment... done
   checking consistency... done
   preparing documents... done
   writing output... [100%] index
   writing additional files... genindex search
   copying static files... done
   dumping search index... done
   dumping object inventory... done
   build succeeded.

   Build finished. The HTML pages are in build/html.

* If the docs built correctly then you can open them in your default
  browser with this command (while still in the ``docsite``
  directory):

.. code:: bash

   $ xdg-open ./build/html/index.html

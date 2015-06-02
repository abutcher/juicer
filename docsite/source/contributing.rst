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

.. code-block:: console
   :linenos:
   :emphasize-lines: 2

   [~/juicer] 23:29:58  (master)
   $ make ci
   sed "s/%VERSION%/1.0.0/" juicer/__init__.py.in > juicer/__init__.py
   #############################################
   # Creating a virtualenv
   #############################################
   virtualenv juicerenv
   New python executable in juicerenv/bin/python2
   Also creating executable in juicerenv/bin/python
   Installing setuptools, pip...done.
   . juicerenv/bin/activate && pip install -r requirements.txt

   ... snip ...

   Verify pulp role create ... ok
   Verify pulp role delete ... ok
   Verify pulp role list ... ok
   Verify pulp role remove_user ... ok
   Verify pulp role show ... ok
   Verify pulp user create ... ok
   Verify pulp user delete ... ok
   Verify pulp user list ... ok
   Verify pulp user show ... ok
   Verify pulp user update ... ok
   Ensure docker image type upload data is sane ... ok
   Ensure RPM type upload data is sane ... ok

   OK
   #############################################
   # UNIT TESTS RAN. HTML CODE COVERAGE RESULTS:
   % xdg-open ./cover/index.html
   #############################################
   :

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

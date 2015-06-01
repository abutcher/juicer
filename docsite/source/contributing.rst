Contributing
############

.. contents::
   :depth: 3
   :local:

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

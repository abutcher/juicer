.. image:: https://api.travis-ci.org/abutcher/juicer.png
   :target: https://travis-ci.org/abutcher/juicer/
   :align: right
   :height: 19
   :width: 77

.. image:: https://readthedocs.org/projects/juicer/badge/?version=latest
   :target: http://juicer.rtfd.org/
   :align: right
   :height: 19
   :width: 77

.. image:: https://coveralls.io/repos/abutcher/juicer/badge.svg?branch=master
   :target: https://coveralls.io/r/abutcher/juicer?branch=master
   :align: right
   :height: 19
   :width: 77

Juicer
######
Juicer is a command-line interface to the `Pulp REST API
<https://pulp.readthedocs.org/en/2.6-release/dev-guide/integration/rest-api/index.html>`_
which provides a shopping cart style approach to uploading and
promoting groups of packages or docker images through multiple
environments.

Documentation
-------------

The main documentation lives at
`http://juicer.readthedocs.org/en/latest/
<http://juicer.readthedocs.org/en/latest/>`_.

Usage
-----

.. code::

   usage: juicer [-h] [-v] [-V] {cart,rpm,repo,role,user,hello} ...

   manage pulp and release carts

   optional arguments:
   -h, --help            show this help message and exit
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

Create a repository
~~~~~~~~~~~~~~~~~~~

Creating a repository without specifying ``--in`` will automatically
create the repository in every configured environment.

.. code:: bash

   juicer repo create my-repository

Or, a repository can be created in specific environments.

.. code:: bash

   juicer repo create my-repository --in devel

.. note::

   Repositories created by juicer have a relative path which includes
   the environments they were created in. If a repository was created
   in ``devel``, it would be available at
   ``https://<pulp-host>/pulp/repos/devel/``.

   The Pulp ``repo_id`` of a repository created by juicer will be
   ``display_name-environment``. A repository named ``test-repo``
   created in the ``devel`` environment would have a ``repo_id`` of
   ``test-repo-devel``.

   This was done so that multiple environments can co-exist on a
   single Pulp node.

Create a cart
~~~~~~~~~~~~~

A cart is composed of repositories and packages.

.. code:: bash

   juicer cart create my-cart -r my-repository ~/rpmbuild/RPMS/noarch/*.rpm

Multiple packages and repositories can be specified.

.. code:: bash

   juicer cart create my-cart -r my-repository ~/rpmbuild/RPMS/noarch/*.rpm \
                              -r my-other-repository ./awesome.rpm /tmp/woah.rpm

Packages don't have to be local.

.. code:: bash

   juicer cart create my-cart -r my-repository http://dang.com/rpms/omg.rpm

Push a cart to an environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   juicer cart push my-cart --in qa

A cart can be saved remotely once it has been pushed. This can be
useful if the release engineer needs to swap mid-release. Add
``cart_seeds`` (insecure mongo endpoint) to juicer configuration to
enable remote saves. Remote carts can be pulled with ``juicer cart
pull``.

.. code:: bash

   juicer cart delete my-cart
   juicer cart pull my-cart
   juicer cart show my-cart

Configuration
-------------
Juicer is configured through a ``~/.config/juicer/config`` file. The
config is broken into sections by environment and may also contain an
optional DEFAULT section, from which the defaults for all following
sections are supplied.

The standard flow of this sample infrastructure goes from devel to
prod; meaning that we upload our packages to devel and test them
accordingly in our development environment before we promote them to
prod.

.. code::

  [DEFAULT]
  username: admin
  password: admin
  port: 443
  verify_ssl: True
  ca_path: /etc/pki/pulp/ca.crt
  cert_filename: /etc/pki/pulp/pulp.crt
  start_in: devel
  cart_seeds: localhost:27017

  [devel]
  hostname: localhost
  promotes_to: qa

  [qa]
  hostname: localhost
  promotes_to: stage

  [stage]
  hostname: localhost
  promotes_to: prod

  [prod]
  hostname: localhost

Installation
------------
Juicer was built to talk to Pulp version 2.6.0. Installation instructions are
available `here <https://pulp.readthedocs.org/en/2.6-release/user-guide/installation.html>`_.

Currently the only supported method is installing from source while
we're under construction.

.. code::

  sudo python ./setup.py install

Running locally
---------------

Run ``make ci`` to install dependencies within your local
checkout. This will create an isolated Python `virtualenv
<https://virtualenv.pypa.io/en/latest/>`_. The ``ci`` Makefile target
also runs our tests and checks `PEP8
<http://www.python.org/dev/peps/pep-0008>`_ style formatting.

.. code::

  make ci

  . juicerenv/bin/activate

  juicer -h

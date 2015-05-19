.. image:: https://api.travis-ci.org/abutcher/juicer.png
   :target: https://travis-ci.org/abutcher/juicer/
   :align: right
   :height: 19
   :width: 77

Juicer
======
Juicer is a command-line interface to the `Pulp REST
API <https://pulp.readthedocs.org/en/2.6-release/dev-guide/integration/rest-api/index.html>`_
which provides a 'shopping cart' style approach to uploading and
promoting groups of packages through multiple environments.

This project is a fork of the original `Juicer
<https://github.com/juicer/juicer>`_ project which I hope to improve
upon by leveraging use of the existing Pulp libraries.

Usage
-----
.. code-block::

  usage: juicer [-h] [-v] [-V] {cart,rpm,repo,role,user,hello} ...

  Manage release carts

  optional arguments:
    -h, --help            show this help message and exit
    -v                    show verbose output
    -V, --version         show program's version number and exit

  Commands:
    'juicer COMMAND -h' for individual help topics

    {cart,rpm,repo,role,user,hello}
     cart                cart operations
     rpm                 rpm operations
     repo                repo operations
     role                role operations
     user                user operations
     hello               test your connection to the pulp server

Installation
------------
Juicer was built to talk to Pulp version 2.6.0. Installation instructions are
available `here <https://pulp.readthedocs.org/en/2.6-release/user-guide/installation.html>`_.

Currently the only supported method is installing from source while
we're under construction.

.. code-block::

  sudo python ./setup.py install

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

.. code-block::

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


Running Locally
---------------

Run ``make ci`` to install dependencies within your local
checkout. This will create an isolated Python `virtualenv
<https://virtualenv.pypa.io/en/latest/>`_. The ``ci`` Makefile target
also runs our tests and checks `PEP8
<http://www.python.org/dev/peps/pep-0008>`_ style formatting.

.. code-block::

  make ci

  . juicerenv/bin/activate

  juicer -h

.. _getting_started:

Getting Started
###############

Installation
------------
Juicer was built to talk to Pulp version 2.6.0. Installation instructions are
available `here <https://pulp.readthedocs.org/en/2.6-release/user-guide/installation.html>`_.

Currently the only supported method is installing from source while
we're under construction.

.. code::

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


.. literalinclude:: ../../config
   :language: ini
   :linenos:


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

You can even provide an apache directory index (example:
`http://lnx.cx/~tbielawa/rpms/ <http://lnx.cx/~tbielawa/rpms/>`_) as a
source. The directory listing will be searched for links ending in
``.rpm``. All matches will be added to the cart!

.. code:: bash

   juicer cart create my-dir-cart -r my-repository http://son.com/rpms/
   juicer cart show my-dir-cart


.. code:: json

   {
       "_id": "my-dir-cart",
       "repos_items": {
           "my-repository": [
               "http://son.com/rpms/megafrobber-1.0.3-2.noarch.rpm",
               "http://son.com/rpms/defrobnicate-ng-3.2.1-0.noarch.rpm",
           ]
       }
   }




Push a cart to an environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pushing a cart will upload all of its items to the specified
environment.

.. code:: bash

   juicer cart push my-cart --in qa

.. note::
   A cart can be saved remotely once it has been pushed. This can be
   useful if the release engineer needs to swap mid-release. Add
   ``cart_seeds`` (insecure mongo endpoint) to juicer configuration to
   enable remote saves. Remote carts can be pulled with ``juicer cart
   pull``.

   To further illustrate remote cart saving, we can delete our local
   cart and pull it down again.

   .. code:: bash

      juicer cart delete my-cart --local
      juicer cart pull my-cart
      juicer cart show my-cart

   ``juicer cart pull`` will overwrite a local cart file if it exists.

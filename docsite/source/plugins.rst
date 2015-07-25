.. _plugins:

Plugins
#######

Juicer will execute pre and post upload plugins if they exist. Example
use cases include signing packages, kicking off builds, or anything
that you'd want to do with a cart's files before and after uploading.

- Plugins are read from ``/usr/share/juicer/plugins/pre`` and
  ``/usr/share/juicer/plugins/post``.
- Plugins must be named after the class they contain.
- Plugins will be passed an ``item_type`` (rpm, docker, or iso), the
  ``environment``, and a list of ``items`` that have already been
  synced to the local filesystem.

An Example Plugin
-----------------

Here is an example plugin stored in
``/usr/share/juicer/plugins/pre/myplugin.py`` that displays each item
and its size.

.. code-block:: python

    import os

    class myplugin:
        def __init__(self, item_type, environment, items):
            self.item_type = item_type
            self.environment = environment
            self.items = items

            def run(self):
                print("Item type: {}".format(self.item_type))
                print("Environment: {}".format(self.environment))
                for item in self.items:
                    print("File: {}, Size: {}".format(item, os.path.getsize(item.path)))

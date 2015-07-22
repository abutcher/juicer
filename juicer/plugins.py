# -*- coding: utf-8 -*-
# Juicer - Administer Pulp and Release Carts
# Copyright © 2015, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import imp
import logging
import os

import juicer.common.Constants


class Plugins(object):
    def __init__(self):
        self.output = logging.getLogger('juicer')
        self.post_plugins = []
        self.pre_plugins = []
        self.load_plugins()

    def load_plugins(self):
        for plugin in os.listdir(juicer.common.Constants.PRE_PLUGIN_DIR):
            name = os.path.splitext(os.path.basename(plugin))[0]
            try:
                mod = imp.load_source(name, juicer.common.Constants.PRE_PLUGIN_DIR + plugin)
                self.pre_plugins.append(getattr(mod, name))
            except:
                self.output.error("Failed to load '{plugin}'".format(plugin=plugin))

        for plugin in os.listdir(juicer.common.Constants.POST_PLUGIN_DIR):
            name = os.path.splitext(os.path.basename(plugin))[0]
            try:
                mod = imp.load_source(name, juicer.common.Constants.POST_PLUGIN_DIR + plugin)
                self.pre_plugins.append(getattr(mod, name))
            except:
                self.output.error("Failed to load '{plugin}'".format(plugin=plugin))

    def execute_pre_plugins(self, items):
        for plugin in self.pre_plugins:
            plugin().run(items)

    def execute_post_plugins(self, items):
        for plugin in self.post_plugins:
            plugin().run(items)

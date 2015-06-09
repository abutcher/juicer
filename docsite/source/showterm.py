#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import re
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive

""" the showterm sphinx extension

* Simple Usage - Embed a video, use all defaults

.. showterm:: 7b5f8d42ba021511e627e

* Custom Usage - Use a private/third-party showterm server

.. showterm:: 7b5f8d42ba021511e627e
   :showterm_url: https://showterm.example.com

* Custom Usage - Specify a width and height

.. showterm:: 7b5f8d42ba021511e627e
   :width: 800
   :height: 600
"""

CONTROL_HEIGHT = 30
# TODO: Make this a configuration parameter!!!!111
# The leading "//" is a shortcut to automatically use the
# protocol which matches the loading pages (https enabled
# documentation will embed the https showterm viewer)
DEFAULT_SHOWTERM_URL = "https://showterm.io"

def showterm_url(baseurl, id, speed=None):
    if speed is not None:
        speed = "#%s" % speed
    else:
        speed = ''
    return "{base}/{id}{speed}".format(
        base=baseurl,
        id=id,
        speed=speed)

def get_size(d, key):
    if key not in d:
        return None
    m = re.match("(\d+)(|%|px)$", d[key])
    if not m:
        raise ValueError("invalid size %r" % d[key])
    return int(m.group(1)), m.group(2) or "px"

def css(d):
    return "; ".join(sorted("%s: %s" % kv for kv in d.iteritems()))

class showterm(nodes.General, nodes.Element): pass

def visit_showterm_node(self, node):
    # aspect = node["aspect"]
    # width = node["width"]
    # height = node["height"]
    showtermurl = node["showtermurl"]
    # speed = node["speed"]

    # if aspect is None:
    #     aspect = 16, 9

    height = '480px'
    width = '640px'

    style = {
        "width": width,
        "height": height,
        "border": "0",
    }
    attrs = {
        "src": showterm_url(showtermurl, node['id'], 'stop'),
        "style": css(style),
        "class": "showterm showterm-%s" % node['id'],
    }
    self.body.append(self.starttag(node, "iframe", **attrs))
    self.body.append("</iframe>")

    # if (height is None) and (width is not None) and (width[1] == "%"):
    #     style = {
    #         "padding-top": "%dpx" % CONTROL_HEIGHT,
    #         "padding-bottom": "%f%%" % (width[0] * aspect[1] / aspect[0]),
    #         "width": "%d%s" % (width,'%'),
    #         "position": "relative",
    #     }
    #     self.body.append(self.starttag(node, "div", style=css(style)))
    #     style = {
    #         "position": "absolute",
    #         "top": "0",
    #         "left": "0",
    #         "width": "100%",
    #         "height": "100%",
    #         "border": "0",
    #     }
    #     attrs = {
    #         "src": showterm_url('lnx.cx', node['id'], 'stop'),
    #         "style": css(style),
    #     }
    #     self.body.append(self.starttag(node, "iframe", **attrs))
    #     self.body.append("</iframe></div>")
    # else:
        # if width is None:
        #     if height is None:
        #         width = 690, "px"
        #     else:
        #         width = height[0] * aspect[0] / aspect[1], "px"
        # if height is None:
        #     height = width[0] * aspect[1] / aspect[0], "px"


def depart_showterm_node(self, node):
    pass

class Showterm(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    # These are the legal options for this directive. Keys are the
    # option names, values are functions which assert a condition the
    # option must meet and which may possibly transform the input
    # value into a an expected Python type.
    #
    # `directives.unchanged` asserts no conditions and performs no
    # transformations, "Returns the text argument, unchanged. Returns
    # an empty string ("") if no argument is found."
    #
    # http://docutils.sourceforge.net/docs/howto/rst-directives.html#option-conversion-functions
    option_spec = {
        # "width": directives.unchanged,
        # "height": directives.unchanged,
        # "aspect": directives.unchanged,
        "showtermurl": directives.unchanged,
        # "speed": directives.unchanged,
    }

    def run(self):
        config = self.state.document.settings.env.config

        # if "aspect" in self.options:
        #     aspect = self.options.get("aspect")
        #     # Ensure the ratio is given in a colon delimited string
        #     m = re.match("(\d+):(\d+)", aspect)
        #     if m is None:
        #         raise ValueError("invalid aspect ratio %r" % aspect)
        #     # The match object broke the aspect string into two parts,
        #     # this makes each part a piece of a 2-tuple. A more
        #     # obvious way to do this might have just been aspect =
        #     # tuple(split(':', aspect)), (but that wasn't my choice)
        #     aspect = tuple(int(x) for x in m.groups())
        # else:

        #     aspect = None

        # width = get_size(self.options, "width")
        # height = get_size(self.options, "height")

        showtermurl = self.options.get("showtermurl", None)

        if showtermurl is None:
            showtermurl = config.showtermurl

        # if "speed" in self.options:
        #     speed = self.options.get("speed")
        #     if speed in ['slow', 'fast', 'stop']:
        #         pass
        #     else:
        #         raise ValueError("invalid speed: %s. Leave empty or choose one of: 'slow','fast', 'stop'")
        # else:
        #     pass

        # return [showterm(id=self.arguments[0], aspect='16:9', width=690, height=400, showtermurl='lnx.cx', speed='stop')]
        return [showterm(id=self.arguments[0], showtermurl=showtermurl)]

def setup(app):
    # Default showterm url, change this if you run your own private
    # showterm server. If the parameter changes between builds then
    # the entire HTML document will be rebuilt
    app.add_config_value('showtermurl', DEFAULT_SHOWTERM_URL, 'html')

    app.add_node(showterm, html=(visit_showterm_node, depart_showterm_node))
    app.add_directive("showterm", Showterm)


    # Leave the speed as 'stop' so people can begin playing the

    # termcaps when they want
    # app.add_config_value('showterm_speed', 'stop', 'html')
    # app.add_config_value('showterm_width', 690, 'html')
    # app.add_config_value('showterm_height', 400, 'html')

    # possible future params:
"""
title - to add a title element
caption - short little bit below the cap
width
height
speed - fast, slow, stop

"""

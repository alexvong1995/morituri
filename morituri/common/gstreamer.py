# -*- Mode: Python; test-case-name: morituri.test.test_common_gstreamer -*-
# vi:si:et:sw=4:sts=4:ts=4

# Morituri - for those about to RIP

# Copyright (C) 2009 Thomas Vander Stichele

# This file is part of morituri.
#
# morituri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# morituri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with morituri.  If not, see <http://www.gnu.org/licenses/>.

import re
import commands

from morituri.common import log

# workaround for issue #64


def removeAudioParsers():
    log.debug('gstreamer', 'Removing buggy audioparsers plugin if needed')

    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    registry = Gst.Registry.get()

    plugin = registry.find_plugin("audioparsersbad")
    if plugin:
        # always remove from bad
        log.debug('gstreamer', 'removing audioparsersbad plugin from registry')
        registry.remove_plugin(plugin)

    plugin = registry.find_plugin("audioparsers")
    if plugin:
        log.debug('gstreamer', 'removing audioparsers plugin from %s %s',
            plugin.get_source(), plugin.get_version())

        # the query bug was fixed after 0.10.30 and before 0.10.31
        # the seek bug is still there though
        # if plugin.get_source() == 'gst-plugins-good' \
        #   and plugin.get_version() > '0.10.30.1':
        #    return

        registry.remove_plugin(plugin)

def gstreamerVersion():
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    return _versionify(Gst.version())

def pyGIVersion():
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    return _versionify(gi.version_info)

_VERSION_RE = re.compile(
    "Version:\s*(?P<version>[\d.]+)")

# FIXME: gstreamer 1.x should have fix this bug
# FIXME: find a less hackish way in gstreamer 1.x to make this work
def elementFactoryVersion(name):
    # surprisingly, there is no python way to get from an element factory
    # to its plugin and its version directly; you can only compare
    # with required versions
    # Let's use gst-inspect-0.10 and wave hands and assume it points to the
    # same version that python uses
    output = commands.getoutput('gst-inspect-0.10 %s | grep Version' % name)
    m = _VERSION_RE.search(output)
    if not m:
        return None
    return m.group('version')


def _versionify(tup):
    l = list(tup)
    if len(l) == 4 and l[3] == 0:
        l = l[:3]
    v = [str(n) for n in l]
    return ".".join(v)

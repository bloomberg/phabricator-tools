"""Handles the loading, hook registration and calling of plugins."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_pluginmanager
#
# Public Classes:
#   PluginManager
#    .hook
#   PluginError
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import copy
import importlib
import traceback


class PluginManager(object):

    """Loads plugin_names stores hook registrations and calls hooks.

    hooks is the main registration for hooks and callbacks, it looks like ...

    hooks = {
        'hook_name':[
            ('plugin_name', plugin_callback, False),
            ('2nd_plugin_name', other_callback, True)
        ],
        'another_hook':[
            ('plugin_name', another_hook_callback, False)
        ]
    }

    """

    def __init__(self, plugin_names, trusted_plugin_names):
        """Load the requested plugin submodules and register their hooks."""
        self._hooks = {}
        self._load_plugins(plugin_names, False)
        self._load_plugins(trusted_plugin_names, True)

    def _load_plugins(self, plugin_names, trusted):
        for plugin_name in plugin_names:
            plugin = self._get_plugin(plugin_name)
            self._register_hooks(plugin_name, plugin, trusted)

    def _get_plugin(self, plugin_name):
        """Gets the plugin submodule.

        The import_module method is not expensive as modules are cached
        http://docs.python.org/dev/reference/import.html#the-module-cache

        import_module returns the plugin module itself rather than the
        plugins package.
        docs.python.org/2.7/library/importlib.html#importlib.import_module

        """
        return importlib.import_module(plugin_name)

    def _register_hooks(self, plugin_name, plugin, trusted):
        """Populates the hooks dictionary with the callbacks provided by the
        plugin_names getHooks method."""
        for hook in plugin.get_hooks():
            self._hooks.setdefault(hook[0], []).append(
                (plugin_name, hook[1], trusted))

    def hook(self, hook_name, params):
        """Call's all the plugin_names registered against this hook.

        If a plugin raises an exception it is caught and a PluginError is
        generated and raised. It will print the original stack trace
        created by the plugin.

        :hook_name: The name of the hook registered by the plugin_names
        :params: The dictionary of parameters passed to the plugin

        """
        if hook_name in self._hooks.keys():
            for plugin_name, callback, trusted in self._hooks[hook_name]:
                try:
                    if not trusted:
                        params = copy.deepcopy(params)
                    callback(params)
                except Exception as e:
                    raise PluginError(e, traceback.format_exc(), plugin_name)


class PluginError(Exception):

    """Wraps any exception thrown by plugin."""

    def __init__(self, cause, trace, plugin_name):
        """Create a PluginError.

        :cause: the original exception.
        :trace: the traceback at the time of the exception
        :plugin_name: the string name of the active plugin

        """
        super(PluginError, self).__init__()
        self.trace = trace
        self.cause = cause
        self.plugin_name = plugin_name

    def __str__(self):
        return "The plugin '{0}' has generated\n{1}".format(self.plugin_name,
                                                            self.trace)

# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------

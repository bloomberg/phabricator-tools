Directory Layout
================

* `bin` - binaries for you
* `examples` - examples and utils for using the binaries
* `vagrant` - artifacts for creating an instant phabricator install

Binaries for you
----------------

`bin`

Here are all the end-products you might wish to use from this repository,
it's probably most convienient to create a symbolic link to them or add
the bin directory to $PATH.

* `phab-ping` - a simple tool to check the responsiveness of your Phabricator
* `arcyon` - a wrapper around Conduit API to aid scripting
 
Each command comes with comprehensive help, available by passing the '--help' argument, e.g.:
`$ arcyd --help`

Examples for using the binaries
-------------------------------

`examples`

To make it easy to get started with the binaries, here are some scripts which
illustrate usage examples and provide simple utilities.

Artifacts for creating an instant phabricator install
-----------------------------------------------------

`vagrant`

Everything here depends on having an instance of Phabricator up and running;
so it's important that we can have one up and running easily, these artifacts
enable you to create a new instance of Phabricator in a single step using
Vagrant and Puppet.

Please see [README](https://github.com/bloomberg/phabricator-tools/blob/master/README.md#install-phabricator-in-one-step)
for quickstart instructions.

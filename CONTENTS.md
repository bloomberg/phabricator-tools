Directory Layout
================

* `py` - the python source
* `bin` - binaries for you
* `testbed` - scripts for exercising the binaries
* `vagrant` - artifacts for creating an instant phabricator install

Python Source
-------------

`py`

To simplify usage, all the Python source is in one directory; this is so
that the modules do not need to be added to the PYTHONPATH in order to be
discovered, they run out of the box.

The python modules are divided into 'package groups' which are in turn
divided into 'packages'

There are two top-level package groups:
* `abd` - Arcyd Branch Daemon implementation (may rename this to `arc` later)
* `phl` - code which can be considered re-usable as a 'PHabricator Library'.

The `abd` group is divided into packages like so:
* `abdcmd` - implementation of Arcyd subcommands
* `abdcmnt` - format and submit event-related comments to Differential reviews
* `abdi` - high-level Arcyd implementation details
* `abdmail` - format and send event-related emails to people
* `abdt` - shared types, conventions and tools

The `phl` group is divided into packages like so:
* `phlcon` - thin wrappers around Phabricator Conduit APIs
* `phldef` - predefined data and constants
* `phlgit` - thin wrappers around Git subcommands
* `phlgitu` - high-level Git utilities
* `phlsys` - wrappers around interaction with the operating system

Binaries for you
----------------

`bin`

Here are all the end-products you might wish to use from this repository,
it's probably most convienient to create a symbolic link to them or add
the bin directory to $PATH.

* `arcyd` - the Arcanist branch-watching daemon
* `phab-ping` - a simple tool to check the responsiveness of your Phabricator
* `maily` - a trivial wrapper around sendmail to test configuration

Scripts for exercising the binaries
-----------------------------------

`testbed`

To make it easy to get started with the binaries, here are some scripts which
illustrate usage examples.  They're intended to provide a starting point and
be easy to modify and play with.

Artifacts for creating an instant phabricator install
-----------------------------------------------------

`vagrant`

Everything here depends on having an instance of Phabricator up and running;
so it's important that we can have one up and running easily, these artifacts
enable you to create a new instance of Phabricator in a single step using
Vagrant and Puppet.

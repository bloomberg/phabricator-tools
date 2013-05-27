Directory Layout
================

* `bin` - binaries for you
* `py` - the python source
* `testbed` - scripts for exercising the binaries
* `vagrant` - artifacts for creating an instant phabricator install

Binaries for you
----------------

`bin`

Here are all the end-products you might wish to use from this repository,
it's probably most convienient to create a symbolic link to them or add
the bin directory to $PATH.

* `arcyd` - the Arcanist branch-watching daemon
* `phab-ping` - a simple tool to check the responsiveness of your Phabricator
* `arcyon` - a wrapper around Conduit API to aid scripting

Python Source
-------------

`py`

The python modules are divided into 'package groups' which are in turn
divided into 'packages'.

The package group and package is pre-pended to the name of each module, this
naming convention enforces explicit imports when re-using code and disallows
wide import statements like 'import abd'.

This naming convention also promotes the use of fully-qualified names in
code so that it's easy to predict which module a sybmol comes from.

To simplify imports, all the Python source is in one directory; this may be
revisited as the source base grows.  Since the name of each module is unique,
there is no danger of name collision.

There are two top-level package groups:
* `abd` - Arcyd Branch Daemon implementation (may rename this to `arc` later)
* `aon` - Arcyon implementation
* `phl` - code which can be considered re-usable as a 'PHabricator Library'.

The `abd` package group is divided into packages like so:
* `abdcmd`  - implementation of Arcyd subcommands
* `abdcmnt` - format and submit event-related comments to Differential reviews
* `abdi`    - high-level Arcyd implementation details
* `abdmail` - format and send event-related emails to people
* `abdt`    - shared types, conventions and tools

The `aon` package group is divided into packages like so:
* `aoncmd`  - implementation of Arcyon subcommands
* `aont`    - shared types, conventions and tools

The `phl` package group is divided into packages like so:
* `phlcon`  - thin wrappers around Phabricator Conduit APIs
* `phldef`  - predefined data and constants
* `phlgit`  - thin wrappers around Git subcommands
* `phlgitu` - high-level Git utilities
* `phlsys`  - wrappers around interaction with the operating system

Scripts for exercising the binaries
-----------------------------------

`testbed`

To make it easy to get started with the binaries, here are some scripts which
illustrate usage examples, test functionality and form simple utilities.

They come in two flavors:
* exercisers - try to use as much of the binaries features as possible for QA
* recipies - well-documented usage-examples intended to be copied and extended
* utils - simple wrappers that perform a useful function

Artifacts for creating an instant phabricator install
-----------------------------------------------------

`vagrant`

Everything here depends on having an instance of Phabricator up and running;
so it's important that we can have one up and running easily, these artifacts
enable you to create a new instance of Phabricator in a single step using
Vagrant and Puppet.

Python Source
-------------

The python modules are divided into 'package groups' which are in turn
divided into 'packages'.

The package group and package is pre-pended to the name of each module, this
naming convention enforces explicit imports when re-using code and disallows
wide import statements like 'import abd'.

This naming convention also promotes the use of fully-qualified names in
code so that it's easy to predict which module a sybmol comes from.

To simplify imports, all the Python source for each package group is in the
same directory; this may be revisited as the source base grows.  Since the
name of each module is unique, there is no danger of name collision.

These are the top-level package groups:
* `abd` - Arcyd Branch Daemon implementation (may rename this to `arc` later)
* `aon` - Arcyon implementation
* `phl` - code which can be considered re-usable as a 'PHabricator Library'.
* `pig` - Phab-ping implementation

-----

The **abd** package group is divided into packages like so:

* `abdcmd`  - implementation of Arcyd subcommands
* `abdcmnt` - format and submit event-related comments to Differential reviews
* `abdi`    - high-level Arcyd implementation details
* `abdmail` - format and send event-related emails to people
* `abdt`    - shared types, conventions and tools

-----

The **aon** package group is divided into packages like so:

* `aoncmd`  - implementation of Arcyon subcommands
* `aont`    - shared types, conventions and tools

-----

The **phl** package group is divided into packages like so:

* `phlcon`  - thin wrappers around Phabricator Conduit APIs
* `phldef`  - predefined data and constants
* `phlgit`  - thin wrappers around Git subcommands
* `phlgitu` - high-level Git utilities
* `phlsys`  - wrappers around interaction with the operating system

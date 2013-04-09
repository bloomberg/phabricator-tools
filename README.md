# phabricator-tools

Tools and daemons for administering lots of Phabricator instances and
integrating them with other tools.

## Content

** Arcyd **
Arcanist-git-branch-daemon (WIP), enables simple workflows without using
arcanist directly:

  $ git checkout -b feature/mywork
  .. do work and commit ..
  $ git push origin feature/mywork:ph-review/mywork/master
  .. daemon creates a review based on commit comments ..
  .. reviewer appoves ..
  .. daemon merges to master ..

See arcyd.remarkup for more information.

** phi ** (planned)
A command-line tool for working with lots of Phabricator instances,
e.g.

  $ phi new myinstance

Creates a new Phabricator webfront for 'myinstance' in the instances/
directory, initialised the db, starts the daemons.

(TODO: need to doc directory layout separately)

** gnd ** (planned)
Git-notes-daemon
Pull data from Differential revisions into 'refs/notes/differential' for
individual git repos.  Uses the review URIs embedded in commit messages to
retreive the data.

## Phabricator Developer setup instructions

*To install locally in Linux (tested on Lubuntu 12.10):*

$ sudo puppet apply vagrant/puppet/phabricator/manifests/default.pp \
    --modulepath vagrant/puppet

*To create a local VM serving up Phabricator on Windows:*

Install VirtualBox, Vagrant

$ ./vagrant-up.sh
(should take about 10 mins to download the base image)

When that's done, point a web-browser at 'http://127.0.0.1:8080'
to login to your new Phabricator instance.

Pre-installed Users: "alice", "bob", "phab" (administrator)
All pre-installed users have the password set to 'password'

## Directory Layout

*./arcyd*
    The 'Arcyd' application

*./arcyd_test/*
    A testbed for the Arcyd application to run in,
    setup with 'make_test_repos.sh' and run
        'run_arcyd_single.sh'
    or  'run_arcyd_multi.sh'
    to try arcyd out in the test instance.

*./LICENSE*

*./runtests*
    Convenience script to run the test suite

*./TODO*

*./vagrant*
    All the 'instant Phabricator' artifacts may be found here.

*./*
    To simplify usage, all the Python source is in the root directory;
    this is so that the modules do not need to be added to the PYTHONPATH
    in order to be discovered, they run out of the box.

    The python modules are divided into 'package groups' which are in turn
    divided into 'packages'

    ./abd*
        The 'abd' package group contains the Arcyd-specific code and may be
        renamed to 'arc' later.

        ./abdcmd_*
            Implemenation of Arcyd subcommands

        ./abdcmnt_*
            Format and submit event-related comments to differential revisions

        ./abdmail_*
            Format and submit event-related emails to people

        ./abdt_*
            General shared types and conventions

    ./phl*
        The 'phl' package group contains the code which can be considered
        re-usable as a 'PHabricator Library'.

        ./phlcon_*
            Thin wrappers around Phabricator Conduit APIs

        ./phldef_*
            Predefined data and constants

        ./phlgit_*
            Thin wrappers around Git subcommands

        ./phlgitu_*
            High-level Git utilities

        ./phlsys_*
            Wrappers around interaction with the operating system

## Contacts

Angelos Evripiotis (jevripio@bloomberg.net)

## Credits and Acknowledgements

Thanks to the awesome guys working on the Phabricator project!

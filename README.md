# phabricator-tools

Tools and daemons for administering lots of Phabricator instances and
integrating them with other tools.

## Content

** phi **
A command-line tool for working with lots of Phabricator instances,
e.g.

  $ phi new myinstance

creates a new Phabricator webfront for 'myinstance' in the instances/
directory.

(TODO: need to doc directory layout separately)

** abd **
Arcanist-git-branch-daemon (WIP), enables simple workflows without using
arcanist directly:

  $ git checkout -b feature/mywork
  .. do work and commit ..
  $ git push origin feature/mywork:ph-review/mywork/master
  .. daemon creates a review based on commit comments ..
  .. reviewer appoves ..
  .. daemon merges to master ..

** gnd **
Git-notes-daemon (planned)
Pull data from Differential revisions into 'refs/notes/differential' for
individual git repos.  Uses the review URIs embedded in commit messages to
retreive the data.

## Setup instructions

(TODO, will need to finish Vagrantfile and puppet manifest first)

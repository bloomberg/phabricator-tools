How to contribute
=================

If you'd like to help us improve and extend phabricator-tools, then we welcome
your contributions!

Below you will find some basic steps required to be able to contribute to
phabricator-tools. If you have any questions about this process or any other
aspect of contributing to a Bloomberg open source project, feel free to send an
email to open-tech@bloomberg.net and we'll get your questions answered as
quickly as we can.


Contribution Licensing
---------------------

Since phabricator-tools is distributed under the terms of the [Apache License,
Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html), contributions
that you make to phabricator-tools are licensed under the same terms. In order
for us to be able to accept your contributions, we will need explicit
confirmation from you that you are able and willing to provide them under these
terms, and the mechanism we use to do this is called a Developer's Certificate
of Origin [DCO](DCO.md).  This is very similar to the process used by the
Linux(R) kernel, Samba, and many other major open source projects.

To participate under these terms, all that you must do is include a line like
the following as the last line of the commit message for each commit in your
contribution:

    Signed-Off-By: Random J. Developer <random@developer.example.org>

You must use your real name (sorry, no pseudonyms, and no anonymous
contributions).

Setting up to develop
---------------------

* Run `./meta/install_devtools.sh`
* Install Phabricator locally, either with Vagrant or directly on your linux
  box, see instructions [here](README.md#install-phabricator-in-one-step)
* Make sure that all the tests pass with `./precommit.sh`, these depend on a
  local installation of Phabricator
* To exercise `arcyd` manually, run `./testbed/arcyd/test_shell.sh`. This will
  create a temporary directory and set up a couple of arcyd instances to test
  with. Use `exit` to clean up the instances and return to your previous shell.
* To start playing with `arcyon`, try looking at the
  [examples](examples/arcyon)
* There's a [README](py/README.md) to get you started with the code layout
* There is some [design documentation](doc/design)

Commit etiquette
----------------

* Please ensure that `./precommit.sh` passes cleanly on each of your commits
* Please include a 'Test Plan:' field in each of your commits that documents
  what you did to ensure that your change is valid. This should include enough
  detail that it is repeatable by someone else and it's possible for someone to
  point out things missing or wrong in the plan. e.g.
  ```
  Test Plan:

  Exercise old workaround with old version of Phabricator
      $ arcyon task-query --uri http://127.0.0.1  --ids 6
      .. ok ..

  Exercise new workaround with new version of Phabricator
      $ arcyon task-query --uri https://secure.phabricator.com  --ids 6144
      .. ok ..

  Usual checks just in case
  $ ./precommit.sh
  ```
* Please read Tim Pope's [good advice](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
  on making commit messages
* Please read [PEP8](http://legacy.python.org/dev/peps/pep-0008/)
* Bonus: the Phabricator project has some excellent documentation on
  [writing reviewable code](https://secure.phabricator.com/book/phabflavor/article/writing_reviewable_code/)
  and [revision control](https://secure.phabricator.com/book/phabflavor/article/recommendations_on_revision_control/)

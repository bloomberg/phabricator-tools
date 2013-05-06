phabricator-tools
=================

Tools and daemons for administering lots of Phabricator instances and
integrating them with other tools.

Overview
--------

[Phabricator](http://phabricator.org/) is an awesome, open-source application
for communicating and collaborating with other software developers within
an enterprise.

Many enterprises may be big enough such that it makes sense to have an
instance of Phabricator per area of responsiblity or product being worked
on; for example you may have one Phabricator for your website and one for
each of your major products.

This project aims to complement Phabricator by making installation,
administration and interoperation easier.  At some point it will hopefully
be merged with Phabricator-actual.

Extend Phabricator easily with Arcyon
-------------------------------------

There are often house-keeping tasks which you like to be able to automate,
the Phabricator 'Conduit' API is designed to let you interact with your
instance over http.

Arcyon wraps up the API with a command-line interface for easy scripting.

e.g. say 'poke' on all open reviews not updated for 2 weeks

    $ arcyon query --min-update-age "2 weeks" --status-type open | arcyon comment --ids-file - -m 'poke'

Hands-free Differential reviews with Arcyd
------------------------------------------

This is a daemon which watches git repositories and automatically creates
reviews and lands them when accepted.

Here is an example of someone working with a repository which is watched
by Arcyd:

    $ git checkout -b feature/mywork
    .. do work and commit ..
    $ git push origin feature/mywork:ph-review/mywork/master

    .. Arcyd sees 'ph-review' branch, creates a review based on commits ..

    .. the reviewer approves ..
    .. Arcyd see approval, lands the changes on master, deletes branch ..

Install Phabricator in one step
-------------------------------

To get up and running quickly, a vagrant configuration is included for
creating a new Linux VM and making a fully working Phabricator installation;
including all it's dependencies, i.e. Apache, MySQL.

If you want to provision an existing VM or machine with Phabricator you
can also use the puppet configuration directly.

__To create a new local VM serving up Phabricator__

* Requires [VirtualBox](https://www.virtualbox.org/) and
  [Vagrant](http://www.vagrantup.com/)

1. `$ cd vagrant && vagrant up`
2. Point a web-browser at 'http://127.0.0.1:8080' to login to your new
   Phabricator instance

__To install within an existing VM or machine__
* Tested on Lubuntu 12.10 on VirtualBox

1. `$ sudo puppet apply vagrant/puppet/phabricator/manifests/default.pp
   --modulepath vagrant/puppet`
2. Point a web-browser at 'http://127.0.0.1' to login to your new Phabricator
   instance

__Pre-installed Users__

`alice`, `bob`, `phab` (administrator)
All pre-installed users have the password set to `password`

Contacts
--------

Angelos Evripiotis (jevripio@bloomberg.net)

Credits and Acknowledgements
----------------------------

Thanks to the awesome guys working on the Phabricator project!

License
-------

MIT license. See license text in
[LICENSE](https://github.com/bloomberg/phabricator-tools/blob/master/LICENSE).

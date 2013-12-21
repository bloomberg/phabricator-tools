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

There are often house-keeping tasks which you like to be able to automate;
the Phabricator 'Conduit' API is designed to let you interact with your
instance over HTTP.

Arcyon wraps up the API with a command-line interface for easy scripting.

e.g. say 'poke' on all open reviews not updated for 2 weeks

    $ arcyon query --min-update-age "2 weeks" --status-type open | arcyon comment --ids-file - -m 'poke'

See the raw documentation here:
[MAN PAGES](https://github.com/bloomberg/phabricator-tools/tree/master/doc/man/arcyon).

Install Phabricator in one step
-------------------------------

To get up and running quickly, a Vagrant configuration is included for
creating a new Linux VM and making a fully working Phabricator installation,
including all its dependencies, i.e. Apache, MySQL.

If you want to provision an existing VM or machine with Phabricator you
can also use the included Puppet configuration directly.

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

*Note:* Please note that if you have disabled anonymous user access or limited privilages 
then you would have to specify a user who has required privilages in the default puppet 
manifest file as follows. Change line reading 

    exec { "mysql < ${phab_dir}/initial.db && ${dev_dir}/phabricator/bin/storage upgrade --force":

to 

    exec { "mysql -u phab < ${phab_dir}/initial.db && ${dev_dir}/phabricator/bin/storage upgrade --user phab --force":

__Pre-installed Users__

`alice`, `bob`, `phab` (administrator)
All pre-installed users have the password set to `password`

Monitor your Phabricator instance with phab-ping
------------------------------------------------

A simple wrapper around the 'conduit.ping' API which Phabricator provides,
`phab-ping` behaves much like the regular ping as a simple health-check tool.

It requests some information from the instance running at the specified URL
and reports how long Phabricator takes to respond.

    $ phab-ping https://secure.phabricator.com
    conduit.ping https://secure.phabricator.com/api/
    request 1 : ip-10-170-222-96 : 1336 ms
    request 2 : ip-10-170-222-96 : 1352 ms
    request 3 : ip-10-170-222-96 : 1355 ms
    request 4 : ip-10-170-222-96 : 1353 ms
    request 5 : ip-10-170-222-96 : 1456 ms
    ^C
    --- https://secure.phabricator.com/api/ conduit.ping statistics ---
    5 requests processed
    min / mean / max = 1336.74 / 1371.00 / 1456.22 ms

Contacts
--------

Angelos Evripiotis (jevripiotis@bloomberg.net)

Credits and Acknowledgements
----------------------------

Thanks to the awesome guys working on the Phabricator project!

License
-------

MIT-style license. See license text in
[LICENSE](https://github.com/bloomberg/phabricator-tools/blob/master/LICENSE).

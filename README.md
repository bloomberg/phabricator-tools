# phabricator-tools

*Tools and daemons for administering lots of Phabricator instances and
integrating them with other tools*

[Phabricator](http://phabricator.org/) is an awesome, open-source application for communicating
and collaborating with other software developers within an enterprise.

Many enterprises may be big enough such that it makes sense to have
an instance of Phabricator per area of responsiblity or product being
worked on; for example you may have one Phabricator for your website
and one for each of your major products.

This project aims to complement Phabricator by making installation,
administration and interoperation easier.  At some point it will
hopefully be merged with Phabricator-actual.

The first tool to be provided is *Arcyd*, see below.

## Arcyd
This is a daemon which watches git repositories and automatically creates reviews and lands them when accepted.

Here is an example of someone working with a repository which is watched by Arcyd:

    $ git checkout -b feature/mywork
    .. do work and commit ..
    $ git push origin feature/mywork:ph-review/mywork/master
    .. daemon creates a review based on commit comments ..
    .. the reviewer appoves ..
    .. Arcyd merges the changes to master ..

(TODO: paste existing doc here)

## Phabricator Developer setup instructions

**To install locally in a clean Linux VM (tested on Lubuntu 12.10):**

1. `$ sudo puppet apply vagrant/puppet/phabricator/manifests/default.pp --modulepath vagrant/puppet`
2. Point a web-browser at 'http://127.0.0.1' to login to your new Phabricator instance

**To create a local VM serving up Phabricator on Windows:**

1. Install [VirtualBox](https://www.virtualbox.org/)
2. Install [Vagrant](http://www.vagrantup.com/)
3. ```$ ./vagrant-up.sh```
(should take about 10 mins to download the base image)
4. Point a web-browser at 'http://127.0.0.1:8080' to login to your new Phabricator instance

**Pre-installed Users**

`alice`, `bob`, `phab` (administrator)
All pre-installed users have the password set to `password`

## Contacts

Angelos Evripiotis (jevripio@bloomberg.net)

## Credits and Acknowledgements

Thanks to the awesome guys working on the Phabricator project!


## License

MIT license. See license text in [LICENSE](https://github.com/bloomberg/phabricator-tools/blob/master/LICENSE).

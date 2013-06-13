Examples
========

The files in the `examples/` directory are intended to be simple scripts that can serve as
example usage of the binaries in bin/ and as primitives tools.

Phabricator instance required
-----------------------------

Note that you need a Phabricator instance and user account in order to be able
to use these example scripts.

You can setup an instance locally by following the instructions here:
[README](https://github.com/bloomberg/phabricator-tools/blob/master/README.md#install-phabricator-in-one-step)

You can also use the official Phabricator installation here:
https://secure.phabricator.com/

_Note that this is a production installation, please don't run anything you're
unsure of against it._

Phab-ping
---------

The `examples/phab-ping/` directory has examples for using the `bin/phab-ping`
health-check tool against Phabricator installations.

The examples here assume:
* you are running from the `examples/phab-ping/` directory

**Examples:**

* `ping_phabricator_actual.sh` - check that the official Phabricator instance
   at 'secure.phabricator.com' is reachable and report the round trip time for
   a simple request using the conduit API
```
$ ./ping_phabricator_actual.sh
conduit.ping https://secure.phabricator.com/api/
request 1 : ip-10-170-222-96 : 770 ms
request 2 : ip-10-170-222-96 : 766 ms
request 3 : ip-10-170-222-96 : 767 ms
--- https://secure.phabricator.com/api/ conduit.ping statistics ---
3 requests processed
min / mean / max = 766.90 / 768.45 / 770.99 ms
```

* `watch_instance_mail_on_fail.sh` - continuously ping the specified instance,
  if it fails to respond then mail the specified address.  Note that this
  depends on `sendmail` being setup and configured (which may not be available
  on all platforms).
```
$ ./watch_instance_mail_on_fail.sh http://127.0.0.1 role-account@server.example admin@server.example
pinging http://127.0.0.1
^C
conduit.ping http://127.0.0.1/api/
request 1 : bbuser-VirtualBox : 147 ms
request 2 : bbuser-VirtualBox : 89 ms
request 3 : bbuser-VirtualBox : 93 ms
request 4 : bbuser-VirtualBox : 94 ms
request 5 : bbuser-VirtualBox : 92 ms
request 6 : bbuser-VirtualBox : 86 ms
request 7 : bbuser-VirtualBox : 83 ms
request 8 : bbuser-VirtualBox : 94 ms
request 9 : bbuser-VirtualBox : 81 ms
request 10 : bbuser-VirtualBox : 92 ms
request 11 :
--- http://127.0.0.1/api/ conduit.ping statistics ---
10 requests processed
min / mean / max = 81.89 / 95.50 / 147.32 ms
=== snip ===
STOPPED
```

Arcyon
------

The `examples/arcyon/` directory has examples for interacting with your
Phabricator install using the `bin/arcyon` tool.

The examples here assume:
* you have installed `bin/arcyon` onto your $PATH
* you have a valid `~/.arcrc` and perhaps a `.arcconfig` pointing to a
  Phabricator instance

To guide you through meeting these requirements, please try running:
```
examples/arcyon/ $ ./_check_requirements.sh
```

**Examples:**

* `_check_requirements.sh` - make sure that the other examples will be able to
  run in the current environment; if not then give suggestions for setting up

* `count_recent_reviews_per_period.sh`
```
$ ./count_recent_reviews_per_period.sh
last update time
      1 1 hour
      1 17 hours
      4 1 day
```
...
```
    259 8 months
    144 9 months
    201 10 months
3000 reviews considered
(n.b. counts up to last 3000 reviews or so only)
```

* `list_my_revs.sh`
```
  $ ./list_my_revs.sh
  Open reviews where you are the author:
  178 / Needs Review / full context when diffing
  176 / Accepted / fixup nitpicks from flake8

  Open reviews where you are a reviewer:
  174 / Needs Review / implment phi debug, nodebug, upgrade
  173 / Needs Review / phit_naming: add 'config' to database names
  169 / Accepted / .gitignore: .ropeproject
```

* `list_my_todo.sh`
```
  $ ./list_my_todo.sh
  Revisions you have authored:
  176 / Accepted / fixup nitpicks from flake8

  Revisions you are reviewing:
  174 / Needs Review / implment phi debug, nodebug, upgrade
  173 / Needs Review / phit_naming: add 'config' to database names
```

* `list_reviews_per_day.sh`

* `list_reviews_per_week.sh`

* `list_revisions_by_project.sh`
```
    $ ./list_revisions_by_project.sh
    None 13830
    None 13824
    phabricator 13815
    libphutil 13813
    phabricator 13811
    phabricator 13794
    phabricator 13754
    phabricator 13752
    phabricator 13793
    phabricator 13792
    ^C
```

* `list_top_authors.sh`
```
$ ./list_top_authors.sh
     321 epriestley
     142 chad
     93 vrana
     91 AnhNhan
     71 btrahan
     29 DeedyDas
     28 edward
     27 Afaque_Hussain
     26 hach-que
     22 garoevans
```

* `list_waiting_on.sh`
```
  Revisions you have authored, waiting on others:
  178 / Needs Review / full context when diffing

  Revisions you are reviewing, waiting on others:
  169 / Accepted / .gitignore: .ropeproject
```

* `nudge_stale_waiting_on.sh`
```
  $ ./nudge_stale_waiting_on.sh
  will comment 'nudge' on the following reviews:
  178 169
  Hit 'y' to continue or any other to exit: y
  {u'revisionid': u'178', u'uri': u'http://127.0.0.1/D178'}
  {u'revisionid': u'169', u'uri': u'http://127.0.0.1/D169'}
```

If you're interested in developing bugzfeed, you can set up a full system
pretty easily:

* Run "python setup.py develop" in the root bugzfeed directory.

* If you have a Bugzilla installation, grab the [PushNotify extension][1]
  (this *may* require specifically the source of bugzilla.mozilla.org instead
  of upstream Bugzilla, but I'm not sure).  Put it in your extensions
  directory.
** If you don't have Bugzilla set up already, install the [BMO developer
   vagrant box][2].  You'll have to merge in recent changes, which may break
   things due to some  recent big schema changes, or you can wait until
   [bug 936856][3] is fixed.

* Grab the source to the [mozillapulse package][4] and bring up the vagrant
  box in the 'test' directory.

* The [pulse] options in bugzfeed's config.ini.example contain the default
  settings for the Pulse vagrant box.  Copy this over to config.ini; you
  may want to change other options, particularly in [log].

* Run the bugzfeed server via "bugzfeed-server config.ini".  You may want to
  use -v to see all the notifications being sent out, and don't forget to
  include the path to config.ini if it isn't in your current directory.

* Grab the [Bugzilla Simple Shim][5] and run it on your Bugzilla box.  You'll
  probably want to use the -r option to keep it going.  Configure it to
  point to your Pulse vagrant box, using the same values as in bugzfeed's
  config.ini (but note that the section and option names are different; see
  the config.ini.example in the pulseshims directory).

* If you changed the default port, modify examples/example.js appropriately.
  Then load examples/example.html, subscribe to bugs, modify them in your
  Bugzilla box, and watch the changes stream in!

[1]: http://bzr.mozilla.org/bmo/4.2/files/head:/extensions/ZPushNotify/
[2]: https://wiki.mozilla.org/BMO/Hacking#Developer_vagrant_box
[3]: https://bugzilla.mozilla.org/show_bug.cgi?id=936856
[4]: https://hg.mozilla.org/automation/mozillapulse/
[5]: https://hg.mozilla.org/automation/pulseshims/

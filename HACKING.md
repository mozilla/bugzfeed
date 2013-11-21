If you're interested in developing bugzfeed, you can set up a full system
pretty easily:

* Run "python setup.py develop" in the root bugzfeed directory.

* If you have a Bugzilla installation, grab the [PushNotify extension][1]
  (this *may* require specifically the source of bugzilla.mozilla.org instead
  of upstream Bugzilla, but I'm not sure).  Put it in your extensions
  directory.

 * If you don't have Bugzilla set up already, install the [BMO developer
   vagrant box][2].  You'll have to merge in recent changes, which may break
   things due to some  recent big schema changes, or you can wait until
   [bug 936856][3] is fixed.

* Grab the source to the [mozillapulse package][4] and bring up the vagrant
  box in the "test" directory.

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

You can also set up a minimal installation without Bugzilla, although it
won't be as interesting.  You'll still need a local Pulse instance, as
described above, but you can simulate changes by creating just the table
used by the notification system and writing entries to it yourself.

Just set up a database (anything supported by SQLAlchemy, e.g. MySQL,
PostgreSQL, or even SQLite) and create a table to hold the notifications
(default name is "push\_notify", but it's configurable in the shim's
config.ini).  This table should contain three columns, "id" (int),
"bug\_id" (int), and "delta\_ts" (datetime).  This is the schema in MySQL,
without the foreign-key relationships that would be present in the full
Bugzilla db:

    CREATE TABLE `push_notify` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `bug_id` mediumint(9) NOT NULL,
      `delta_ts` datetime NOT NULL,
      PRIMARY KEY (`id`)
    )

The shim uses SQLSoup to automatically figure out the schema, so as long as
the data types are roughly correct, it should be fine (e.g. exact int sizes
are probably not important).

When this is set up, to simulate a change, you should be able to just add
new entries to the table.  Again with MySQL, something like

    echo 'insert into push_notify (bug_id, delta_ts) values (123456, now())' | mysql -u bugs bugs

with the correct values for the username and database.  This shim should
pick this up and write a notification to your Pulse instance.

[1]: http://bzr.mozilla.org/bmo/4.2/files/head:/extensions/ZPushNotify/
[2]: https://wiki.mozilla.org/BMO/Hacking#Developer_vagrant_box
[3]: https://bugzilla.mozilla.org/show_bug.cgi?id=936856
[4]: https://hg.mozilla.org/automation/mozillapulse/
[5]: https://hg.mozilla.org/automation/pulseshims/

Bugzfeed is a WebSocket server that provides notifications when bugs in a
Bugzilla database change.  It is part of the [Bugzilla Change Notification
System][1].  Currently it uses Mozilla's Pulse service but could conceivably
be extended to use other middleware such as ZeroMQ.

Bugzfeed uses the tornado options format, meaning that options can be
specified either on the command line or in a Python (*not* .ini) config
file via the --config option.  As per standard tornado option processing,
--config overrides options specified earlier on the command line.

[1]: https://wiki.mozilla.org/BMO/ChangeNotificationSystem

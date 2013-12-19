# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import socket
import threading
import time

from mozillapulse.consumers import SimpleBugzillaConsumer

class ListenerThread(threading.Thread):

    RETRY_TIMEOUT_SEC = 30
    daemon = True

    def __init__(self, cfg, cb):
        threading.Thread.__init__(self)
        self.cb = cb
        self.consumer = SimpleBugzillaConsumer(**cfg)

    def run(self):
        def cb(body, message):
            self.cb((body['payload']['id'], body['payload']['delta_ts']))
        self.consumer.configure(topic='#', callback=cb)

        while True:
            start_time = time.time()
            try:
                self.consumer.listen()
            except socket.error:
                # Common to be disconnected every 10 minutes or so, so
                # don't necessarily log anything.
                pass

            elapsed = time.time() - start_time

            # We can't easily tell if the consumer actually connected for any
            # length of time.  If the call returned relatively quickly, then
            # presume there is a problem establishing the connection, and wait
            # a bit before trying.  Otherwise, we either connected for a
            # while, or we took a long time to error out when trying to
            # connect.  Either way, retry immediately.

            if elapsed < self.RETRY_TIMEOUT_SEC:
                logging.warn('Connection (or connection attempt) lasted only '
                             '%d seconds; sleeping for %d seconds before '
                             'retrying.' % (elapsed, self.RETRY_TIMEOUT_SEC))
                time.sleep(self.RETRY_TIMEOUT_SEC)

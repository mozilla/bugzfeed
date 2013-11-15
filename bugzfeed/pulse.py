# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import threading

from mozillapulse.consumers import SimpleBugzillaConsumer

class ListenerThread(threading.Thread):

    daemon = True

    def __init__(self, cfg, cb):
        threading.Thread.__init__(self)
        self.cb = cb
        self.consumer = SimpleBugzillaConsumer(**cfg)

    def run(self):
        def cb(body, message):
            self.cb((body['payload']['id'], body['payload']['delta_ts']))
        self.consumer.configure(topic='#', callback=cb)
        self.consumer.listen()

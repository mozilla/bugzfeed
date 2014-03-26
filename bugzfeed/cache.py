# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import errno
import json

class MessageCache(object):

    MAX_MESSAGES = 10000

    def __init__(self, filename):
        self.filename = filename
        self.messages = []
        self.load()

    def load(self):
        try:
            self.messages = json.loads(file(self.filename, 'r').read())
        except IOError, e:
            if e.errno != errno.ENOENT:
                raise
            self.messages = []

    def flush(self):
        file(self.filename, 'w').write(json.dumps(self.messages))

    def update(self, message):
        self.messages.append(message)
        self.messages = self.messages[-self.MAX_MESSAGES:]
        self.flush()

    def query(self, bug_ids, since):
        for m in self.messages:
            if m['bug'] in bug_ids and m['when'] >= since:
                yield m

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import logging

from collections import defaultdict

class BadBugId(Exception):
    pass


class BugSubscriptions(object):

    def __init__(self):
        self.conn_bug_map = defaultdict(set)
        self.bug_conn_map = defaultdict(set)

    def subscribe(self, bug_id, connection):
        bug_id = self._bug_id(bug_id)
        self.bug_conn_map[bug_id].add(connection)
        self.conn_bug_map[connection].add(bug_id)

    def unsubscribe(self, bug_id, connection):
        bug_id = self._bug_id(bug_id)
        try:
            self.bug_conn_map[bug_id].remove(connection)
            self.conn_bug_map[connection].remove(bug_id)
        except KeyError:
            logging.warning('Failed to unsubscribe connection %s from bug %d.'
                            % (connection, bug_id))

    def subscriptions(self, connection):
        if connection not in self.conn_bug_map:
            return []
        return list(self.conn_bug_map[connection])

    def connection_closed(self, connection):
        bugs = list(self.conn_bug_map[connection])
        for b in bugs:
            self.unsubscribe(b, connection)

    def update(self, u):
        self.bug_updated(*u)

    def bug_updated(self, bug_id, when):
        for c in self.bug_conn_map[bug_id]:
            logging.debug('Alerting connection %d that bug %d changed at %s.'
                          % (id(c), bug_id, when))
            c.write_message(json.dumps({'command': 'update', 'bug': bug_id,
                                        'when': when}))

    @staticmethod
    def _bug_id(bug_id):
        if isinstance(bug_id, int):
            return bug_id
        try:
            return int(bug_id)
        except ValueError:
            raise BadBugId()


subscriptions = BugSubscriptions()

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json

import tornado.websocket

from bugzfeed import __version__ as bugzfeed_version
from bugzfeed.subscriptions import subscriptions, BadBugId

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        decoded = json.loads(message)
        command = decoded['command']
        result = 'ok'
        extra_attrs = {}
        try:
            if command == 'subscribe':
                subscriptions.subscribe(decoded['bug'], self)
                extra_attrs['bugs'] = subscriptions.subscriptions(self)
            elif command == 'unsubscribe':
                subscriptions.unsubscribe(decoded['bug'], self)
                extra_attrs['bugs'] = subscriptions.subscriptions(self)
            elif command == 'subscriptions':
                extra_attrs['bugs'] = subscriptions.subscriptions(self)
            elif command == 'version':
                extra_attrs['version'] = bugzfeed_version
            else:
                result = 'error'
                extra_attrs['error'] = 'invalid command'
        except BadBugId:
            result = 'error'
            extra_attrs['error'] = 'invalid bug id; must be integer'
        response = {'result': result, 'command': command}
        response.update(extra_attrs)
        self.write_message(json.dumps(response))

    def on_close(self):
        subscriptions.connection_closed(self)

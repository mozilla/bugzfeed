# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json

import tornado.websocket

from bugzfeed import __version__ as bugzfeed_version
from bugzfeed.subscriptions import subscriptions, BadBugId


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        '''Accept all cross-origin traffic.'''
        return True

    def on_message(self, message):
        decoded = json.loads(message)
        command = decoded['command']
        result = 'ok'
        extra_attrs = {}
        cb = None
        cb_args = []
        try:
            if command == 'subscribe':
                cb = subscriptions.subscribe(decoded['bugs'], self)
                if decoded.get('since'):
                    cb = subscriptions.catch_up
                    cb_args = [decoded['bugs'], decoded['since'], self]
                extra_attrs['bugs'] = subscriptions.subscriptions(self)
            elif command == 'unsubscribe':
                subscriptions.unsubscribe(decoded['bugs'], self)
                extra_attrs['bugs'] = subscriptions.subscriptions(self)
            elif command == 'subscriptions':
                extra_attrs['bugs'] = subscriptions.subscriptions(self)
            elif command == 'version':
                extra_attrs['version'] = bugzfeed_version
            else:
                result = 'error'
                extra_attrs['error'] = 'invalid command'
        except KeyError, e:
            result = 'error'
            extra_attrs['error'] = 'missing mandatory arg: %s' % e
        except BadBugId:
            result = 'error'
            extra_attrs['error'] = 'invalid bug id; must be integer'
        response = {'result': result, 'command': command}
        response.update(extra_attrs)
        self.write_message(json.dumps(response))
        if cb:
            cb(*cb_args)

    def on_close(self):
        subscriptions.connection_closed(self)

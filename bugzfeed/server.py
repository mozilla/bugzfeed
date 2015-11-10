# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import sys
from collections import defaultdict

import tornado.ioloop
import tornado.options
import tornado.web

from bugzfeed import config
from bugzfeed.pulse import ListenerThread
from bugzfeed.subscriptions import update_subscriptions
from bugzfeed.websocket import DevWebSocketHandler, WebSocketHandler


tornado.options.define('address', default='0.0.0.0',
                       help='server IP address, defaults to 0.0.0.0',
                       type=str)
tornado.options.define('port', default=8844, help='server port', type=int)

application = tornado.web.Application([
    (r'/dev/', DevWebSocketHandler),
    (r'/', WebSocketHandler),
])


def main():
    opts = tornado.options.options.as_dict()
    ioloop = tornado.ioloop.IOLoop.instance()

    def bug_updated(update):
        ioloop.add_callback(update_subscriptions, update)

    logging.info('Starting Pulse listener.')
    listener = ListenerThread(config.pulse_cfg, bug_updated)
    listener.start()
    logging.info('Starting WebSocket server on %s:%d.' %
                 (opts['address'], opts['port']))
    logging.debug('Debug logs enabled.')
    application.listen(opts['port'], address=opts['address'])
    try:
        ioloop.start()
    except KeyboardInterrupt:
        return


def cli():
    try:
        tornado.options.parse_command_line()
    except tornado.options.Error, e:
        print >> sys.stderr, e
        sys.exit(1)
    main()

if __name__ == '__main__':
    cli()

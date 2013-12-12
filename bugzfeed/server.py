# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import sys

from collections import defaultdict

import tornado.ioloop
import tornado.options
import tornado.web

from bugzfeed.pulse import ListenerThread
from bugzfeed.subscriptions import subscriptions
from bugzfeed.websocket import WebSocketHandler

def define_group_opt(group, name, **kwargs):
    kwargs['group'] = group
    tornado.options.define('%s_%s' % (group, name), **kwargs)

tornado.options.define('address', default='',
                       help='server IP address, defaults to 0.0.0.0', type=str)
tornado.options.define('port', default=8844, help='server port', type=int)
tornado.options.define('config', default=None, help='path to config file',
                       type=str,
                       callback=lambda path: \
                           tornado.options.parse_config_file(path, final=False))

define_group_opt('pulse', 'host', default=None, help='pulse host name or IP',
                 type=str)
define_group_opt('pulse', 'port', default=None, help='pulse host port',
                 type=int)
define_group_opt('pulse', 'vhost', default=None, help='pulse vhost', type=str)
define_group_opt('pulse', 'user', default=None, help='pulse username', type=str)
define_group_opt('pulse', 'password', default=None, help='pulse password',
                 type=str)
define_group_opt('pulse', 'broker_timezone', default=None,
                 help='pulse timezone', type=str)


application = tornado.web.Application([
    (r'/', WebSocketHandler),
])


def get_pulse_cfg(pulse_opts):
    # Preserve only options with values so that pulse config defaults can be
    # used.
    pulse_cfg = dict([(k, v) for (k, v) in pulse_opts.iteritems()
                      if v is not None])
    if not 'applabel' in pulse_cfg:
        pulse_cfg['applabel'] = 'bugzfeed'
    return pulse_cfg


def main(opts_global, opts_groups):
    pulse_cfg = get_pulse_cfg(opts_groups['pulse'])
    ioloop = tornado.ioloop.IOLoop.instance()
    def bug_updated(updates):
        ioloop.add_callback(subscriptions.update, updates)
    logging.info('Starting Pulse listener.')
    listener = ListenerThread(pulse_cfg, bug_updated)
    listener.start()
    logging.info('Starting WebSocket server on port %d.' % opts_global['port'])
    logging.debug('Debug logs enabled.')
    application.listen(opts_global['port'], address=opts_global['address'])
    try:
        ioloop.start()
    except KeyboardInterrupt:
        return


def get_opts(options):
    """Separates options into globals and groups and translates to dicts."""
    opts_global = tornado.options.options.as_dict()
    opts_groups = defaultdict(dict)
    for group in tornado.options.options.groups():
        for k, v in opts_global.items():
            if k.startswith('%s_' % group):
                opts_groups[group][k[len(group)+1:]] = v
                del opts_global[k]
    return (opts_global, dict(opts_groups))


def cli():
    try:
        tornado.options.parse_command_line()
    except tornado.options.Error, e:
        print >> sys.stderr, e
        sys.exit(1)
    opts_global, opts_groups = get_opts(tornado.options.options)
    main(opts_global, opts_groups)


if __name__ == '__main__':
    cli()

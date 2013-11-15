# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import ConfigParser
import optparse
import sys

import mozlog
import tornado.ioloop
import tornado.web

from bugzfeed.pulse import ListenerThread
from bugzfeed.subscriptions import subscriptions
from bugzfeed.websocket import WebSocketHandler

application = tornado.web.Application([
    (r'/', WebSocketHandler),
])

def load_pulse_cfg(cfg):
    pulse_cfg = {}
    if cfg.has_section('pulse'):
        for opt in cfg.options('pulse'):
            pulse_cfg[opt] = cfg.get('pulse', opt)
    return pulse_cfg


def setup_logging(cfg, options):
    try:
        logfile = cfg.get('log', 'file')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        logfile = None

    if logfile:
        handler = mozlog.FileHandler(logfile)
    else:
        handler = mozlog.StreamHandler()

    handler.setFormatter(mozlog.logger.MozFormatter(include_timestamp=True))

    verbose = options.verbose
    if not verbose:
        try:
            verbose = cfg.getboolean('log', 'verbose')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            verbose = False

    log = mozlog.getLogger('bugzfeed', handler=handler)
    if verbose:
        log.setLevel(mozlog.DEBUG)
    else:
        log.setLevel(mozlog.INFO)
    return log


def main(cfgfile, options):
    cfg = ConfigParser.ConfigParser()
    cfg.read(cfgfile)
    log = setup_logging(cfg, options)
    pulse_cfg = load_pulse_cfg(cfg)
    port = cfg.getint('server', 'port')
    ioloop = tornado.ioloop.IOLoop.instance()
    def bug_updated(updates):
        ioloop.add_callback(subscriptions().update, updates)
    log.info('Starting Pulse listener.')
    listener = ListenerThread(pulse_cfg, bug_updated)
    listener.start()
    log.info('Starting WebSocket server.')
    application.listen(port)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        return


def cli():
    parser = optparse.OptionParser(usage='%prog [options] <config file>')
    parser.add_option('-v', '--verbose', action='store_true', default=False,
                        help='output debug messages')
    (options, args) = parser.parse_args()
    if not args:
        parser.print_usage()
        sys.exit(1)
    main(args[0], options)


if __name__ == '__main__':
    cli()

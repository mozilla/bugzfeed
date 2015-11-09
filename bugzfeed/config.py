import os
import socket

# Configuration is set via environment variables.
pulse_cfg = {}

pulse_cfg['host'] = os.getenv('PULSE_HOST', 'pulse.mozilla.org')
pulse_cfg['vhost'] = os.getenv('PULSE_VHOST', '/')
pulse_cfg['user'] = os.getenv('PULSE_USER', 'bugzfeed')
pulse_cfg['password'] = os.getenv('PULSE_PASSWORD', None)
pulse_cfg['durable'] = bool(int(os.getenv('PULSE_DURABLE', 0)))
pulse_cfg['applabel'] = os.getenv('PULSE_APPLABEL',
                                  'bugzfeed-%s' % socket.gethostname())
pulse_bugzfeed_dev = bool(int(os.getenv('PULSE_BUGZFEED_DEV', 0)))
database_url = os.getenv('DATABASE_URL', None)
max_messages = int(os.getenv('MAX_MESSAGES', 10000))

if pulse_cfg['password'] is None:
    raise Exception('PULSE_PASSWORD must be set.')
elif database_url is None:
    raise Exception('DATABASE_URL must be set.')

from __future__ import with_statement

import subprocess
import time
import optparse
from daemon import DaemonContext

from ConfigParser import SafeConfigParser

from calabar.tunnels import TunnelManager
from calabar.tunnels.vpnc import VpncTunnel

VPNC_CONF = '/etc/calabar/default.conf'
CALABAR_CONF = '/etc/calabar/calabar.conf'

OPTION_LIST = (
    optparse.make_option('-c', '--configfile', action="store", dest="configfile",
                         default=CALABAR_CONF,
                         help="The vpnc configuration file to use"),
    optparse.make_option('-d', '--daemon', action="store_true", dest="daemon",
                         default=False,
                         help="Run in the background as a daemon"),
)


def run_tunnels(configfile='/etc/calabar/calabar.conf', daemon=False):
    """Run the configured VPN/SSH tunnels and keep them running"""
    config = SafeConfigParser()
    config.read(configfile)

    tm = TunnelManager()
    if daemon:
        with DaemonContext():
            _run_tunnels(tm, config)
    else:
        _run_tunnels(tm, config)

def _run_tunnels(tm, config):
    tm.load_tunnels(config)

    tm.start_tunnels()

    while True:
        tm.continue_tunnels()
        time.sleep(5)

def parse_options(arguments):
    """Parse the available options to ``calabard``."""
    parser = optparse.OptionParser(option_list=OPTION_LIST)
    options, values = parser.parse_args(arguments)

    return options
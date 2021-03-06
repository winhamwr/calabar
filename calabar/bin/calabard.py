from __future__ import with_statement

import subprocess
import time
import optparse
import os
import sys

from ConfigParser import SafeConfigParser

from calabar.tunnels import TunnelManager
from calabar.tunnels.vpnc import VpncTunnel

VPNC_CONF = '/etc/calabar/default.conf'
CALABAR_CONF = '/etc/calabar/calabar.conf'

OPTION_LIST = (
    optparse.make_option('-c', '--configfile', action="store", dest="configfile",
                         default=CALABAR_CONF,
                         help="The vpnc configuration file to use"),
)

def run_tunnels(configfile='/etc/calabar/calabar.conf'):
    """Run the configured VPN/SSH tunnels and keep them running"""
    config = SafeConfigParser()
    config.read(configfile)

    tm = TunnelManager()
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
import subprocess
import time
import optparse
from ConfigParser import ConfigParser

from calabar.tunnels import TunnelManager
from calabar.tunnels.vpnc import VpncTunnel

VPNC = 'vpnc'
VPNC_CONF = '/etc/calabar/default.conf'

OPTION_LIST = (
    optparse.make_option('-c', '--configfile', action="store", dest="configfile",
                         default=VPNC_CONF,
                         help="The vpnc configuration file to use"),
)


def run_tunnels(configfile=VPNC_CONF):
    """Run the configured VPN/SSH tunnels and keep them running"""
    tm = TunnelManager(configfile)
    t = VpncTunnel(configfile)
    tm.t = t
    tm.start_tunnels()

    while True:
        tm.continue_tunnels()
        time.sleep(5)


def parse_options(arguments):
    """Parse the available options to ``calabard``."""
    parser = optparse.OptionParser(option_list=OPTION_LIST)
    options, values = parser.parse_args(arguments)

    return options
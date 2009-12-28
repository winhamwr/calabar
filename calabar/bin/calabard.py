from __future__ import with_statement

import subprocess
import time
import optparse
from daemon import DaemonContext

from ConfigParser import SafeConfigParser

from calabar.log import setup_logger, redirect_stdouts_to_logger
from calabar.tunnels import TunnelManager
from calabar.tunnels.vpnc import VpncTunnel

LOGFILE = '/var/log/calabar.log'
VPNC_CONF = '/etc/calabar/default.conf'
CALABAR_CONF = '/etc/calabar/calabar.conf'

OPTION_LIST = (
    optparse.make_option('-c', '--configfile', action="store", dest="configfile",
                         default=CALABAR_CONF,
                         help="The vpnc configuration file to use"),
    optparse.make_option('-d', '--daemon', action="store_true", dest="daemon",
                         default=False,
                         help="Run in the background as a daemon"),
    optparse.make_option('-f', '--logfile', default=LOGFILE,
                         action="store", dest="logfile",
                         help="Path to log file."),
)


def run_tunnels(configfile='/etc/calabar/calabar.conf', daemon=False,
                logfile=LOGFILE):
    """Run the configured VPN/SSH tunnels and keep them running"""
    config = SafeConfigParser()
    config.read(configfile)

    tm = TunnelManager()
    if daemon:
        # Since without stderr any errors will be silently suppressed,
        # we need to know that we have access to the logfile
        if logfile:
            open(logfile, "a").close()
        with DaemonContext():
            logger = setup_logger(logfile=logfile)
            redirect_stdouts_to_logger(logger)

            _run_tunnels(tm, config)
    else:
        logger = setup_logger(logfile=logfile)
        redirect_stdouts_to_logger(logger)
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
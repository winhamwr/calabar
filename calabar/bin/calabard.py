import subprocess
import time
import optparse
from ConfigParser import ConfigParser

VPNC = 'vpnc'
VPNC_CONF = '/etc/calabar/default.conf'

OPTION_LIST = (
    optparse.make_option('-c', '--configfile', action="store", dest="configfile",
                         default=VPNC_CONF,
                         help="The vpnc configuration file to use"),
)

class TunnelManager():
    def __init__(self, conf):
        """
        Create a new ``TunnelManager`` using the given ConfigParser.
        """
        self.conf = conf
        self._load_conf(self.conf)

    def _load_conf(self, conf):
        """
        Load all of the appropriate options from the ConfigParser.
        """
        pass

    def start_tunnels(self):
        """
        Start all of the configured tunnels and register to keep them running.
        """
        pass


def run_tunnels(configfile=VPNC_CONF):
    """Run the configured VPN/SSH tunnels and keep them running"""

    cmd = ['calabar_vpnc', configfile, '--no-detach']
    proc = subprocess.Popen(cmd, executable=VPNC)

    while True:
        proc.poll()
        if proc.returncode:
            print "VPNC EXITED"
            break
        else:
            print "proc: %s running" % proc.pid
        time.sleep(5)


def parse_options(arguments):
    """Parse the available options to ``calabard``."""
    parser = optparse.OptionParser(option_list=OPTION_LIST)
    options, values = parser.parse_args(arguments)

    return options
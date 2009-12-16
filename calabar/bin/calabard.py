import subprocess
import time
import optparse

VPNC = 'vpnc'
VPNC_CONF = '/etc/calabar/default.conf'

OPTION_LIST = (
    optparse.make_option('-c', '--configfile', action="store", dest="configfile",
                         default=VPNC_CONF,
                         help="The vpnc configuration file to use"),
)

def run_tunnels(configfile=VPNC_CONF):
    """Run the configured VPN/SSH tunnels and keep them running"""

    cmd = ['calabar_vpnc', configfile, '--no-detach']
    proc = subprocess.Popen(cmd, executable=VPNC)

    while True:
        return_code = proc.poll()
        if return_code:
            print "VPNC EXITED"
            break
        time.sleep(5)


def parse_options(arguments):
    """Parse the available options to ``calabard``."""
    parser = optparse.OptionParser(option_list=OPTION_LIST)
    options, values = parser.parse_args(arguments)

    return options
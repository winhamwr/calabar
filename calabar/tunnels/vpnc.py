from calabar.tunnels.base import TunnelBase

class VpncTunnel(TunnelBase):
    TYPE = 'vpnc'
    PROC_NAME = 'calabar_vpnc'
    EXEC = '/usr/sbin/vpnc'

    def __init__(self, conf_file, executable=None, *args, **kwargs):
        """
        Create a new vpnc tunnel using the given vpn configuration file.
        """
        self.conf_file = conf_file

        cmd = self._build_cmd(self.conf_file)
        if not executable:
            executable = VpncTunnel.EXEC

        super(VpncTunnel, self).__init__(cmd, executable, *args, **kwargs)

    def _build_cmd(self, conf_file):
        """
        Build the command that subprocess will execute in order to start the
        vpnc tunnel process.

        Command is in the format [<proccess_display_name>, <arg>...]
        """
        cmd = [VpncTunnel.PROC_NAME, conf_file]

        stay_in_foreground = ['--no-detach']
        random_port = ['--local-port', '0']
        non_interactive = ['--non-inter']

        cmd += stay_in_foreground + random_port + non_interactive

        return cmd

    @staticmethod
    def parse_configuration(config, section_name):
        """
        Parse out the required tunnel information from the given
        :mod:ConfigParser.ConfigParser instance, with this tunnel being
        represented by the tunnel at ``section_name``.

        Returns a dictionary with options corresponding to those taken by
        :member:`__init__`
        """
        tun_conf_d = {} # Tunnel configuration directory
        tun_conf_d['type'] = VpncTunnel.TYPE
        tun_conf_d['conf'] = config.get(section_name, 'conf')

        # Optional parts
        tun_conf_d['ips'] = []
        if config.has_option(section_name, 'ips'):
            tun_conf_d['ips'] = config.get(section_name, 'ips')

        # Get the binary/executable for VPNC
        tun_conf_d['executable'] = None
        if config.has_option(VpncTunnel.TYPE, 'bin'):
            tun_conf_d['executable'] = config.get(VpncTunnel.TYPE, 'bin')

        return tun_conf_d
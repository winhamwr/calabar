from calabar.tunnels.base import TunnelBase

class VpncTunnel(TunnelBase):
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
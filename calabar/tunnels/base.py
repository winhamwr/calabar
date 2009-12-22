import subprocess
import os
import signal

from calabar.tunnels import TUN_TYPE_STR, ExecutableNotFound, TunnelTypeDoesNotMatch, is_really_running

class TunnelBase(object):
    TUNNEL_TYPE = 'base'

    def __init__(self, cmd, executable, name='default', tunnel_type=None):
        """
        Create a tunnel that's opened using the given command and executable.

        ``cmd`` is a list of command arguments with the first argument being the
        display name that the tunnel process should use eg ``calabar_vpnc``
        ``executable`` is a path to the executable file that will be used to
        create the tunnel eg. ``/usr/sbin/vpnc``
        ``name`` will be this tunnels string identifier.
        ``tun_type`` if given, must match :attr:`TunnelBase.TYPE` or a
        :exc:`TunnelTypeDoesNotMatch` exception will be raised.
        """
        self.cmd = cmd
        self.executable = executable
        self.proc = None
        self.name = name
        if tunnel_type and tunnel_type != TunnelBase.TUNNEL_TYPE:
            raise TunnelTypeDoesNotMatch(
                'Tunnel type <%s> does not match expected <%s>' % (tunnel_type, TunnelBase.TUNNEL_TYPE))
        self.closing = False # Are we currently trying to close this tunnel
        self.opening = False # Not currently trying to open this tunnel

    def open(self):
        """
        Open the tunnel.
        """
        if not which(self.executable):
            raise ExecutableNotFound("The executable <%s> in invalid. Not found or not marked executable." % repr(self.executable))

        self.closing = False
        self.opening = True
        self.proc = self._open(self.cmd, self.executable)

        return self.proc

    def _open(self, cmd, executable):
        """
        Perform the actual process launch using the command and executable
        configured for this tunnel.
        """
        proc = subprocess.Popen(cmd, executable=executable)

        return proc

    def is_running(self):
        if self.proc:
            return is_really_running(self)
        else:
            return False

    def close(self, wait=True, force=False):
        """
        Close this tunnel if currently running and waits for it to finish closing.

        If ``force`` is given as True, close using :mod:signal.SIGKILL to force a close.
        """
        self.closing = True
        self.opening = False
        if self.is_running():
            sig = signal.SIGTERM
            if force:
                sig = signal.SIGKILL

            os.kill(self.proc.pid, sig)
            if wait:
                self.proc.wait()

    def handle_closed(self, exit_status):
        """
        Handle the tunnel process having closed externally. There was probably
        some sort of error.
        """
        self.closing = False
        self.opening = False
        self.proc = None

    @staticmethod
    def parse_configuration(config, section_name):
        """
        Parse out the required tunnel information from the given
        :mod:ConfigParser.ConfigParser instance, with this tunnel being
        represented by the tunnel at ``section_name``.

        Returns a dictionary with options corresponding to those taken by
        :member:`__init__`
        """
        tun_conf_d = {}
        tun_conf_d[TUN_TYPE_STR] = TunnelBase.TUNNEL_TYPE
        cmd = config.get(section_name, 'cmd')
        tun_conf_d['cmd'] = cmd.split()
        tun_conf_d['executable'] = config.get(section_name, 'executable')

        return tun_conf_d


def which(program):
    """
    Determine where the given executable exists on the path (if it exists). Mimics
    the behavior of the gnu ``which`` command.

    Returns ``None`` if the executable is not found.

    Taken from: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

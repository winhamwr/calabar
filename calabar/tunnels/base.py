import subprocess
import os
import signal

class TunnelBase(object):
    def __init__(self, cmd, executable):
        """
        Create a tunnel that's opened using the given command and executable.

        ``cmd`` is a list of command arguments with the first argument being the
        display name that the tunnel process should use eg ``calabar_vpnc``
        ``executable`` is a path to the executable file that will be used to
        create the tunnel eg. ``/usr/sbin/vpnc``
        """
        self.cmd = cmd
        self.executable = executable

    def open(self):
        """
        Open the tunnel. Returns True on successful opening.
        """
        self.proc = self._open(self.cmd, self.executable)
        if self.proc:
            return True
        return False

    def _open(self, cmd, executable):
        """
        Perform the actual process launch using the command and executable
        configured for this tunnel.
        """
        try:
            proc = subprocess.Popen(cmd, executable=executable)
        except OSError:
            proc = None

        return proc

    def is_running(self):
        if self.proc:
            return self.proc.poll() == None
        else:
            return False

    def close(self, wait=True, force=False):
        """
        Close this tunnel if currently running and waits for it to finish closing.

        If ``force`` is given as True, close using SIGKILL to force a close.
        """
        if self.is_running():
            sig = signal.SIGTERM
            if force:
                sig = signal.SIGKILL

            os.kill(self.proc.pid, sig)
            if wait:
                self.proc.wait()
import subprocess
import os
import signal

class ExecutableNotFound(Exception):
    """
    The given tunnel executable wasn't found or isn't executable.
    """
    pass

class TunnelBase(object):
    def __init__(self, cmd, executable, name='default'):
        """
        Create a tunnel that's opened using the given command and executable.

        ``cmd`` is a list of command arguments with the first argument being the
        display name that the tunnel process should use eg ``calabar_vpnc``
        ``executable`` is a path to the executable file that will be used to
        create the tunnel eg. ``/usr/sbin/vpnc``
        """
        self.cmd = cmd
        self.executable = executable
        self.proc = None
        self.name = name

    def open(self):
        """
        Open the tunnel. Returns True on successful opening.
        """
        if not which(self.executable):
            raise ExecutableNotFound("The executable <%s> in invalid. Not found or not marked executable." % repr(self.executable))
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
            print "OSError running tunnel"
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

        If ``force`` is given as True, close using :mod:signal.SIGKILL to force a close.
        """
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
        self.proc = None


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

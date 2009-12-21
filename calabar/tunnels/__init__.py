"""
calabar.tunnels

This module encapsulates various tunnel processes and their management.
"""

import signal
import os

from calabar.tunnels.vpnc import VpncTunnel

class TunnelManager():
    def __init__(self, conf):
        """
        Create a new ``TunnelManager`` using the given ConfigParser.
        """
        self.conf = conf
        self._load_conf(self.conf)
        self._register_for_close()

    def _load_conf(self, conf):
        """
        Load all of the appropriate options from the ConfigParser.
        """
        pass

    def start_tunnels(self):
        """
        Start all of the configured tunnels and register to keep them running.
        """
        self.t.open()

    def continue_tunnels(self):
        """
        Ensure that all of the tunnels are still running.
        """
        if not self.t.is_running():
            print "TUNNEL EXITED"
            print "RESTARTING"
            self.t.open()
        else:
            print "proc: %s running" % self.t.proc.pid

    def _register_for_close(self):
        """
        Register the child tunnel process for a close event. This keeps process
        from becoming defunct.
        """
        signal.signal(signal.SIGCHLD, self._handle_child_close)

    def _handle_child_close(self, signum, frame):
        """
        Handle a closed child.

        Call :mod:os.wait() on the process so that it's not defunct.
        """
        assert signum == signal.SIGCHLD

        print "CHILD TUNNEL CLOSED"
        pid, exit_status = os.wait()

        if self.t.proc and self.t.proc.pid == pid:
            self.t.handle_closed(exit_status)


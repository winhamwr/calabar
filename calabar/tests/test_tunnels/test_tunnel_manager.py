import unittest
import os
import psi.process
import subprocess
import time
import signal

from calabar.tunnels import TunnelManager
from calabar.tunnels.base import TunnelBase

PROC_NOT_RUNNING = [
    psi.process.PROC_STATUS_DEAD,
    psi.process.PROC_STATUS_ZOMBIE,
    psi.process.PROC_STATUS_STOPPED
]
def is_really_running(tunnel):
    if tunnel.proc:
        pt = psi.process.ProcessTable()
        proc = pt[tunnel.proc.pid]
        status = proc.status
        if not status in PROC_NOT_RUNNING:
            return True

    return False


class TestStartingSingleTunnel(unittest.TestCase):

    def setUp(self):
        self.executable = 'cal_run_forever'
        self.cmd = [self.executable]

        self.t = TunnelBase(self.cmd, self.executable)

        self.tm = TunnelManager('foo')
        self.tm.t = self.t

    def tearDown(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        try:
            subprocess.call("ps auxww | grep %s | awk '{print $2}' | xargs kill" % self.executable, shell=True)
        except OSError:
            pass

    def test_start_success(self):
        self.tm.start_tunnels()

        self.assertTrue(self.tm.t.is_running())

    def test_continue_not_started(self):
        """
        Calling continue before starting shouldn't error out
        """
        self.tm.continue_tunnels()

    def test_continue_post_start(self):
        self.tm.start_tunnels()

        self.tm.continue_tunnels()
        self.assertTrue(self.tm.t.is_running())

    def test_vanilla_continue(self):
        self.tm.start_tunnels()
        self.tm.continue_tunnels()

        self.assertTrue(self.tm.t.is_running())

    def test_close(self):
        self.tm.start_tunnels()

        self.tm.t.close(wait=False)


    def test_continue_after_kill(self):
        self.tm.start_tunnels()

        self.tm.t.close(wait=False)

        self.tm.continue_tunnels()
        time.sleep(.5)
        self.tm.continue_tunnels()

        self.assertTrue(is_really_running(self.tm.t))


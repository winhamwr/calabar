import unittest
import subprocess
import os
import signal
import time

from calabar.tunnels.base import TunnelBase, ExecutableNotFound, TunnelTypeDoesNotMatch

class TestInvalidTunnel(unittest.TestCase):
    def setUp(self):
        cmd = ['ls']
        executable = 'lsDOESNOTEXIST'

        self.t = TunnelBase(cmd, executable)

    def test_open_fail(self):
        """
        Test that ``TunnelBase.open`` returns ``False`` on a failed process
        open.

        Uses the ``ls`` unix program since it will return right away.
        """
        self.assertRaises(ExecutableNotFound, self.t.open)

    def test_isrunning_failure(self):
        """
        Test that TunnelBase.is_running correctly detects a process that failed
        to run.
        """
        self.assertRaises(ExecutableNotFound, self.t.open)

        is_running = self.t.is_running()

        self.assertFalse(is_running, 'ls should not be running')

    def test_close_failure(self):
        """
        Test that calling ``TunnelBase.close`` on a process that failed to start
        doesn't throw any errors.
        """
        self.assertRaises(ExecutableNotFound, self.t.open)

        self.t.close()
        self.t.close(force=True)
        self.assertFalse(self.t.is_running())


class TestInvalidConf(unittest.TestCase):

    def test_invalid_type(self):
        self.assertRaises(TunnelTypeDoesNotMatch, TunnelBase,
                          *[None, None], **{'tunnel_type':'invalid'})


class TestValidTunnel(unittest.TestCase):
    def setUp(self):
        self.executable = 'cal_run_forever'
        self.cmd = [self.executable]

        self.t = TunnelBase(self.cmd, self.executable)

    def tearDown(self):
        subprocess.call(['killall', self.executable])

    def test_open_proc(self):
        """
        Test that ``TunnelBase.open`` returns the Popen object on a successful process
        open and also sets the proc attribute.
        """
        proc = self.t.open()
        self.assertNotEqual(proc, None)
        self.assertEqual(proc, self.t.proc)

    def test_isrunning_success(self):
        """
        Test that TunnelBase.is_running correctly detects a currently running process.
        """
        proc = self.t.open()
        is_running = self.t.is_running()

        self.assertTrue(is_running, '%s should still be running' % self.executable)

    def test_isrunning_closed(self):
        """
        Test that TunnelBase.is_running correctly detects a process that has been
        closed.
        """
        proc = self.t.open()
        os.kill(self.t.proc.pid, signal.SIGKILL)
        self.t.proc.wait() # Wait for the process to close

        is_running = self.t.is_running()

        self.assertFalse(is_running, '%s should not be running' % self.executable)

    def test_close_running(self):
        """
        Test that calling ``TunnelBase.close`` on a running process actually
        closes it.
        """
        proc = self.t.open()
        self.t.close()

        is_running = self.t.is_running()
        self.assertFalse(is_running)

    def test_close_running_force(self):
        """
        Test that calling ``TunnelBase.close`` with force=True on a running
        process actually closes it.
        """
        proc = self.t.open()
        self.t.close(force=True)

        is_running = self.t.is_running()
        self.assertFalse(is_running)

    def test_close_already_closed(self):
        """
        Test that calling ``TunnelBase.close`` on a process that is already
        closed doesn't throw any errors.
        """
        proc = self.t.open()
        os.kill(self.t.proc.pid, signal.SIGKILL)
        self.t.proc.wait()

        self.t.close()
        self.t.close(force=True)
        self.assertFalse(self.t.is_running())
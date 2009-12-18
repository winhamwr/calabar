import unittest

from calabar.tunnels.base import TunnelBase

class MockPopen(object):
    def __init__(self, cmd, executable):
        self.pid = 1
        self.returncode = None

    def poll(self):
        return self.returncode

    def kill(self):
        self.returncode = 0

class TestTunnelBase(unittest.TestCase):

    def test_open_success(self):
        """
        Test that ``TunnelBase.open`` returns ``True`` on a successful process
        open.

        Uses the ``top`` unix program.
        """
        cmd = ['ls']
        executable = 'ls'

        t = TunnelBase(cmd, executable)

        success = t.open()
        self.assertTrue(success, "ls should have successfully opened")

    def test_open_fail(self):
        """
        Test that ``TunnelBase.open`` returns ``False`` on a failed process
        open.

        Uses the ``ls`` unix program since it will return right away.
        """
        cmd = ['ls']
        executable = 'lsDOESNOTEXIST'

        t = TunnelBase(cmd, executable)

        success = t.open()
        self.assertFalse(success, "ls shouldn't be running")




import unittest
import os
import psi.process
import subprocess
import time
import signal
from ConfigParser import SafeConfigParser

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
        proc = pt.get(tunnel.proc.pid, None)
        if proc:
            status = proc.status
            if not status in PROC_NOT_RUNNING:
                return True

    return False


class TestStartingSingleTunnel(unittest.TestCase):

    def setUp(self):
        self.executable = 'cal_run_forever'
        self.cmd = [self.executable]

        self.t = TunnelBase(self.cmd, self.executable)

        self.tm = TunnelManager()
        self.tm.tunnels = [self.t]

    def tearDown(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        try:
            subprocess.call("ps auxww | grep %s | awk '{print $2}' | xargs kill" % self.executable, shell=True)
        except OSError:
            pass

    def test_start_success(self):
        self.tm.start_tunnels()

        self.assertTrue(self.t.is_running())

    def test_continue_not_started(self):
        """
        Calling continue before starting shouldn't error out
        """
        self.tm.continue_tunnels()

    def test_continue_post_start(self):
        self.tm.start_tunnels()

        self.tm.continue_tunnels()
        self.assertTrue(self.t.is_running())

    def test_vanilla_continue(self):
        self.tm.start_tunnels()
        self.tm.continue_tunnels()

        self.assertTrue(self.t.is_running())

    def test_close(self):
        self.tm.start_tunnels()

        self.t.close(wait=False)


    def test_continue_after_kill(self):
        self.tm.start_tunnels()

        self.t.close(wait=False)

        self.tm.continue_tunnels()
        time.sleep(.5)
        self.tm.continue_tunnels()

        self.assertTrue(is_really_running(self.t))


class TestVpncParserOpts(unittest.TestCase):
    """Test that various options don't throw errors parsing"""

    def test_minimums(self):
        self.conf = SafeConfigParser()
        self.sec1 = 'tunnel:testvpnc'
        self.conf.add_section(self.sec1)
        self.conf.set(self.sec1, 'type', 'vpnc')
        self.conf.set(self.sec1, 'conf', '/path/to/conf.conf')

        tm = TunnelManager()
        tm.load_tunnels(self.conf)

        self.assertEqual(len(tm.tunnels), 1)

class TestVpncParser(unittest.TestCase):

    def setUp(self):
        self.conf = SafeConfigParser()
        self.sec1 = 'tunnel:testvpnc'
        self.conf.add_section(self.sec1)
        self.conf.set(self.sec1, 'type', 'vpnc')
        self.conf.set(self.sec1, 'conf', '/path/to/conf.conf')
        self.conf.set(self.sec1, 'ips', '10.10.10.10, 5.5.5.5')

        self.vpnc_sec = 'vpnc'
        self.conf.add_section(self.vpnc_sec)
        self.conf.set(self.vpnc_sec, 'bin', '/path/to/vpnc.bin')
        self.conf.set(self.vpnc_sec, 'base_conn_script', '/path/to/vpnc-conn-script')

        self.tm = TunnelManager()

    def test_base_parse(self):
        self.tm.load_tunnels(self.conf)
        self.assertEqual(len(self.tm.tunnels), 1)

    def test_name(self):
        self.tm.load_tunnels(self.conf)
        t = self.tm.tunnels[0]

        self.assertEqual(t.name, 'testvpnc')

    def test_cmd(self):
        self.tm.load_tunnels(self.conf)
        t = self.tm.tunnels[0]

        self.assertEqual(t.cmd, ['calabar_vpnc', '/path/to/conf.conf', '--no-detach', '--local-port', '0', '--non-inter'])

    def test_executable(self):
        self.tm.load_tunnels(self.conf)
        t = self.tm.tunnels[0]

        self.assertEqual(t.executable, '/path/to/vpnc.bin')


class TestBaseParser(unittest.TestCase):

    def setUp(self):
        self.executable = 'cal_run_forever'

        self.conf = SafeConfigParser()
        self.sec1 = 'tunnel:test'
        self.conf.add_section(self.sec1)
        self.conf.set(self.sec1, 'type', 'base')
        self.conf.set(self.sec1, 'cmd', self.executable)
        self.conf.set(self.sec1, 'executable', self.executable)

        self.tm = TunnelManager()

    def test_base_parse(self):
        self.tm.load_tunnels(self.conf)
        self.tm.start_tunnels()

    def test_name(self):
        self.tm.load_tunnels(self.conf)
        t = self.tm.tunnels[0]

        self.assertEqual(t.name, 'test')

    def test_cmd(self):
        self.tm.load_tunnels(self.conf)
        t = self.tm.tunnels[0]

        self.assertEqual(t.cmd, [self.executable])

    def test_executable(self):
        self.tm.load_tunnels(self.conf)
        t = self.tm.tunnels[0]

        self.assertEqual(t.executable, self.executable)

    def test_runs(self):
        self.tm.load_tunnels(self.conf)
        t = self.tm.tunnels[0]

        self.tm.start_tunnels()

        self.assertTrue(t.is_running())

class TestTunnelConf(TestStartingSingleTunnel):
    """
    Run the same tests as TestStartingSingleTunnel, only do them with a tunnel
    loaded from the configuration file.
    """

    def setUp(self):
        self.executable = 'cal_run_forever'

        conf = SafeConfigParser()
        sec1 = 'tunnel:test'
        conf.add_section(sec1)
        conf.set(sec1, 'type', 'base')
        conf.set(sec1, 'cmd', self.executable)
        conf.set(sec1, 'executable', self.executable)

        self.tm = TunnelManager()
        self.tm.load_tunnels(conf)
        self.tm.start_tunnels()

        self.t = self.tm.tunnels[0]


class TestLongRun(unittest.TestCase):

    def setUp(self):
        self.executable = 'cal_run_forever'
        self.cmd = [self.executable]

        self.t = TunnelBase(self.cmd, self.executable)

        self.tm = TunnelManager()
        self.tm.tunnels = [self.t]

    def tearDown(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        try:
            subprocess.call("ps auxww | grep %s | awk '{print $2}' | xargs kill" % self.executable, shell=True)
        except OSError:
            pass

    def test_single_run(self):
        self.tm.start_tunnels()
        self.tm.continue_tunnels()
        time.sleep(1)

        self.assertTrue(is_really_running(self.t))

class TestLongRunConf(TestLongRun):
    """
    Run the same tests as TestLongRun, only do them with a tunnel
    loaded from the configuration file.
    """

    def setUp(self):
        self.executable = 'cal_run_forever'

        conf = SafeConfigParser()
        sec1 = 'tunnel:test'
        conf.add_section(sec1)
        conf.set(sec1, 'type', 'base')
        conf.set(sec1, 'cmd', self.executable)
        conf.set(sec1, 'executable', self.executable)

        self.tm = TunnelManager()
        self.tm.load_tunnels(conf)

        self.t = self.tm.tunnels[0]
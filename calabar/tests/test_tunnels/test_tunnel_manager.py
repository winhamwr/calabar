import unittest
import os
import psi.process
import subprocess
import time
import signal
from ConfigParser import SafeConfigParser

from calabar.tunnels import TunnelManager, TunnelsAlreadyLoadedException, ExecutableNotFound
from calabar.tunnels.base import TunnelBase, which

PROC_NOT_RUNNING = [
    psi.process.PROC_STATUS_DEAD,
    psi.process.PROC_STATUS_ZOMBIE,
    psi.process.PROC_STATUS_STOPPED
]
def is_really_running(tunnel):
    pt = psi.process.ProcessTable()
    try:
        proc = pt.get(tunnel.proc.pid, None)
    except AttributeError:
        # we might not actually have a tunnel.proc or it might poof while we're checking
        return False
    if proc:
        status = proc.status
        if not status in PROC_NOT_RUNNING:
            return True

    return False

class TearDownRunForever(unittest.TestCase):
    def tearDown(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        try:
            subprocess.call("ps auxww | grep %s | awk '{print $2}' | xargs kill" % self.executable, shell=True)
        except OSError:
            pass

class TestStartingSingleTunnel(TearDownRunForever):

    def setUp(self):
        self.executable = 'cal_run_forever'
        self.cmd = [self.executable]

        self.t = TunnelBase(self.cmd, self.executable)

        self.tm = TunnelManager()
        self.tm.tunnels = [self.t]

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


class TestVpncParserOpts(unittest.TestCase):
    """Test that various options don't throw errors parsing"""

    def test_minimums(self):
        self.conf = SafeConfigParser()
        self.sec1 = 'tunnel:testvpnc'
        self.conf.add_section(self.sec1)
        self.conf.set(self.sec1, 'tunnel_type', 'vpnc')
        self.conf.set(self.sec1, 'conf_file', '/path/to/conf.conf')

        tm = TunnelManager()
        tm.load_tunnels(self.conf)

        self.assertEqual(len(tm.tunnels), 1)

class TestVpncParser(unittest.TestCase):

    def setUp(self):
        self.conf = SafeConfigParser()
        self.sec1 = 'tunnel:testvpnc'
        self.conf.add_section(self.sec1)
        self.conf.set(self.sec1, 'tunnel_type', 'vpnc')
        self.conf.set(self.sec1, 'conf_file', '/path/to/conf.conf')
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

        expected_cmd = ['calabar_vpnc', '/path/to/conf.conf', '--no-detach',
                        '--local-port', '0', '--non-inter', '--script']
        self.assertEqual(len(t.cmd), len(expected_cmd)+1) # +1 for the actual script

        for expected_arg in expected_cmd:
            self.assertTrue(expected_arg in t.cmd)

        # Now check the last arg and make sure it's to /tmp/...
        self.assertTrue(t.cmd[-1].startswith('/tmp/'))


    def test_executable(self):
        self.tm.load_tunnels(self.conf)
        t = self.tm.tunnels[0]

        self.assertEqual(t.executable, '/path/to/vpnc.bin')


class TestBaseParser(TearDownRunForever):

    def setUp(self):
        self.executable = 'cal_run_forever'

        self.conf = SafeConfigParser()
        self.sec1 = 'tunnel:test'
        self.conf.add_section(self.sec1)
        self.conf.set(self.sec1, 'tunnel_type', 'base')
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
    Run the same tests as TestStartingSingleTunnel with a tunnel
    loaded from the configuration file. Also adds a few extra tests.
    """

    def setUp(self):
        self.executable = 'cal_run_forever'

        conf = SafeConfigParser()
        sec1 = 'tunnel:test'
        conf.add_section(sec1)
        conf.set(sec1, 'tunnel_type', 'base')
        conf.set(sec1, 'cmd', self.executable)
        conf.set(sec1, 'executable', self.executable)

        self.tm = TunnelManager()
        self.tm.load_tunnels(conf)
        self.tm.start_tunnels()

        self.t = self.tm.tunnels[0]

    def test_already_loaded(self):
        conf = SafeConfigParser()
        self.assertRaises(TunnelsAlreadyLoadedException, self.tm.load_tunnels, *[conf])

class TestInvalidTunnelConfs(unittest.TestCase):

    def test_invalid_tunnel_type_conf(self):
        conf = SafeConfigParser()
        sec1 = 'tunnel:test'
        conf.add_section(sec1)
        conf.set(sec1, 'tunnel_type', 'INVALID')

        tm = TunnelManager()
        self.assertRaises(NotImplementedError, tm.load_tunnels, *[conf])

    def test_invalid_load_tunnel_type(self):
        tun_conf_d = {'tunnel_type': 'INVALID'}

        tm = TunnelManager()
        self.assertRaises(NotImplementedError, tm._load_tunnel, *['test', tun_conf_d])


class TestInvalidTunnels(unittest.TestCase):

    def setUp(self):
        self.tunnel = TunnelBase(['ls'], 'DOESNOTEXIST')

        self.tm = TunnelManager()
        self.tm.tunnels.append(self.tunnel)

    def test_start_bad_exec(self):
        self.tm.start_tunnels()
        # No error was raised
        self.assertFalse(self.tunnel.is_running())

    def test_continue_bad_exec(self):
        self.tm.continue_tunnels()
        # No error was raised
        self.assertFalse(self.tunnel.is_running())

class TestLongRun(TearDownRunForever):

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

    def test_close_running_externally_handled(self):
        self.tm.start_tunnels()

        proc = self.t.proc
        os.kill(proc.pid, signal.SIGTERM)
        # Wait for the process to close
        _wait_for_condition(lambda : not self.t.is_running(), "Process not closed")

        self.assertFalse(self.t.is_running())

    def test_continue_after_kill(self):
        self.tm.start_tunnels()

        self.t.close(wait=False)

        _wait_for_condition(lambda: not is_really_running(self.t), "Process not stopped")
        self.tm.continue_tunnels()
        _wait_for_condition(lambda: is_really_running(self.t), "Process not started")

        self.assertTrue(is_really_running(self.t))

def _wait_for_condition(cond, msg):
    """
    Wait up to 1 second in .1 second increments for the callable to return true,
    otherwise throw an error.
    """
    for x in range(11):
        if x == 10:
            self.fail(msg)
        if not cond():
            time.sleep(.1)
        else:
            print "time: %d" % (x*0.1)
            break

def test_which_fs():
    which_path = which('/bin/ls')

    assert which_path == '/bin/ls'
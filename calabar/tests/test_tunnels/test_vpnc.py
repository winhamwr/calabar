import unittest
import os
from ConfigParser import SafeConfigParser

from calabar.tunnels.vpnc import VpncTunnel
from calabar.tunnels import TunnelTypeDoesNotMatch

class TestDefaultTunnelConf(unittest.TestCase):
    def setUp(self):
        self.t = VpncTunnel(conf_file=None)

    def test_cmd_builder(self):
        """
        Test that ``VpncTunnel._build_cmd`` builds the proper command.
        """
        test_conf = '/tmp/test'
        expected_cmd = ['calabar_vpnc', test_conf]

        cmd = self.t._build_cmd(test_conf, None)
        self.assertTrue(cmd, expected_cmd)

    def test_executable(self):
        self.assertEqual(self.t.executable, '/usr/sbin/vpnc')

class TestConfigParsing(unittest.TestCase):

    def setUp(self):
        self.cp = SafeConfigParser()
        self.sec = 'tunnel:testvpnc'
        self.cp.add_section(self.sec)
        self.cp.set(self.sec, 'tunnel_type', 'vpnc')
        self.cp.set(self.sec, 'conf_file', '/path/to/conf.conf')
        self.cp.set(self.sec, 'ips', '192.168.3.50')

    def test_single_ip_parsing(self):
        tun_conf_d = VpncTunnel.parse_configuration(self.cp, self.sec)
        self.assertEqual(tun_conf_d['ips'], ['192.168.3.50'])

    def test_multiple_ip_parsing(self):
        self.cp.set(self.sec, 'ips', '192.168.3.50, 192.168.3.51')

        tun_conf_d = VpncTunnel.parse_configuration(self.cp, self.sec)
        self.assertEqual(tun_conf_d['ips'], ['192.168.3.50', '192.168.3.51'])

class TestSplitTunneling(unittest.TestCase):

    def setUp(self):
        self.cp = SafeConfigParser()
        self.sec = 'tunnel:testvpnc'
        self.cp.add_section(self.sec)
        self.cp.set(self.sec, 'tunnel_type', 'vpnc')
        self.cp.set(self.sec, 'conf_file', '/path/to/conf.conf')
        self.cp.set(self.sec, 'ips', '')

    def test_no_ip_contents(self):
        tun_conf_d = VpncTunnel.parse_configuration(self.cp, self.sec)
        t = VpncTunnel(**tun_conf_d)

        contents = t._tun_script
        self.assertEqual(contents.count('add_ip'), 1)

    def test_single_ip_contents(self):
        self.cp.set(self.sec, 'ips', '192.168.3.50')

        tun_conf_d = VpncTunnel.parse_configuration(self.cp, self.sec)
        t = VpncTunnel(**tun_conf_d)

        contents = t._tun_script
        self.assertEqual(contents.count('add_ip 192.168.3.50'), 1)

    def test_multiple_ip_contents(self):
        self.cp.set(self.sec, 'ips', '192.168.3.50, 8.8.8.8')

        tun_conf_d = VpncTunnel.parse_configuration(self.cp, self.sec)
        t = VpncTunnel(**tun_conf_d)

        contents = t._tun_script
        self.assertEqual(contents.count('add_ip 192.168.3.50'), 1)
        self.assertEqual(contents.count('add_ip 8.8.8.8'), 1)

    def test_file_exists(self):
        tun_conf_d = VpncTunnel.parse_configuration(self.cp, self.sec)
        t = VpncTunnel(**tun_conf_d)

        os.path.isfile(t.get_split_tunnel_script_fp())

    def test_file_executable(self):
        tun_conf_d = VpncTunnel.parse_configuration(self.cp, self.sec)
        t = VpncTunnel(**tun_conf_d)

        fp = t.get_split_tunnel_script_fp()
        isfile = os.path.isfile(fp)
        self.assertTrue(isfile and os.access(fp, os.X_OK))

class TestInvalidConf(unittest.TestCase):

    def test_invalid_type(self):
        self.assertRaises(TunnelTypeDoesNotMatch, VpncTunnel,
                          *[None], **{'tunnel_type':'invalid'})

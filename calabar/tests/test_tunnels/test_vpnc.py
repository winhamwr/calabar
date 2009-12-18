import unittest

from calabar.tunnels.vpnc import VpncTunnel

class TestDefaultTunnelConf(unittest.TestCase):
    def setUp(self):
        self.t = VpncTunnel(conf_file=None)

    def test_cmd_builder(self):
        """
        Test that ``VpncTunnel._build_cmd`` builds the proper command.
        """
        test_conf = '/tmp/test'
        expected_cmd = ['calabar_vpnc', test_conf]

        cmd = self.t._build_cmd(test_conf)
        self.assertTrue(cmd, expected_cmd)

    def test_executable(self):
        self.assertEqual(self.t.executable, '/usr/sbin/vpnc')

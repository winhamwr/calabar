"""
calabar.tunnels

This module encapsulates various tunnel processes and their management.
"""

import signal
import os
import sys
import psi.process

TUN_TYPE_STR = 'tunnel_type' # Configuration/dictionary key for the type of tunnel
# Should match the tunnel_type argument to Tunnel __init__ methods

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

class TunnelsAlreadyLoadedException(Exception):
    """Once tunnels are loaded the first time, other methods must be used to
    update them"""
    pass

class ExecutableNotFound(Exception):
    """
    The given tunnel executable wasn't found or isn't executable.
    """
    pass

class TunnelTypeDoesNotMatch(Exception):
    """
    The given ``tun_type`` doesn't match expected Tunnel.
    """
    pass

class TunnelManager():
    """
    A class for working with multiple :class:`calabar.tunnels.base.TunnelBase`
    tunnels.

    Creating this tunnels registers it for SIG_CHLD signals, so only ONE
    TunnelManager can exist at a time for purposes of keeping the other tunnels
    running.
    """
    def __init__(self):
        self.tunnels = []
        self._register_for_close()

    def load_tunnels(self, config):
        """
        Load config information to create all required tunnels.
        """
        if self.tunnels:
            raise TunnelsAlreadyLoadedException("TunnelManager.load_tunnels can't be called after tunnels have already been loaded. Use update_tunnels() instead")
        tun_confs_d = get_tunnels(config)

        for name, tun_conf_d in tun_confs_d.items():
            t = self._load_tunnel(name, tun_conf_d)
            self.tunnels.append(t)

    def _load_tunnel(self, tunnel_name, tun_conf_d):
        """
        Create and return a tunnel instance from a ``tun_conf_d`` dictionary.

        ``tun_conf_d`` is a dictionary matching the output of a tunnel's
        implementation of :mod:`calabar.tunnels.base.TunnelBase:parse_configuration`
        method.
        """
        from calabar.conf import TUNNELS
        tun_type = tun_conf_d[TUN_TYPE_STR]
        for tunnel in TUNNELS:
            if tunnel.TUNNEL_TYPE == tun_type:
                t = tunnel(name=tunnel_name, **tun_conf_d)
                return t

        raise NotImplementedError()

    def start_tunnels(self):
        """
        Start all of the configured tunnels and register to keep them running.
        """
        for t in self.tunnels:
            try:
                t.open()
            except ExecutableNotFound, e:
                print >> sys.stderr, e

    def continue_tunnels(self):
        """
        Ensure that all of the tunnels are still running.
        """
        for t in self.tunnels:
            if not t.is_running():
                print "TUNNEL [%s] EXITED" % t.name
                print "RESTARTING"
                try:
                    t.open()
                except ExecutableNotFound, e:
                    print >> sys.stderr, e
            else:
                print "[%s]:%s running" % (t.name, t.proc.pid)

    def _register_for_close(self):
        """
        Register the child tunnel process for a close event. This keeps process
        from becoming defunct.
        """
        signal.signal(signal.SIGCHLD, self._handle_child_close)

        # Register for a termination signal so we can clean up children
        signal.signal(signal.SIGTERM, self._handle_terminate)

    def _handle_terminate(self, signum, frame):
        for t in self.tunnels:
            t.close(wait=False)

        exit()

    def _handle_child_close(self, signum, frame):
        """
        Handle a closed child.

        Call :mod:os.wait() on the process so that it's not defunct.
        """
        assert signum == signal.SIGCHLD

        print "CHILD TUNNEL CLOSED"
        pid, exit_status = os.wait()

        for t in self.tunnels:
            # For all of the "closing" tunnels, if they've stopped running, handle the close
            if t.closing and not t.is_running():
                # Assume the same exit_status
                t.handle_closed(exit_status)



TUNNEL_PREFIX = 'tunnel:'

def get_tunnels(config):
    """
    Return a dictionary of dictionaries containg tunnel configurations based on the
    given SafeConfigParser instance.

    An example return value might be::

        {
            'foo':
                {
                    'tunnel_type': 'vpnc',
                    'conf_file': '/etc/calabar/foo.conf',
                    'ips': [10.10.254.1]
                },
            'bar':
                {
                    'tunnel_type': 'ssh',
                    'from': 'root@10.10.251.2:386',
                    'to': '127.0.0.1:387
                }
        }
    """
    tun_confs_d = {}

    for section in config.sections():
        if section.startswith(TUNNEL_PREFIX):
            tun_conf_d = parse_tunnel(config, section)

            tun_name = section[len(TUNNEL_PREFIX):]
            tun_confs_d[tun_name] = tun_conf_d

    return tun_confs_d

def parse_tunnel(config, section):
    """
    Parse the given ``section`` in the given ``config``
    :mod:`ConfigParser.ConfigParser` object to generate a tunnel configuration
    dictionary using all configured tunnel types and their configuration
    parsers.
    """
    from calabar.conf import TUNNELS
    tun_type = config.get(section, TUN_TYPE_STR)
    for tunnel in TUNNELS:
        if tun_type == tunnel.TUNNEL_TYPE:
            tun_conf_d = tunnel.parse_configuration(config, section)
            return tun_conf_d

    raise NotImplementedError("The tunnel type [%s] isn't supported" % tun_type)

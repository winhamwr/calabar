from __future__ import with_statement

import subprocess
import time
import optparse
import os
import sys

from daemon import DaemonContext
from ConfigParser import SafeConfigParser

from calabar.log import setup_logger, redirect_stdouts_to_logger
from calabar.tunnels import TunnelManager
from calabar.tunnels.vpnc import VpncTunnel

LOGFILE = '/var/log/calabar.log'
VPNC_CONF = '/etc/calabar/default.conf'
CALABAR_CONF = '/etc/calabar/calabar.conf'
DAEMON_PID_FILE = '/var/run/calabard.pid'

OPTION_LIST = (
    optparse.make_option('-c', '--configfile', action="store", dest="configfile",
                         default=CALABAR_CONF,
                         help="The vpnc configuration file to use"),
    optparse.make_option('-d', '--daemon', action="store_true", dest="daemon",
                         default=False,
                         help="Run in the background as a daemon"),
    optparse.make_option('-f', '--logfile', default=LOGFILE,
                         action="store", dest="logfile",
                         help="Path to log file."),
    optparse.make_option('-p', '--pidfile', default=DAEMON_PID_FILE,
            action="store", dest="pidfile",
            help="Path to pidfile."),
)

def create_pidlock(pidfile):
    """Create a PIDFile to be used with python-daemon.

    If the pidfile already exists the program exits with an error message,
    however if the process it refers to is not running anymore, the pidfile
    is just deleted.

    Taken from `celery`_
    """
    from daemon import pidlockfile
    from lockfile import LockFailed

    class PIDFile(object):

        def __init__(self, path):
            self.path = os.path.abspath(path)

        def __enter__(self):
            try:
                pidlockfile.write_pid_to_pidfile(self.path)
            except OSError, exc:
                raise LockFailed(str(exc))
            return self

        def __exit__(self, *_exc):
            self.release()

        def is_locked(self):
            return os.path.exists(self.path)

        def release(self):
            try:
                os.unlink(self.path)
            except OSError, exc:
                if exc.errno in (errno.ENOENT, errno.EACCES):
                    return
                raise

        def read_pid(self):
            return pidlockfile.read_pid_from_pidfile(self.path)

        def is_stale(self):
            pid = self.read_pid()
            try:
                os.kill(pid, 0)
            except os.error, exc:
                if exc.errno == errno.ESRCH:
                    sys.stderr.write("Stale pidfile exists. Removing it.\n")
                    self.release()
                    return True
            except TypeError, exc:
                sys.stderr.write("Broken pidfile found. Removing it.\n")
                self.release()
                return True
            return False

    pidlock = PIDFile(pidfile)
    if pidlock.is_locked() and not pidlock.is_stale():
        raise SystemExit(
                "ERROR: Pidfile (%s) already exists.\n"
                "Seems we're already running? (PID: %d)" % (
                    pidfile, pidlock.read_pid()))
    return pidlock

def run_tunnels(configfile='/etc/calabar/calabar.conf', daemon=False,
                logfile=LOGFILE, pidfile=DAEMON_PID_FILE):
    """Run the configured VPN/SSH tunnels and keep them running"""
    config = SafeConfigParser()
    config.read(configfile)

    tm = TunnelManager()
    if daemon:
        # Since without stderr any errors will be silently suppressed,
        # we need to know that we have access to the logfile
        if logfile:
            open(logfile, "a").close()
        pidlock = create_pidlock(pidfile)
        with DaemonContext(pidfile=pidlock):
            # Re-register the signals because python-daemon steals sigchld
            tm._register_for_close()
            logger = setup_logger(logfile=logfile)
            redirect_stdouts_to_logger(logger)

            _run_tunnels(tm, config)
    else:
        logger = setup_logger(logfile=logfile)
        #redirect_stdouts_to_logger(logger)
        _run_tunnels(tm, config)

def _run_tunnels(tm, config):
    tm.load_tunnels(config)

    tm.start_tunnels()

    while True:
        tm.continue_tunnels()
        time.sleep(5)

def parse_options(arguments):
    """Parse the available options to ``calabard``."""
    parser = optparse.OptionParser(option_list=OPTION_LIST)
    options, values = parser.parse_args(arguments)

    return options
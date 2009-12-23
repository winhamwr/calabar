====================
Configuring calabard
====================

``calabard`` follows the normal unixy convention os using text files for config.
By default, ``calabard`` looks for its configuration file at ``/etc/calabar/default.conf``.
This file tells ``calabard`` where to look for the various executables, which
tunnels to set up, how to set them up, etc.

Config File Format
==================

The config file conforms to the `ConfigParser`_ format, which is similar to
the Microsoft Windows INI file structure. It has one caveat though, in that
certain fields accept a list of `comma-separated values`_.

An example configuration file might be::

    [vpnc]
    bin = /usr/sbin/vpnc
    conn_script = /etc/vpnc/vpnc-script

    [tunnel:foo]
    tunnel_type = vpnc
    conf_file = /etc/calabar/foo.conf
    ips = 10.10.250.1, 192.168.10.2


.. _`ConfigParser`: http://docs.python.org/library/configparser.html
.. _`comma-separated values`: http://docs.python.org/library/csv.html


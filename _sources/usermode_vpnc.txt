==================================
Using VPNC With a Non-Root Account
==================================

::
    $ sudo apt-get install usermode
    $ sudo addgroup vpn
    $ sudo addgroup wes vpn
    # Make /etc/pam.d/vpnc
    # Make /etc/security/console.apps/vpnc
    $ sudo ln -s /usr/bin/consolehelper /usr/local/bin/vpnc
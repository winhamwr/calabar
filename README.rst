=====================================
 calabar - VPN and SSH Tunnel Manager
=====================================

:Version: 0.0.1

Introduction
============

Calabar helps you define and manage multiple split-tunnel VPN connections and
SSH tunnels over specific ports.

Example Problem
---------------

Calabar is meant to solve the following class of problem:

You need to connect to multiple remote LDAP servers over different VPNs
and then connect to those LDAP server as if they were local (to keep things
simple for your application). You want to keep those disparate VPNs up so that
you can continue accessing the different LDAP servers and you want to be able
to configure them on the fly so that a utrusted ser of your web app can enter
their VPN settings and be connected without requiring any downtime or sys admin
intervention. You also need to manage port forwarding so that tunnels don't
conflict.

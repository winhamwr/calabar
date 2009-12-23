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

What an Odd Name?
-----------------

The `Calabar Python`_ is also known as the African Burrowing Python. Since this
project is all about tunnelling, I figured that was as good a name as any. The
`City in Nigeria`_ is just an innocent bystander.

.. _`Calabar Python`: http://en.wikipedia.org/wiki/Calabar_Python
.. _`City in Nigeria`: http://en.wikipedia.org/wiki/Calabar

Installation
============

The easiest way to install the current development version of Calabard is via
``pip``::

    $ pip install -e git+git://github.com/winhamwr/calabar.git


Usage
=====

Example usage::

    $ calabard /etc/calabar/my.conf

Where ``/etc/calabar/my.conf`` is the path to your _`configuration` file.

Bug Tracker
===========

If you have feedback about bugs, features or anything else, the github issue
tracking is a great place to report them: http://github.com/winhamwr/calabar/issues

License
=======

This software is licensed under the ``New BSD License``. See the ``LICENSE``
file in the top distribution directory for the full license text.

Versioning
==========

This project uses `Semantic Versioning`_.

.. _`Semantic Versioning`: http://semver.org/
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import sys
import os

from setuptools import setup, find_packages, Command

import calabar

long_description = codecs.open("README.rst", "r", "utf-8").read()

setup(
    name='calabar',
    version=calabar.__version__,
    description=calabar.__doc__,
    author=calabar.__author__,
    author_email=calabar.__contact__,
    url=calabar.__homepage__,
    platforms=["any"],
    license="BSD",
    packages=find_packages(),
    scripts=["bin/calabard", "bin/cal_run_forever"],
    zip_safe=False,
    install_requires=['psi >=0.3b2, <0.4'],
    cmdclass = {},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Programming Language :: Python",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Internet",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=long_description,
)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import sys
import os

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command

import calabar

py_version_info = sys.version_info
py_major_version = py_version_info[0]
py_minor_version = py_version_info[1]

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
    packages=find_packages('calabar'),
    scripts=["bin/calabard", "bin/cal_run_forever"],
    zip_safe=False,
    install_requires=['psi==0.3b2', 'python-daemon==1.5.2'],
    extra_requires={},
    cmdclass = {},
    classifiers=[
        "Development Status :: 3 - Alpha",
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
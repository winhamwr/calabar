#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import sys
import os
from distutils.core import setup

def find_packages(root):
    # so we don't depend on setuptools; from the Storm ORM setup.py
    packages = []
    for directory, subdirectories, files in os.walk(root):
        if '__init__.py' in files:
            packages.append(directory.replace(os.sep, '.'))
    return packages

import calabar

install_requires = ["python-daemon>=1.4.8"]

py_version_info = sys.version_info
py_major_version = py_version_info[0]
py_minor_version = py_version_info[1]

if (py_major_version == 2 and py_minor_version <=5) or py_major_version < 2:
    install_requires.append("multiprocessing")

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
    scripts=[],
    zip_safe=False,
    install_requires=install_requires,
    extra_requires={
    },
    cmdclass = {},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
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
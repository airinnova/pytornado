#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, Extension, find_namespace_packages
import os

from src.lib.pytornado.__version__ import __version__

# See also: https://github.com/kennethreitz/setup.py/blob/master/setup.py

NAME = 'pytornado'
VERSION = __version__
AUTHOR = 'Aaron Dettmann'
EMAIL = 'dettmann@kth.se'
DESCRIPTION = 'A vortex-lattice implementation (VLM) implementation'
URL = 'https://github.com/airinnova/pytornado'
REQUIRES_PYTHON = '>=3.6.0'
REQUIRED = [
    'numpy',
    'scipy',
    'matplotlib==3.0.2',
    'commonlibs',
]
README = 'README.rst'
PACKAGE_DIR = 'src/lib/'
LICENSE = 'Apache License 2.0'


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, README), "r") as fp:
    long_description = fp.read()

# Extension modules
# See
# * https://docs.python.org/3.7/extending/building.html
# * https://docs.python.org/3/distutils/setupscript.html
module1_path = 'src/lib/pytornado/aero/'
module1 = Extension(
        'pytornado.aero.c_vlm',
        sources=[
            module1_path + 'c_vlm.cpp',
            module1_path + 'c_boundary.cpp',
            module1_path + 'c_downwash.cpp',
            module1_path + 'c_lattice.cpp',
            module1_path + 'c_results.cpp',
            ],
        include_dirs=[
            module1_path,
            '/usr/include/python3.6',
            '/usr/lib/python3/dist-packages/numpy/core/include/'
            ]
        )

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    url=URL,
    ext_modules=[module1],
    include_package_data=True,
    scripts=[
        'src/bin/pytornado',
        ],
    package_dir={'': PACKAGE_DIR},
    license=LICENSE,
    # packages=[NAME],
    packages=find_namespace_packages(where=PACKAGE_DIR),
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED,
    # See: https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)

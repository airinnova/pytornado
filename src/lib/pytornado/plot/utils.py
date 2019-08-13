#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2017-2019 Airinnova AB and the PyTornado authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------

# Authors:
# * Alessandro Gastaldi
# * Aaron Dettmann

"""
Constants and boilerplate code for visualization in PyTornado.

Developed at Airinnova AB, Stockholm, Sweden.
"""

from datetime import datetime

import numpy as np

NUM_POINTS = 64

COLOR1 = 'black'
COLOR2 = [1.0, 0.4, 0.4]
COLOR3 = [0.4, 0.4, 1.0]
COLOR4 = [1.0, 0.4, 1.0]
COLOR5 = [0.7, 0.7, 0.7]

# Display item names for view containing up to MAX_ITEMS_TEXT items
MAX_ITEMS_TEXT = 10

COLORMAP = 'Spectral'

# Standard 'savefig' settings
STANDARD_DPI = 200
STANDARD_FORMAT = 'png'


def get_limits(points, lims, symm=0):
    """
    Determine external limits of domain occupied by set of points.

    Args:
        :points: (numpy) points of current plot object
        :lims: (numpy) current bounding box
        :symm: (int) symmetry setting
    """

    # flatten multi-dimensional array of coordinates to (m x n x ...) x 3
    if points.ndim > 2 and points.shape[-1]:
        points = points.reshape(-1, 3)

    lims_min = lims[0]
    lims_max = lims[1]

    # 1. FIND LIMITS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    points_min = points.min(axis=0)
    points_max = points.max(axis=0)

    indices_min = points_min < lims_min
    indices_max = points_max > lims_max

    lims_min[indices_min] = points_min[indices_min]
    lims_max[indices_max] = points_max[indices_max]

    # 2. ACCOUNT FOR SYMMETRIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    if symm == 1:
        if -points_max[2] < lims_min[2]:
            lims_min[2] = -points_max[2]

        if -points_min[2] > lims_max[2]:
            lims_max[2] = -points_min[2]

    if symm == 2:
        if -points_max[1] < lims_min[1]:
            lims_min[1] = -points_max[1]

        if -points_min[1] > lims_max[1]:
            lims_max[1] = -points_min[1]

    if symm == 3:
        if -points_max[0] < lims_min[0]:
            lims_min[0] = -points_max[0]

        if -points_min[0] > lims_max[0]:
            lims_max[0] = -points_min[0]


def scale_fig(axes, lims, directions='xyz'):
    """
    Scale axes to ensure unit aspect ratio between plot axes.

    Args:
        :axes: (object) matplotlib.axis.Axis object
        :lims: (numpy) current bounding box
        :directions: (string) combination of x, y, z for axis directions.
            * e.g. 'zx' -> x-axis = aircraft z-coord, y-axis = aircraft x-coord, no z-axis (2D view).
    """

    # find largest (half-)range
    lims_min = lims[0]
    lims_max = lims[1]
    range_max = 0.5*(lims_max - lims_min).max(axis=0)

    # find midpoint of geometry
    x_mid = 0.5*(lims_max[0] + lims_min[0])
    y_mid = 0.5*(lims_max[1] + lims_min[1])
    z_mid = 0.5*(lims_max[2] + lims_min[2])

    domain = {'x': (x_mid - 1.1*range_max, x_mid + 1.1*range_max),
              'y': (y_mid - 1.1*range_max, y_mid + 1.1*range_max),
              'z': (z_mid - 1.1*range_max, z_mid + 1.1*range_max)}

    # 2D plot
    if len(directions) == 2:
        axes.set_xlim(domain[directions[0]])
        axes.set_ylim(domain[directions[1]])

    # 3D plot
    elif len(directions) == 3:
        axes.set_xlim(domain[directions[0]])
        axes.set_ylim(domain[directions[1]])
        axes.set_zlim(domain[directions[2]])


def interpolate_quad(a, b, c, d, size):
    """
    Bi-linear parametrisation of arbitrary twisted quadrilateral.

    Args:
        :a, b, c, d: (numpy) coordinates of corner vertices
        :nr, ns: (intpy) number of chord- and span-wise points

    Returns:
        :x, y, z: (numpy) coordinates of NC x NS interpolated points
    """

    fr = 0.5*np.sqrt(np.sum((b - a)**2.0)) + 0.5*np.sqrt(np.sum((c - d)**2.0))
    fs = 0.5*np.sqrt(np.sum((d - a)**2.0)) + 0.5*np.sqrt(np.sum((c - b)**2.0))

    nr = 2.0 + np.ceil(NUM_POINTS*fr/size)
    ns = 2.0 + np.ceil(NUM_POINTS*fs/size)

    r, s = np.meshgrid(np.linspace(0.0, 1.0, num=nr), np.linspace(0.0, 1.0, num=ns))

    alfa1 = a[0]
    alfa2 = b[0] - a[0]
    alfa3 = d[0] - a[0]
    alfa4 = a[0] - b[0] + c[0] - d[0]

    beta1 = a[1]
    beta2 = b[1] - a[1]
    beta3 = d[1] - a[1]
    beta4 = a[1] - b[1] + c[1] - d[1]

    gama1 = a[2]
    gama2 = b[2] - a[2]
    gama3 = d[2] - a[2]
    gama4 = a[2] - b[2] + c[2] - d[2]

    x = alfa1 + alfa2*r + alfa3*s + alfa4*r*s
    y = beta1 + beta2*r + beta3*s + beta4*r*s
    z = gama1 + gama2*r + gama3*s + gama4*r*s

    return x, y, z

# TODO | remove meshgrid and surface visualisation (too slow)


def get_date_str():
    """
    Return a date string
    """

    now = datetime.now().strftime("%F_%H-%M-%S-%f")
    return now

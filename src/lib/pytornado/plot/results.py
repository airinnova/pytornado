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
Functions for visualisation of PyTornado aircraft geometry.

Developed at Airinnova AB, Stockholm, Sweden.
"""

import os
import logging

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D

from commonlibs.logger import truncate_filepath
from commonlibs.math.vectors import unit_vector

from pytornado.plot.utils import get_limits, scale_fig, interpolate_quad, \
                                 get_date_str, COLOR1, COLOR5, \
                                 COLORMAP, STANDARD_DPI, STANDARD_FORMAT

logger = logging.getLogger(__name__)


def view_panelwise(aircraft, state, lattice, vlmdata, key, plt_settings, block=True):
    """
    Generate 3D view of aircraft with colormap of selected result.

    Args:
        :aircraft: (object) data structure for aircraft model
        :lattice: (object) data structure for VLM lattice
        :vlmdata: (object) data structure for VLM input and output
        :key: (string) name of variable to be displayed
        :block: (bool) halt program execution until figures closed
    """

    logger.info("Generating result plot...")

    if not aircraft.wing:
        return logger.error(f"Aircraft model '{aircraft.uid}' is empty!")

    if not aircraft.state:
        logger.warning(f"Aircraft '{aircraft.uid}' contains ill-defined components!")

    figure_1 = plt.figure(figsize=(16, 12), edgecolor=COLOR1)
    axes_xyz = figure_1.add_subplot(111, projection='3d')
    axes_xyz.set_aspect('equal')

    figure_2 = plt.figure(figsize=(20, 6), edgecolor=COLOR1)
    axes_yz = figure_2.add_subplot(131)
    axes_xz = figure_2.add_subplot(132)
    axes_xy = figure_2.add_subplot(133)

    axes_yz.set_aspect('equal')
    axes_xz.set_aspect('equal')
    axes_xy.set_aspect('equal')

    lims = np.zeros((2, 3))

    for wing_uid, wing in aircraft.wing.items():
        if wing.state:
            for segment in wing.segment.values():
                points = np.array([segment.vertices['a'],
                                   segment.vertices['b'],
                                   segment.vertices['c'],
                                   segment.vertices['d'],
                                   segment.vertices['a']])

                get_limits(points, lims, symm=wing.symmetry)

            for control in wing.control.values():
                points = np.array([control.abs_vertices['d'],
                                   control.abs_vertices['a'],
                                   control.abs_vertices['b'],
                                   control.abs_vertices['c']])

                get_limits(points, lims, symm=wing.symmetry)

    size = np.sqrt(np.sum((lims[1] - lims[0])**2.0))

    scale_fig(axes_xyz, lims)
    scale_fig(axes_yz, lims, directions='yz')
    scale_fig(axes_xz, lims, directions='xz')
    scale_fig(axes_xy, lims, directions='xy')

    num_segments = 0
    num_wings = 0

    colormap = cm.get_cmap(COLORMAP) if COLORMAP else None

    # Plot free stream vector
    free_stream_vel = 3*unit_vector(state.free_stream_velocity_vector)
    orig = np.array([lims[0, 0], 0, 0]) - free_stream_vel
    axes_xyz.quiver(*orig, *free_stream_vel, color=COLOR1, linewidth=1)
    axes_xyz.text(*orig, f"{state.aero['airspeed']} m/s")

    for wing_uid, wing in aircraft.wing.items():
        num_wings += 1

        if not wing.state:
            logger.warning(f"Wing '{wing_uid}' ignored (ill-defined).")
            continue

        M = list()

        for segment_uid, segment in wing.segment.items():
            num_segments += 1

            points = np.array([segment.vertices['a'],
                               segment.vertices['b'],
                               segment.vertices['c'],
                               segment.vertices['d'],
                               segment.vertices['a']])

            X = points[:, 0]
            Y = points[:, 1]
            Z = points[:, 2]

            M.append(np.mean(points, axis=0))

            axes_xyz.plot(X, Y, Z, color=COLOR1, marker='.', linewidth=0.50, markersize=4.0)
            axes_yz.plot(Y, Z, color=COLOR1, linewidth=0.50)
            axes_xz.plot(X, Z, color=COLOR1, linewidth=0.50)
            axes_xy.plot(X, Y, color=COLOR1, linewidth=0.50)

            # x, y-symmetry
            if wing.symmetry == 1:
                axes_xyz.plot(X, Y, -Z, color=COLOR1, linewidth=0.5)

                axes_yz.plot(Y, -Z, color=COLOR1, linewidth=0.5)
                axes_xz.plot(X, -Z, color=COLOR1, linewidth=0.5)

            # x, z-symmetry
            elif wing.symmetry == 2:
                axes_xyz.plot(X, -Y, Z, color=COLOR1, linewidth=0.5)

                axes_yz.plot(-Y, Z, color=COLOR1, linewidth=0.5)
                axes_xy.plot(X, -Y, color=COLOR1, linewidth=0.5)

            # y, z-symmetry
            elif wing.symmetry == 3:
                axes_xyz.plot(-X, Y, Z, color=COLOR1, linewidth=0.5)

                axes_xz.plot(-X, Z, color=COLOR1, linewidth=0.5)
                axes_xy.plot(-X, Y, color=COLOR1, linewidth=0.5)

        for control_uid, control in wing.control.items():
            if control.device_type == 'flap':
                points = np.array([control.abs_vertices['d'],
                                   control.abs_vertices['a'],
                                   control.abs_vertices['b'],
                                   control.abs_vertices['c']])

            elif control.device_type == 'slat':
                points = np.array([control.abs_vertices['b'],
                                   control.abs_vertices['c'],
                                   control.abs_vertices['d'],
                                   control.abs_vertices['a']])

            X = points[:, 0]
            Y = points[:, 1]
            Z = points[:, 2]

            axes_xyz.plot(X, Y, Z, color=COLOR1, marker='.', linewidth=1.0, markersize=4.0)
            axes_yz.plot(Y, Z, color=COLOR1, linewidth=1.0)
            axes_xz.plot(X, Z, color=COLOR1, linewidth=1.0)
            axes_xy.plot(X, Y, color=COLOR1, linewidth=1.0)

            hinge_points = np.array([control.abs_hinge_vertices['p_inner'],
                                     control.abs_hinge_vertices['p_outer']])

            X_hinge = hinge_points[:, 0]
            Y_hinge = hinge_points[:, 1]
            Z_hinge = hinge_points[:, 2]
            axes_xyz.plot(X_hinge, Y_hinge, Z_hinge, '--', color=COLOR1, marker='.', linewidth=1.0, markersize=4.0)
            axes_yz.plot(Y_hinge, Z_hinge, '--', color=COLOR1, linewidth=1.0)
            axes_xz.plot(X_hinge, Z_hinge, '--', color=COLOR1, linewidth=1.0)
            axes_xy.plot(X_hinge, Y_hinge, '--', color=COLOR1, linewidth=1.0)

            # x, y-symmetry
            if wing.symmetry == 1:
                axes_xyz.plot(X, Y, -Z, color=COLOR1, linewidth=0.5)
                axes_yz.plot(Y, -Z, color=COLOR1, linewidth=0.5)
                axes_xz.plot(X, -Z, color=COLOR1, linewidth=0.5)

            # x, z-symmetry
            elif wing.symmetry == 2:
                axes_xyz.plot(X, -Y, Z, color=COLOR1, linewidth=0.5)
                axes_yz.plot(-Y, Z, color=COLOR1, linewidth=0.5)
                axes_xy.plot(X, -Y, color=COLOR1, linewidth=0.5)

            # y, z-symmetry
            elif wing.symmetry == 3:
                axes_xyz.plot(-X, Y, Z, color=COLOR1, linewidth=0.5)
                axes_xz.plot(-X, Z, color=COLOR1, linewidth=0.5)
                axes_xy.plot(-X, Y, color=COLOR1, linewidth=0.5)

    # Normalise to range [0, 1]
    data = vlmdata.panelwise[key]
    val_range = max(data) - min(data)
    if val_range != 0:
        values = (data - min(data))/val_range
    else:
        values = np.zeros(data.shape)

    for pp, val in zip(lattice.p, values):
        color = colormap(val) if colormap else COLOR5

        points_p = np.array([pp[0],
                             pp[1],
                             pp[2],
                             pp[3],
                             pp[0]])

        X = points_p[:, 0]
        Y = points_p[:, 1]
        Z = points_p[:, 2]

        axes_xyz.plot(X, Y, Z, color=COLOR5, linewidth=0.25)
        axes_yz.plot(Y, Z, color=COLOR5, linewidth=0.25)
        axes_xz.plot(X, Z, color=COLOR5, linewidth=0.25)
        axes_xy.plot(X, Y, color=COLOR5, linewidth=0.25)

        XS, YS, ZS = interpolate_quad(points_p[0], points_p[1], points_p[2], points_p[3], size)
        axes_xyz.plot_surface(XS, YS, ZS, color=color, linewidth=0.0, shade=False, cstride=1, rstride=1)
        # axes_yz.fill(YS, ZS, color=color, facecolor=color, fill=True)
        # axes_xz.fill(XS, ZS, color=color, facecolor=color, fill=True)
        # axes_xy.fill(XS, YS, color=color, facecolor=color, fill=True)

    # 2.2. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.annotate(f"num_segments = {num_segments:02d}\n"
                      + f"num_wing = {num_wings:02d}",
                      xy=(0, 0), xytext=(1, 0), textcoords='axes fraction', va='bottom', ha='right')

    # 2.3. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    cbar = cm.ScalarMappable(cmap=colormap)
    cbar.set_array(vlmdata.panelwise[key])

    cbar = figure_1.colorbar(cbar)
    cbar.set_label(key)

    # 2.4. DISPLAY LABELS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.set_xlabel('x [m]')
    axes_xyz.set_ylabel('y [m]')
    axes_xyz.set_zlabel('z [m]')

    axes_yz.set_xlabel('y [m]')
    axes_yz.set_ylabel('z [m]')

    axes_xz.set_xlabel('x [m]')
    axes_xz.set_ylabel('z [m]')

    axes_xy.set_xlabel('x [m]')
    axes_xy.set_ylabel('y [m]')

    axes_xyz.set_title(aircraft.uid)

    axes_yz.set_title(aircraft.uid)
    axes_xz.set_title(aircraft.uid)
    axes_xy.set_title(aircraft.uid)

    figure_2.suptitle(f"{aircraft.uid} | {key}")

    plt.tight_layout()
    figure_1.subplots_adjust(left=0.15, bottom=0.01, right=0.90, top=0.98, wspace=0.39, hspace=0.45)

    if plt_settings['save']:
        fname1 = os.path.join(plt_settings['plot_dir'], f"results3_{key}_{get_date_str()}.{STANDARD_FORMAT}")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname1)}'")
        figure_1.savefig(fname1, dpi=STANDARD_DPI, format=STANDARD_FORMAT)

        fname2 = os.path.join(plt_settings['plot_dir'], f"results_{key}_{get_date_str()}.{STANDARD_FORMAT}")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname2)}'")
        figure_2.savefig(fname2, dpi=STANDARD_DPI, format=STANDARD_FORMAT)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')

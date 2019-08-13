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
from mpl_toolkits.mplot3d import Axes3D
from commonlibs.logger import truncate_filepath

from pytornado.plot.utils import get_limits, scale_fig, get_date_str, COLOR1, \
                                 COLOR3, COLOR4, MAX_ITEMS_TEXT, STANDARD_DPI, \
                                 STANDARD_FORMAT
from pytornado.objects.objecttools import all_subareas

logger = logging.getLogger(__name__)


def view_aircraft(aircraft, lattice, plt_settings, opt_settings, block=True, plot=None):
    """Generate 3D and 2D views of aircraft lattice.

    By default, shows segment vertices and edges.

    Optionally, shows:
        * GRID (bilinear interpolation of segment surface)
        * SURF (colored bilinear interpolation of segment surface)
        * NORM (display segment normal vectors)

    Args:
        :aircraft: (object) data structure for aircraft model
        :lattice: (object) data structure for VLM lattice
        :block: (bool) halt execution while figure is open
        :plot: (string) additional visualisation features ('grid', 'surf', 'norm')
        :plt_settings: general plot settings
        :opt_settings: optional settings
    """

    logger.info("Generating lattice plot...")

    if not aircraft.wing:
        return logger.error(f"Aircraft model '{aircraft.uid}' is empty!")

    if not aircraft.state:
        logger.warning(f"Aircraft '{aircraft.uid}' contains ill-defined components!")

    # 2. 3D VIEW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    figure_1 = plt.figure(figsize=(12, 12), edgecolor=COLOR1)
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

    X = [aircraft.refs['gcenter'][0]]
    Y = [aircraft.refs['gcenter'][1]]
    Z = [aircraft.refs['gcenter'][2]]

    axes_xyz.plot(X, Y, Z, color=COLOR1, marker='x', markersize=8.0)

    axes_yz.plot(Y, Z, color=COLOR1, marker='x', markersize=8.0)
    axes_xz.plot(X, Z, color=COLOR1, marker='x', markersize=8.0)
    axes_xy.plot(X, Y, color=COLOR1, marker='x', markersize=8.0)

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
                points = np.array([control.abs_vertices['b'],
                                   control.abs_vertices['c'],
                                   control.abs_vertices['d'],
                                   control.abs_vertices['a']])

                get_limits(points, lims, symm=wing.symmetry)

    # size = np.sqrt(np.sum((lims[1] - lims[0])**2.0))

    scale_fig(axes_xyz, lims)
    scale_fig(axes_yz, lims, directions='yz')
    scale_fig(axes_xz, lims, directions='xz')
    scale_fig(axes_xy, lims, directions='xy')

    # 2.1. DISPLAY GEOMETRY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    num_segments = 0
    num_wings = 0

    for wing_uid, wing in aircraft.wing.items():
        num_wings += 1

        if not wing.state:
            logger.error(f"Wing '{wing_uid}' ignored (ill-defined).")
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

            axes_xyz.plot(X, Y, Z, color=COLOR1, marker='.', linewidth=1.0, markersize=4.0)

            axes_yz.plot(Y, Z, color=COLOR1, linewidth=1.0)
            axes_xz.plot(X, Z, color=COLOR1, linewidth=1.0)
            axes_xy.plot(X, Y, color=COLOR1, linewidth=1.0)

            # x, y-symmetry
            if wing.symmetry == 1:
                axes_xyz.plot(X, Y, -Z, color=COLOR1, linewidth=1.0)
                axes_yz.plot(Y, -Z, color=COLOR1, linewidth=1.0)
                axes_xz.plot(X, -Z, color=COLOR1, linewidth=1.0)

            # x, z-symmetry
            elif wing.symmetry == 2:
                axes_xyz.plot(X, -Y, Z, color=COLOR1, linewidth=1.0)
                axes_yz.plot(-Y, Z, color=COLOR1, linewidth=1.0)
                axes_xy.plot(X, -Y, color=COLOR1, linewidth=1.0)

            # y, z-symmetry
            elif wing.symmetry == 3:
                axes_xyz.plot(-X, Y, Z, color=COLOR1, linewidth=1.0)
                axes_xz.plot(-X, Z, color=COLOR1, linewidth=1.0)
                axes_xy.plot(-X, Y, color=COLOR1, linewidth=1.0)

        if len(aircraft.wing) < MAX_ITEMS_TEXT:
            M = np.mean(M, axis=0)

            text = axes_xyz.text(M[0], M[1], M[2], wing_uid, backgroundcolor='w', size='medium')
            text.set_bbox(dict(color='w', alpha=0.4))

        # PLOT SUBDIVISIONS
        if 'subdivisions' in opt_settings:
            for this_subarea, _, _, _ in all_subareas(aircraft):
                subarea_type = this_subarea[1]
                subarea = this_subarea[2]

                if subarea_type == 'segment':
                    color = 'blue'
                elif subarea_type == 'slat':
                    color = 'green'
                elif subarea_type == 'flap':
                    color = 'red'

                mirror_list = [False]
                if subarea.symmetry:
                    mirror_list.append(True)

                for mirror in mirror_list:
                    vertices = subarea.abs_vertices(mirror)
                    points = np.array([vertices['a'],
                                       vertices['b'],
                                       vertices['c'],
                                       vertices['d'],
                                       vertices['a']])

                    X = points[:, 0]
                    Y = points[:, 1]
                    Z = points[:, 2]

                    axes_xyz.plot(X, Y, Z, color=color, marker='.', linewidth=1.0, markersize=4.0)
                    axes_yz.plot(Y, Z, color=color, linewidth=1.0)
                    axes_xz.plot(X, Z, color=color, linewidth=1.0)
                    axes_xy.plot(X, Y, color=color, linewidth=1.0)

                    # Camber line local axis
                    if 'camberline_rot_axis' in opt_settings:
                        camber_axis_vertices = subarea.abs_camber_line_rot_axis_vertices(mirror)
                        inner = camber_axis_vertices['p_inner']
                        outer = camber_axis_vertices['p_outer']
                        subarea_vertices = subarea.abs_vertices(mirror)
                        axes_xyz.quiver(*((subarea_vertices['a'] + subarea_vertices['b'])/2),
                                        *(outer - inner), color='orange', linewidth=1)

                    if subarea_type in ['flap', 'slat']:
                        hinge_vertices = subarea.abs_hinge_vertices(mirror)
                        hinge_axis = subarea.abs_hinge_axis(mirror)

                        x, y, z = hinge_vertices['p_inner']
                        u, v, w = hinge_axis
                        axes_xyz.quiver(x, y, z, u, v, w, color='black', linewidth=1)

                        points = np.array([hinge_vertices['p_inner'], hinge_vertices['p_outer']])
                        X = points[:, 0]
                        Y = points[:, 1]
                        Z = points[:, 2]

                        axes_yz.plot(Y, Z, '--', color='black', linewidth=1.0)
                        axes_xz.plot(X, Z, '--', color='black', linewidth=1.0)
                        axes_xy.plot(X, Y, '--', color='black', linewidth=1.0)

        # PLOT CONTROLS
        if 'controls' in opt_settings:
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

                axes_xyz.plot(X, Y, Z, color=COLOR4, marker='.', linewidth=1.0, markersize=4.0)
                axes_yz.plot(Y, Z, color=COLOR4, linewidth=1.0)
                axes_xz.plot(X, Z, color=COLOR4, linewidth=1.0)
                axes_xy.plot(X, Y, color=COLOR4, linewidth=1.0)

                hinge_points = np.array([control.abs_hinge_vertices['p_inner'],
                                         control.abs_hinge_vertices['p_outer']])

                X_hinge = hinge_points[:, 0]
                Y_hinge = hinge_points[:, 1]
                Z_hinge = hinge_points[:, 2]
                axes_xyz.plot(X_hinge, Y_hinge, Z_hinge, '--', color=COLOR3, marker='.', linewidth=1.0, markersize=4.0)
                axes_yz.plot(Y_hinge, Z_hinge, '--', color=COLOR3, linewidth=1.0)
                axes_xz.plot(X_hinge, Z_hinge, '--', color=COLOR3, linewidth=1.0)
                axes_xy.plot(X_hinge, Y_hinge, '--', color=COLOR3, linewidth=1.0)

                # x, y-symmetry
                if wing.symmetry == 1:
                    axes_xyz.plot(X, Y, -Z, color=COLOR4, linewidth=0.5)
                    axes_yz.plot(Y, -Z, color=COLOR4, linewidth=0.5)
                    axes_xz.plot(X, -Z, color=COLOR4, linewidth=0.5)

                # x, z-symmetry
                elif wing.symmetry == 2:
                    axes_xyz.plot(X, -Y, Z, color=COLOR4, linewidth=0.5)
                    axes_yz.plot(-Y, Z, color=COLOR4, linewidth=0.5)
                    axes_xy.plot(X, -Y, color=COLOR4, linewidth=0.5)

                # y, z-symmetry
                elif wing.symmetry == 3:
                    axes_xyz.plot(-X, Y, Z, color=COLOR4, linewidth=0.5)
                    axes_xz.plot(-X, Z, color=COLOR4, linewidth=0.5)
                    axes_xy.plot(-X, Y, color=COLOR4, linewidth=0.5)

    for pp, pc, pv, pn in zip(lattice.p, lattice.c, lattice.v, lattice.n):
        points_p = np.array([pp[0], pp[1], pp[2], pp[3], pp[0]])

        # PANELS
        X = points_p[:, 0]
        Y = points_p[:, 1]
        Z = points_p[:, 2]

        axes_xyz.plot(X, Y, Z, color=COLOR1, linewidth=0.25)
        axes_yz.plot(Y, Z, color=COLOR1, linewidth=0.25)
        axes_xz.plot(X, Z, color=COLOR1, linewidth=0.25)
        axes_xy.plot(X, Y, color=COLOR1, linewidth=0.25)

        # PLOT THE NORMALS
        if 'normals' in opt_settings:
            points_c2n = np.array([pc, pc+pn])

            X = points_c2n[:, 0]
            Y = points_c2n[:, 1]
            Z = points_c2n[:, 2]

            axes_xyz.plot(X, Y, Z, color='blue', linewidth=0.5)
            axes_yz.plot(Y, Z, color='blue', linewidth=0.5)
            axes_xz.plot(X, Z, color='blue', linewidth=0.5)
            axes_xy.plot(X, Y, color='blue', linewidth=0.5)

        # PLOT VORTEX POINTS
        if 'horseshoes' in opt_settings:
            points_v = np.array([pv[0],
                                 pv[1],
                                 pv[2],
                                 pv[3],
                                 pv[0]])

            X = points_v[:, 0]
            Y = points_v[:, 1]
            Z = points_v[:, 2]

            axes_xyz.plot(X, Y, Z, color='green', linewidth=0.25)
            axes_yz.plot(Y, Z, color='green', linewidth=0.25)
            axes_xz.plot(X, Z, color='green', linewidth=0.25)
            axes_xy.plot(X, Y, color='green', linewidth=0.25)

    if 'horseshoe_midpoints' in opt_settings:
        for bound_leg_midpoint in lattice.bound_leg_midpoints:
            axes_xyz.scatter(*bound_leg_midpoint, marker='.', s=10, color='red')

    # 2.2. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.annotate(f"num_segments = {num_segments:02d}\n"
                      + f"num_wing = {num_wings:02d}",
                      xy=(0, 0), xytext=(1, 0), textcoords='axes fraction', va='bottom', ha='right')

    # 2.3. DISPLAY LABELS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

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

    figure_2.suptitle(aircraft.uid)

    plt.tight_layout()

    if plt_settings['save']:
        fname1 = os.path.join(plt_settings['plot_dir'], f"lattice3D_{get_date_str()}.{STANDARD_FORMAT}")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname1)}'")
        figure_1.savefig(fname1, dpi=STANDARD_DPI, format=STANDARD_FORMAT)

        fname2 = os.path.join(plt_settings['plot_dir'], f"lattice_{get_date_str()}.{STANDARD_FORMAT}")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname2)}'")
        figure_2.savefig(fname2, dpi=STANDARD_DPI, format=STANDARD_FORMAT)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')

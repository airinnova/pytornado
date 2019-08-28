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
Visualisation of the aircraft geometry

Developed at Airinnova AB, Stockholm, Sweden.
"""

import os
import logging
from contextlib import contextmanager

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from commonlibs.logger import truncate_filepath
from commonlibs.math.vectors import unit_vector

from pytornado.plot.utils import get_limits, scale_fig, interpolate_quad, get_date_str
from pytornado.plot.utils import COLOR1, COLOR2, COLOR3, COLOR4, COLOR5, MAX_ITEMS_TEXT, STANDARD_DPI, STANDARD_FORMAT
import pytornado.objects.objecttools as ot

logger = logging.getLogger(__name__)

COLORMAP = 'Pastel1'
NUM_COLORS = 9.0

colormap = cm.get_cmap(COLORMAP)


@contextmanager
def plot2d3d(aircraft, plot_name, plot_settings):
    """
    Context manager for 2D and 3D plots

    Args:
        :aircraft: Aircraft model
        :plot_name: Name if file is to be saved
        :plot_settings: Dictionary with plot settings

    Yields:
        * A tuple with (figure_2d, axes_2d, figure_3d, axes_3d)

    Note:
        * A suffix '2D' or '3D' is added to 'plot_name'
    """

    # ----- 3D plot -----
    figure_3d, axes_3d = _init_plot3d(title=aircraft.uid)
    _add_info_plot3d(axes_3d, aircraft)

    # ----- 2D plot -----
    figure_2d, axes_2d = _init_plot2d(title=aircraft.uid)

    scale_plots(axes_2d, axes_3d, aircraft)

    try:
        yield (figure_2d, axes_2d, figure_3d, axes_3d)
    finally:
        show_and_save(plot_settings, (figure_3d, plot_name + '3D'), (figure_2d, plot_name + '2D'))
        plt.close('all')


def _init_plot3d(title=''):
    """
    Initialise an axes object for 3D plots

    Args:
        :title: (str) Plot title

    Returns:
        :fig: Figure object (matplotlib)
        :axes: Axes object (matplotlib)
    """

    fig = plt.figure(figsize=(12, 12), edgecolor=COLOR1)
    axes = fig.gca(projection='3d')
    axes.set_aspect('equal')

    # Add labels
    axes.set_xlabel('X [m]')
    axes.set_ylabel('Y [m]')
    axes.set_zlabel('Z [m]')

    axes.set_title(title)
    return fig, axes


def _init_plot2d(title=''):
    """
    Initialise an axes object for 2D plots

    Args:
        :title: (str) Plot title

    Returns:
        :fig: Figure object (matplotlib)
        :axes: Tuple with axes objects (matplotlib)
    """

    fig = plt.figure(figsize=(20, 7), edgecolor=COLOR1)
    axes_yz = fig.add_subplot(131)
    axes_xz = fig.add_subplot(132)
    axes_xy = fig.add_subplot(133)
    axes_yz.set_aspect('equal')
    axes_xz.set_aspect('equal')
    axes_xy.set_aspect('equal')

    # Add labels
    axes_yz.set_xlabel('Y [m]')
    axes_yz.set_ylabel('Z [m]')

    axes_xz.set_xlabel('X [m]')
    axes_xz.set_ylabel('Z [m]')

    axes_xy.set_xlabel('X [m]')
    axes_xy.set_ylabel('Y [m]')

    # Add titles
    axes_yz.set_title("Y-Z plane")
    axes_xz.set_title("X-Z plane")
    axes_xy.set_title("X-Y plane")

    fig.suptitle(title)
    return fig, (axes_yz, axes_xz, axes_xy)


def scale_plots(axes_2d, axes_3d, aircraft):
    """
    Correct the axes scaling

    TODO
    """

    axes_yz, axes_xz, axes_xy = axes_2d

    # Iterate through segment vertices to determine required plot dimension
    lims = np.zeros((2, 3))
    for (_, _, segment), (_, _, wing) in ot.all_segments(aircraft):
        points = np.array([segment.vertices['a'],
                           segment.vertices['b'],
                           segment.vertices['c'],
                           segment.vertices['d'],
                           segment.vertices['a']])

        get_limits(points, lims, symm=wing.symmetry)

    # size = np.sqrt(np.sum((lims[1] - lims[0])**2.0))

    scale_fig(axes_3d, lims)

    scale_fig(axes_yz, lims, directions='yz')
    scale_fig(axes_xz, lims, directions='xz')
    scale_fig(axes_xy, lims, directions='xy')


def _add_CG_plot3d(axes_3d, aircraft):
    """
    Add a marker indicating the centre of gravity

    Args:
        :axes_3d: Axes object (matplotlib)
        :aircraft: (object) data structure for aircraft model
    """

    X, Y, Z = aircraft.refs['gcenter']
    axes_3d.scatter(X, Y, Z, color=COLOR1, marker='x', s=40, linewidth=2)


def _add_CG_plot2d(axes_2d, aircraft):
    """
    Add a marker indicating the centre of gravity

    Args:
        :axes: Axes object (matplotlib)
        :aircraft: (object) data structure for aircraft model
    """

    X, Y, Z = aircraft.refs['gcenter']
    axes_yz, axes_xz, axes_xy = axes_2d

    axes_yz.scatter(Y, Z, color=COLOR1, marker='x', s=40, linewidth=2)
    axes_xz.scatter(X, Z, color=COLOR1, marker='x', s=40, linewidth=2)
    axes_xy.scatter(X, Y, color=COLOR1, marker='x', s=40, linewidth=2)


def add_CG(axes_2d, axes_3d, aircraft):
    """
    TODO
    """

    _add_CG_plot3d(axes_3d, aircraft)
    _add_CG_plot2d(axes_2d, aircraft)


def add_wings(axes_2d, axes_3d, aircraft):
    """
    Add wings to axes objects

    TODO
    """

    axes_yz, axes_xz, axes_xy = axes_2d
    for (_, segment_uid, segment), (_, wing_uid, wing) in ot.all_segments(aircraft):
        M = list()
        points = np.array([segment.vertices['a'],
                           segment.vertices['b'],
                           segment.vertices['c'],
                           segment.vertices['d'],
                           segment.vertices['a']])

        X = points[:, 0]
        Y = points[:, 1]
        Z = points[:, 2]

        M.append(np.mean(points, axis=0))

        # ----------------------------------------
        # ----------------------------------------
        # ----------------------------------------
        # ----------------------------------------
        # ----------------------------------------
        # if plot == 'norm':
        #     X1, Y1, Z1 = 0.25*points[3, :] + 0.75*points[0, :]
        #     X2, Y2, Z2 = 0.25*points[2, :] + 0.75*points[1, :]

        #     X3, Y3, Z3 = 0.50*points[1, :] + 0.50*points[0, :]
        #     X4, Y4, Z4 = 0.50*points[2, :] + 0.50*points[3, :]

        #     XM, YM, ZM = (0.5*X2 + 0.5*X1, 0.5*Y2 + 0.5*Y1, 0.5*Z2 + 0.5*Z1)

        #     XA, YA, ZA = (X2 - X1, Y2 - Y1, Z2 - Z1)
        #     XB, YB, ZB = (X4 - X3, Y4 - Y3, Z4 - Z3)

        #     XN, YN, ZN = np.cross([XA, YA, ZA], [XB, YB, ZB])

        #     axes_3d.quiver(XM, YM, ZM, XN, YN, ZN, color=COLOR4)

    ######################
    ######################
    ######################
            # Normal, more concise
            # axes_xyz.quiver(XM, YM, ZM, *segment.normal_vector, color="green")
    ######################
    ######################
    ######################

        # elif plot == 'wire':
        #     XW, YW, ZW = interpolate_quad(points[0], points[1], points[2], points[3], size)
        #     axes_3d.plot_wireframe(XW, YW, ZW, color=COLOR1, linewidth=0.2)

        # elif plot == 'surf':
        #     C = 0.0
        #     color = colormap(C) if colormap else COLOR5
        #     XS, YS, ZS = interpolate_quad(points[0], points[1], points[2], points[3], size)
        #     axes_3d.plot_surface(XS, YS, ZS, color=color, linewidth=0.0, shade=False, cstride=1, rstride=1)
        #     C = (C + 1.0/NUM_COLORS) % 1.0
        # ----------------------------------------
        # ----------------------------------------
        # ----------------------------------------
        # ----------------------------------------
        # ----------------------------------------

        axes_3d.plot(X, Y, Z, color=COLOR1, marker='.', linewidth=0.50, markersize=4.0)

        axes_yz.plot(Y, Z, color=COLOR1, linewidth=0.50)
        axes_xz.plot(X, Z, color=COLOR1, linewidth=0.50)
        axes_xy.plot(X, Y, color=COLOR1, linewidth=0.50)

        # x, y-symmetry
        if wing.symmetry == 1:
            axes_3d.plot(X, Y, -Z, color=COLOR5, linewidth=0.5)
            axes_yz.plot(Y, -Z, color=COLOR5, linewidth=0.5)
            axes_xz.plot(X, -Z, color=COLOR5, linewidth=0.5)

        # x, z-symmetry
        elif wing.symmetry == 2:
            axes_3d.plot(X, -Y, Z, color=COLOR5, linewidth=0.5)
            axes_yz.plot(-Y, Z, color=COLOR5, linewidth=0.5)
            axes_xy.plot(X, -Y, color=COLOR5, linewidth=0.5)

        # y, z-symmetry
        elif wing.symmetry == 3:
            axes_3d.plot(-X, Y, Z, color=COLOR5, linewidth=0.5)
            axes_xz.plot(-X, Z, color=COLOR5, linewidth=0.5)
            axes_xy.plot(-X, Y, color=COLOR5, linewidth=0.5)

        # # ----- Segment "main direction" -----
        # P = 0.5*(segment.vertices['a'] + segment.vertices['d'])
        # N = 3
        # axes_3d.quiver(*P, *(N*unit_vector(segment.main_direction)), color="red", linewidth=2.0)

    if len(aircraft.wing) < MAX_ITEMS_TEXT:
        M = np.mean(M, axis=0)
        text = axes_3d.text(M[0], M[1], M[2], wing_uid, backgroundcolor='w', size='medium')
        text.set_bbox(dict(color='w', alpha=0.4))


def add_controls(axes_2d, axes_3d, aircraft):
    """
    Add control surfaces to axes objects

    TODO
    """

    axes_yz, axes_xz, axes_xy = axes_2d

    # ----- Add outer control geometry -----
    for (_, control_uid, control), (_, wing_uid, wing) in ot.all_controls(aircraft):
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

        axes_3d.plot(X, Y, Z, color=COLOR4, marker='.', linewidth=1.0, markersize=4.0)
        axes_yz.plot(Y, Z, color=COLOR4, linewidth=1.0)
        axes_xz.plot(X, Z, color=COLOR4, linewidth=1.0)
        axes_xy.plot(X, Y, color=COLOR4, linewidth=1.0)

        # ----- Add hinges -----
        hinge_points = np.array([control.abs_hinge_vertices['p_inner'],
                                 control.abs_hinge_vertices['p_outer']])

        X_hinge = hinge_points[:, 0]
        Y_hinge = hinge_points[:, 1]
        Z_hinge = hinge_points[:, 2]
        axes_3d.plot(X_hinge, Y_hinge, Z_hinge, '--', color=COLOR3, marker='.', linewidth=1.0, markersize=4.0)
        axes_yz.plot(Y_hinge, Z_hinge, '--', color=COLOR3, linewidth=1.0)
        axes_xz.plot(X_hinge, Z_hinge, '--', color=COLOR3, linewidth=1.0)
        axes_xy.plot(X_hinge, Y_hinge, '--', color=COLOR3, linewidth=1.0)

        # x-y symmetry
        if wing.symmetry == 1:
            axes_3d.plot(X, Y, -Z, color=COLOR4, linewidth=1.0)
            axes_yz.plot(Y, -Z, color=COLOR4, linewidth=1.0)
            axes_xz.plot(X, -Z, color=COLOR4, linewidth=1.0)

        # x-z symmetry
        elif wing.symmetry == 2:
            axes_3d.plot(X, -Y, Z, color=COLOR4, linewidth=0.5)
            axes_yz.plot(-Y, Z, color=COLOR4, linewidth=0.5)
            axes_xy.plot(X, -Y, color=COLOR4, linewidth=0.5)

        # y-z symmetry
        elif wing.symmetry == 3:
            axes_3d.plot(-X, Y, Z, color=COLOR4, linewidth=0.5)
            axes_xz.plot(-X, Z, color=COLOR4, linewidth=0.5)
            axes_xy.plot(-X, Y, color=COLOR4, linewidth=0.5)


def _add_info_plot3d(axes, aircraft):
    """
    Add info box to 3D plot

    Args:
        :axes: Axes object (matplotlib)
        :aircraft: Aircraft model
    """

    axes.annotate(
        f"Wings = {ot.count_all_wings(aircraft):2d}\n"
        + f"Segments = {ot.count_all_segments(aircraft):2d}\n"
        + f"Controls = {ot.count_all_controls(aircraft):2d}\n\n"
        + f"Aircraft size = {aircraft.size:5.2f}",
        xy=(0, 0),
        xytext=(1, 0),
        textcoords='axes fraction',
        va='bottom',
        ha='right'
    )


def show_and_save(plot_settings, *figures):
    """
    Save and/or show plots

    Args:
        :plot_settings: Plot settings
        :*figures: Tuples with (figure_object, 'name_of_plot')
    """

    if plot_settings['save']:
        for figure, fig_name in figures:
            fname = os.path.join(plot_settings['plot_dir'], f"{fig_name}_{get_date_str()}.{STANDARD_FORMAT}")
            logger.info(f"Saving plot as file: '{truncate_filepath(fname)}'")
            figure.savefig(fname, dpi=STANDARD_DPI, format=STANDARD_FORMAT)

    if plot_settings['show']:
        plt.show()


def add_lattice(axes_2d, axes_3d, lattice):
    """
    TODO
    """

    axes_yz, axes_xz, axes_xy = axes_2d
    for pp, pc, pv, pn in zip(lattice.p, lattice.c, lattice.v, lattice.n):
        points_p = np.array([pp[0], pp[1], pp[2], pp[3], pp[0]])

        # PANELS
        X = points_p[:, 0]
        Y = points_p[:, 1]
        Z = points_p[:, 2]

        axes_3d.plot(X, Y, Z, color=COLOR1, linewidth=0.25)
        axes_yz.plot(Y, Z, color=COLOR1, linewidth=0.25)
        axes_xz.plot(X, Z, color=COLOR1, linewidth=0.25)
        axes_xy.plot(X, Y, color=COLOR1, linewidth=0.25)

        # # ==========
        # opt_settings = ['normals', 'horseshoes', 'horseshoe_midpoints']
        # # ==========

        # # PLOT THE NORMALS
        # if 'normals' in opt_settings:
        #     points_c2n = np.array([pc, pc+pn])

        #     X = points_c2n[:, 0]
        #     Y = points_c2n[:, 1]
        #     Z = points_c2n[:, 2]

        #     axes_3d.plot(X, Y, Z, color='blue', linewidth=0.5)
        #     axes_yz.plot(Y, Z, color='blue', linewidth=0.5)
        #     axes_xz.plot(X, Z, color='blue', linewidth=0.5)
        #     axes_xy.plot(X, Y, color='blue', linewidth=0.5)

        # # PLOT VORTEX POINTS
        # if 'horseshoes' in opt_settings:
        #     points_v = np.array([pv[0],
        #                          pv[1],
        #                          pv[2],
        #                          pv[3],
        #                          pv[0]])

        #     X = points_v[:, 0]
        #     Y = points_v[:, 1]
        #     Z = points_v[:, 2]

        #     axes_3d.plot(X, Y, Z, color='green', linewidth=0.25)
        #     axes_yz.plot(Y, Z, color='green', linewidth=0.25)
        #     axes_xz.plot(X, Z, color='green', linewidth=0.25)
        #     axes_xy.plot(X, Y, color='green', linewidth=0.25)

    # if 'horseshoe_midpoints' in opt_settings:
        # for bound_leg_midpoint in lattice.bound_leg_midpoints:
        #     axes_3d.scatter(*bound_leg_midpoint, marker='.', s=10, color='red')







# ===========================================================================
# ===========================================================================
# ===========================================================================

        # # PLOT SUBDIVISIONS
        # if 'subdivisions' in opt_settings:
        #     for this_subarea, _, _, _ in all_subareas(aircraft):
        #         subarea_type = this_subarea[1]
        #         subarea = this_subarea[2]

        #         if subarea_type == 'segment':
        #             color = 'blue'
        #         elif subarea_type == 'slat':
        #             color = 'green'
        #         elif subarea_type == 'flap':
        #             color = 'red'

        #         mirror_list = [False]
        #         if subarea.symmetry:
        #             mirror_list.append(True)

        #         for mirror in mirror_list:
        #             vertices = subarea.abs_vertices(mirror)
        #             points = np.array([vertices['a'],
        #                                vertices['b'],
        #                                vertices['c'],
        #                                vertices['d'],
        #                                vertices['a']])

        #             X = points[:, 0]
        #             Y = points[:, 1]
        #             Z = points[:, 2]

        #             axes_xyz.plot(X, Y, Z, color=color, marker='.', linewidth=1.0, markersize=4.0)
        #             axes_yz.plot(Y, Z, color=color, linewidth=1.0)
        #             axes_xz.plot(X, Z, color=color, linewidth=1.0)
        #             axes_xy.plot(X, Y, color=color, linewidth=1.0)

        #             # Camber line local axis
        #             if 'camberline_rot_axis' in opt_settings:
        #                 camber_axis_vertices = subarea.abs_camber_line_rot_axis_vertices(mirror)
        #                 inner = camber_axis_vertices['p_inner']
        #                 outer = camber_axis_vertices['p_outer']
        #                 subarea_vertices = subarea.abs_vertices(mirror)
        #                 axes_xyz.quiver(*((subarea_vertices['a'] + subarea_vertices['b'])/2),
        #                                 *(outer - inner), color='orange', linewidth=1)

        #             if subarea_type in ['flap', 'slat']:
        #                 hinge_vertices = subarea.abs_hinge_vertices(mirror)
        #                 hinge_axis = subarea.abs_hinge_axis(mirror)

        #                 x, y, z = hinge_vertices['p_inner']
        #                 u, v, w = hinge_axis
        #                 axes_xyz.quiver(x, y, z, u, v, w, color='black', linewidth=1)

        #                 points = np.array([hinge_vertices['p_inner'], hinge_vertices['p_outer']])
        #                 X = points[:, 0]
        #                 Y = points[:, 1]
        #                 Z = points[:, 2]

        #                 axes_yz.plot(Y, Z, '--', color='black', linewidth=1.0)
        #                 axes_xz.plot(X, Z, '--', color='black', linewidth=1.0)
        #                 axes_xy.plot(X, Y, '--', color='black', linewidth=1.0)

# ===========================================================================
# ===========================================================================
# ===========================================================================

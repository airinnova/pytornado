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
Plot tools and commmon plot operations

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

import pytornado.plot.utils as pu
import pytornado.objects.objecttools as ot

logger = logging.getLogger(__name__)

COLORMAP = cm.get_cmap('Spectral')


class _Colors:
    BLACK = 'black'
    GREY = 'grey'
    GREEN = 'green'
    RED = 'red'
    BLUE = 'blue'

    # ----- Objects -----
    MESH = BLACK
    MESH_MIRROR = GREY
    CONTROL_SLAT = GREEN
    CONTROL_FLAP = RED
    CONTROL_HINGE = RED

C = _Colors


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
        * 'plot_name' is used to generate a file name if plot are to be saved.
          A suffix '2D' or '3D' is added to 'plot_name'
    """

    # ----- 3D plot -----
    figure_3d, axes_3d = _init_plot3d(title=aircraft.uid)
    _add_info_plot3d(axes_3d, aircraft)

    # ----- 2D plot -----
    figure_2d, axes_2d = _init_plot2d(title=aircraft.uid)

    scale_plots(axes_2d, axes_3d, aircraft)

    try:
        yield (figure_2d, axes_2d, figure_3d, axes_3d)
    # except:
    #     plt.close('all')
    finally:
        show_and_save(plot_settings, (figure_3d, plot_name + '3D'), (figure_2d, plot_name + '2D'))
        plt.close('all')


def _init_plot3d(title=''):
    """
    Initialise an axes object for 3D plots

    Args:
        :title: (str) Plot title

    Returns:
        :figure_3d: Figure object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
    """

    figure_3d = plt.figure(figsize=(12, 12), edgecolor=C.BLACK)
    axes_3d = figure_3d.gca(projection='3d')
    axes_3d.set_aspect('equal')

    # Add labels
    axes_3d.set_xlabel('X [m]')
    axes_3d.set_ylabel('Y [m]')
    axes_3d.set_zlabel('Z [m]')

    axes_3d.set_title(title)
    return figure_3d, axes_3d


def _init_plot2d(title=''):
    """
    Initialise an axes object for 2D plots

    Args:
        :title: (str) Plot title

    Returns:
        :figure_2d: Figure object (matplotlib)
        :axes_2d: 2D axes object (matplotlib)
    """

    figure_2d = plt.figure(figsize=(20, 7), edgecolor=C.BLACK)
    axes_yz = figure_2d.add_subplot(131)
    axes_xz = figure_2d.add_subplot(132)
    axes_xy = figure_2d.add_subplot(133)
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

    figure_2d.suptitle(title)
    return figure_2d, (axes_yz, axes_xz, axes_xy)


def scale_plots(axes_2d, axes_3d, aircraft):
    """
    Correct the axes scaling

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
        :aircraft: Aircraft model
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
        pu.get_limits(points, lims, symm=wing.symmetry)

    # Adjust scaling for all axes objects
    pu.scale_fig(axes_3d, lims)
    pu.scale_fig(axes_yz, lims, directions='yz')
    pu.scale_fig(axes_xz, lims, directions='xz')
    pu.scale_fig(axes_xy, lims, directions='xy')


def _add_CG_plot3d(axes_3d, aircraft):
    """
    Add a marker indicating the centre of gravity

    Args:
        :axes_3d: 3D axes object (matplotlib)
        :aircraft: (object) data structure for aircraft model
    """

    X, Y, Z = aircraft.refs['gcenter']
    axes_3d.scatter(X, Y, Z, color=C.BLACK, marker='x', s=40, linewidth=2)


def _add_CG_plot2d(axes_2d, aircraft):
    """
    Add a marker indicating the centre of gravity

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :aircraft: (object) data structure for aircraft model
    """

    X, Y, Z = aircraft.refs['gcenter']
    axes_yz, axes_xz, axes_xy = axes_2d

    axes_yz.scatter(Y, Z, color=C.BLACK, marker='x', s=40, linewidth=2)
    axes_xz.scatter(X, Z, color=C.BLACK, marker='x', s=40, linewidth=2)
    axes_xy.scatter(X, Y, color=C.BLACK, marker='x', s=40, linewidth=2)


def add_CG(axes_2d, axes_3d, aircraft):
    """
    Add a marker indicating the centre of gravity

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
        :aircraft: (object) data structure for aircraft model
    """

    _add_CG_plot3d(axes_3d, aircraft)
    _add_CG_plot2d(axes_2d, aircraft)


def add_wings(axes_2d, axes_3d, aircraft):
    """
    Add wings (segment vertices) to axes objects

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
        :aircraft: (object) data structure for aircraft model
    """

    axes_yz, axes_xz, axes_xy = axes_2d
    for (_, segment_uid, segment), (_, wing_uid, wing) in ot.all_segments(aircraft):
        points = np.array([segment.vertices['a'],
                           segment.vertices['b'],
                           segment.vertices['c'],
                           segment.vertices['d'],
                           segment.vertices['a']])
        _plot_XYZ_points(axes_2d, axes_3d, points, wing.symmetry, linewidth=1, color=C.MESH_MIRROR)

        # TODO
        # segment.center --> wing.center
        # center = np.mean(M, axis=0)
        # text = axes_3d.text(center[0], centre[1], centre[2], wing_uid, backgroundcolor='w', size='medium')
        # text.set_bbox(dict(color='w', alpha=0.4))
        # ============


def add_controls(axes_2d, axes_3d, aircraft):
    """
    Add control surfaces to axes objects

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
        :aircraft: (object) data structure for aircraft model
    """

    axes_yz, axes_xz, axes_xy = axes_2d

    # ----- Add outer control geometry -----
    for (_, control_uid, control), (_, wing_uid, wing) in ot.all_controls(aircraft):
        color = C.CONTROL_FLAP if control.device_type == 'flap' else C.CONTROL_SLAT
        points = np.array([control.abs_vertices['d'],
                           control.abs_vertices['a'],
                           control.abs_vertices['b'],
                           control.abs_vertices['c']])
        _plot_XYZ_points(axes_2d, axes_3d, points, wing.symmetry, linewidth=2, color=color)

        # ----- Add hinges -----
        hinge_points = np.array([control.abs_hinge_vertices['p_inner'],
                                 control.abs_hinge_vertices['p_outer']])
        _plot_XYZ_points(axes_2d, axes_3d, points, wing.symmetry, linewidth=2, color=C.CONTROL_HINGE)


def _add_info_plot3d(axes_3d, aircraft):
    """
    Add info box to 3D plot

    Args:
        :axes_3d: Axes object (matplotlib)
        :aircraft: Aircraft model
    """

    axes_3d.annotate(
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
            fname = os.path.join(
                plot_settings['plot_dir'],
                f"{fig_name}_{pu.get_date_str()}.{pu.STANDARD_FORMAT}"
            )
            logger.info(f"Saving plot as file: '{truncate_filepath(fname)}'")
            figure.savefig(fname, dpi=pu.STANDARD_DPI, format=pu.STANDARD_FORMAT)

    if plot_settings['show']:
        plt.show()


def add_lattice(axes_2d, axes_3d, lattice):
    """
    Add the VLM mesh

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
        :lattice: Lattice object
    """

    axes_yz, axes_xz, axes_xy = axes_2d
    for pp, pc, pv, pn in zip(lattice.p, lattice.c, lattice.v, lattice.n):
        # PANELS
        points_p = np.array([pp[0], pp[1], pp[2], pp[3], pp[0]])
        _plot_XYZ_points(axes_2d, axes_3d, points_p, symmetry=None, linewidth=0.5, color=C.MESH)

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

def add_freestream_vector(axes_2d, axes_3d, state):
    """
    Add a free stream vector

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
        :state: State model
    """

    # Plot free stream vector
    free_stream_vel = 3*unit_vector(state.free_stream_velocity_vector)
    # TODO: improve location!!!
    # orig = np.array([lims[0, 0], 0, 0]) - free_stream_vel
    orig = np.array([0, 0, 0]) - free_stream_vel
    axes_3d.quiver(*orig, *free_stream_vel, color=C.BLACK, linewidth=1)
    axes_3d.text(*orig, f"{state.aero['airspeed']:.1f} m/s")


def add_results(axes_2d, axes_3d, figure_3d, vlmdata, lattice):
    """
    Add results

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
        :figure_3d: Figure object (matplotlib)
        :vlmdata: (object) data structure for VLM analysis data
        :lattice: Lattice object
    """

    # =================================================
    # TODO
    # TODO
    # TODO
    key = 'cp'
    size = 100
    # =================================================

    axes_yz, axes_xz, axes_xy = axes_2d

    # Normalise to range [0, 1]
    data = vlmdata.panelwise[key]
    val_range = max(data) - min(data)
    if val_range != 0:
        values = (data - min(data))/val_range
    else:
        values = np.zeros(data.shape)

    for pp, val in zip(lattice.p, values):
        color = COLORMAP(val)

        points_p = np.array([pp[0],
                             pp[1],
                             pp[2],
                             pp[3],
                             pp[0]])

        X = points_p[:, 0]
        Y = points_p[:, 1]
        Z = points_p[:, 2]

        XS, YS, ZS = pu.interpolate_quad(points_p[0], points_p[1], points_p[2], points_p[3], size)
        axes_3d.plot_surface(XS, YS, ZS, color=color, linewidth=0.0, shade=False, cstride=1, rstride=1)
        axes_yz.fill(YS, ZS, color=color, facecolor=color, fill=True)
        axes_xz.fill(XS, ZS, color=color, facecolor=color, fill=True)
        axes_xy.fill(XS, YS, color=color, facecolor=color, fill=True)

    cbar = cm.ScalarMappable(cmap=COLORMAP)
    cbar.set_array(vlmdata.panelwise[key])

    cbar = figure_3d.colorbar(cbar)
    cbar.set_label(key)

    # figure_2.suptitle(f"{aircraft.uid} | {key}")
    # plt.tight_layout()
    # figure_1.subplots_adjust(left=0.15, bottom=0.01, right=0.90, top=0.98, wspace=0.39, hspace=0.45)


def _plot_XYZ_points(axes_2d, axes_3d, points, symmetry, *, linewidth, color, color_mirror=None):
    """
    Plot a group of XYZ coordinates

    Args:
        :axes_2d: 2D axes object (matplotlib)
        :axes_3d: 3D axes object (matplotlib)
        :XYZ: Tuple with coordinates (X, Y, Z)
        :symmetry: Symmetry flag
        :linewidth: Linewidth
        :color: Color of the primary side
        :color_mirror: Color of the mirrored side (None if same as 'color')
    """

    X = points[:, 0]
    Y = points[:, 1]
    Z = points[:, 2]
    axes_yz, axes_xz, axes_xy = axes_2d
    color_mirror = color if color_mirror is None else color_mirror

    axes_3d.plot(X, Y, Z, color=color, linewidth=linewidth)
    axes_yz.plot(Y, Z, color=color, linewidth=linewidth)
    axes_xz.plot(X, Z, color=color, linewidth=linewidth)
    axes_xy.plot(X, Y, color=color, linewidth=linewidth)

    # X-Y symmetry
    if symmetry == 1:
        axes_3d.plot(X, Y, -Z, color=color, linewidth=linewidth)
        axes_yz.plot(Y, -Z, color=color, linewidth=linewidth)
        axes_xz.plot(X, -Z, color=color, linewidth=linewidth)

    # X-Z symmetry
    elif symmetry == 2:
        axes_3d.plot(X, -Y, Z, color=color, linewidth=linewidth)
        axes_yz.plot(-Y, Z, color=color, linewidth=linewidth)
        axes_xy.plot(X, -Y, color=color, linewidth=linewidth)

    # Y-Z symmetry
    elif symmetry == 3:
        axes_3d.plot(-X, Y, Z, color=color, linewidth=linewidth)
        axes_xz.plot(-X, Z, color=color, linewidth=linewidth)
        axes_xy.plot(-X, Y, color=color, linewidth=linewidth)

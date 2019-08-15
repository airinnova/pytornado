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

from pytornado.plot.utils import get_limits, scale_fig, interpolate_quad, get_date_str
from pytornado.plot.utils import COLOR1, COLOR2, COLOR3, COLOR4, COLOR5, MAX_ITEMS_TEXT

logger = logging.getLogger(__name__)

COLORMAP = 'Pastel1'
NUM_COLORS = 9.0


def view_aircraft(aircraft, plt_settings, plot=None, block=True):
    """Generate 3D and 2D views of full aircraft geometry.

    By default, shows segment vertices and edges.
    Display options (specified in the PLOT kwarg):

        * NONE -- default, segment edges
        * GRID -- wireframe representation of segment surface
        * SURF -- wireframe representation of segment surface, color fill
        * NORM -- segment edges and normal vectors

    Args:
        :aircraft: (object) data structure for aircraft model
        :block: (bool) halt execution while figure is open
        :plot: (string) additional visualisation features ('wire', 'surf', 'norm')

    Returns:
        :None:
    """

    logger.info("Generating geometry plot...")

    if not aircraft.state:
        logger.warning(f"Aircraft '{aircraft.uid}' is ill-defined")

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

    for wing_uid, wing in aircraft.wing.items():
        if wing.state:
            for segment in wing.segment.values():
                points = np.array([segment.vertices['a'],
                                   segment.vertices['b'],
                                   segment.vertices['c'],
                                   segment.vertices['d'],
                                   segment.vertices['a']])

                get_limits(points, lims, symm=wing.symmetry)

        if wing.state:
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

    # 2.1. DISPLAY GEOMETRY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    num_segments = 0
    num_wings = 0

    colormap = cm.get_cmap(COLORMAP) if COLORMAP else None
    C = 0.0

    X = [aircraft.refs['gcenter'][0]]
    Y = [aircraft.refs['gcenter'][1]]
    Z = [aircraft.refs['gcenter'][2]]

    axes_xyz.plot(X, Y, Z, color=COLOR1, marker='x', markersize=8.0)

    axes_yz.plot(Y, Z, color=COLOR1, marker='x', markersize=8.0)
    axes_xz.plot(X, Z, color=COLOR1, marker='x', markersize=8.0)
    axes_xy.plot(X, Y, color=COLOR1, marker='x', markersize=8.0)

    for wing_uid, wing in aircraft.wing.items():
        num_wings += 1

        if not wing.state:
            logger.warning(f"Wing '{wing_uid}' ignored (ill-defined)")
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

            if plot == 'norm':
                X1, Y1, Z1 = 0.25*points[3, :] + 0.75*points[0, :]
                X2, Y2, Z2 = 0.25*points[2, :] + 0.75*points[1, :]

                X3, Y3, Z3 = 0.50*points[1, :] + 0.50*points[0, :]
                X4, Y4, Z4 = 0.50*points[2, :] + 0.50*points[3, :]

                XM, YM, ZM = (0.5*X2 + 0.5*X1, 0.5*Y2 + 0.5*Y1, 0.5*Z2 + 0.5*Z1)

                XA, YA, ZA = (X2 - X1, Y2 - Y1, Z2 - Z1)
                XB, YB, ZB = (X4 - X3, Y4 - Y3, Z4 - Z3)

                XN, YN, ZN = np.cross([XA, YA, ZA], [XB, YB, ZB])

                axes_xyz.quiver(XM, YM, ZM, XN, YN, ZN, color=COLOR4)

        ######################
        ######################
        ######################
                # Normal, more concise
                # axes_xyz.quiver(XM, YM, ZM, *segment.normal_vector, color="green")
        ######################
        ######################
        ######################

            elif plot == 'wire':
                XW, YW, ZW = interpolate_quad(points[0], points[1], points[2], points[3], size)
                axes_xyz.plot_wireframe(XW, YW, ZW, color=COLOR1, linewidth=0.2)

            elif plot == 'surf':
                color = colormap(C) if colormap else COLOR5
                XS, YS, ZS = interpolate_quad(points[0], points[1], points[2], points[3], size)
                axes_xyz.plot_surface(XS, YS, ZS, color=color, linewidth=0.0, shade=False, cstride=1, rstride=1)
                C = (C + 1.0/NUM_COLORS) % 1.0

            axes_xyz.plot(X, Y, Z, color=COLOR1, marker='.', linewidth=0.50, markersize=4.0)

            axes_yz.plot(Y, Z, color=COLOR1, linewidth=0.50)
            axes_xz.plot(X, Z, color=COLOR1, linewidth=0.50)
            axes_xy.plot(X, Y, color=COLOR1, linewidth=0.50)

            # x, y-symmetry
            if wing.symmetry == 1:
                axes_xyz.plot(X, Y, -Z, color=COLOR5, linewidth=0.5)
                axes_yz.plot(Y, -Z, color=COLOR5, linewidth=0.5)
                axes_xz.plot(X, -Z, color=COLOR5, linewidth=0.5)

            # x, z-symmetry
            elif wing.symmetry == 2:
                axes_xyz.plot(X, -Y, Z, color=COLOR5, linewidth=0.5)
                axes_yz.plot(-Y, Z, color=COLOR5, linewidth=0.5)
                axes_xy.plot(X, -Y, color=COLOR5, linewidth=0.5)

            # y, z-symmetry
            elif wing.symmetry == 3:
                axes_xyz.plot(-X, Y, Z, color=COLOR5, linewidth=0.5)
                axes_xz.plot(-X, Z, color=COLOR5, linewidth=0.5)
                axes_xy.plot(-X, Y, color=COLOR5, linewidth=0.5)

            # ----- Segment "main direction" -----
            P = 0.5*(segment.vertices['a'] + segment.vertices['d'])
            N = 3
            axes_xyz.quiver(*P, *(N*unit_vector(segment.main_direction)), color="red", linewidth=2.0)

        if len(aircraft.wing) < MAX_ITEMS_TEXT:
            M = np.mean(M, axis=0)
            text = axes_xyz.text(M[0], M[1], M[2], wing_uid, backgroundcolor='w', size='medium')
            text.set_bbox(dict(color='w', alpha=0.4))

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # CONTROL SURFACES
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
                axes_xyz.plot(X, Y, -Z, color=COLOR4, linewidth=1.0)
                axes_yz.plot(Y, -Z, color=COLOR4, linewidth=1.0)
                axes_xz.plot(X, -Z, color=COLOR4, linewidth=1.0)

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

    # 2.2. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.annotate(f"num_segments = {num_segments:02d}\n"
                      + f"num_wing     = {num_wings:02d}\n"
                      + f"size         = {aircraft.size}",
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
        fname1 = os.path.join(plt_settings['plot_dir'], f"geo_aircraft3D_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname1)}'")
        figure_1.savefig(fname1, dpi=300)

        fname2 = os.path.join(plt_settings['plot_dir'], f"geo_aircraft_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname2)}'")
        figure_2.savefig(fname2, dpi=300)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')


def view_overlay(aircraft1, aircraft2, plt_settings, block=True):
    """
    Generate 3D overlaid view of two aircraft geometries.

    By default, shows segment vertices and edges.

    Args:
        :aircraft1: (object) data structure for the first aircraft
        :aircraft2: (object) data structure for the second aircraft
        :block: (bool) halt execution while figure is open
    """

    logger.info("Generating geometry overlay plot...")

    if not aircraft1.state:
        logger.warning("Aircraft1 is ill-defined!")

    if not aircraft2.state:
        logger.warning("Aircraft2 is ill-defined!")

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

    # 2.1. DISPLAY GEOMETRY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    lims = np.zeros((2, 3))

    for aircraft, color in zip([aircraft1, aircraft2], [COLOR1, COLOR2]):
        for wing in aircraft.wing.values():
            for segment in wing.segment.values():
                points = np.array([segment.vertices['a'],
                                   segment.vertices['b'],
                                   segment.vertices['c'],
                                   segment.vertices['d'],
                                   segment.vertices['a']])

                X = points[:, 0]
                Y = points[:, 1]
                Z = points[:, 2]

                get_limits(points, lims, symm=wing.symmetry)
                axes_xyz.plot(X, Y, Z, color=color, marker='.', markersize=4)

                axes_yz.plot(Y, Z, color=color, marker='.', markersize=4)
                axes_xz.plot(X, Z, color=color, marker='.', markersize=4)
                axes_xy.plot(X, Y, color=color, marker='.', markersize=4)

                # x, y-symmetry
                if wing.symmetry == 1:
                    axes_xyz.plot(X, Y, -Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_yz.plot(Y, -Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_xz.plot(X, -Z, color=color, linestyle=':', marker='.', markersize=2)

                # x, z-symmetry
                elif wing.symmetry == 2:
                    axes_xyz.plot(X, -Y, Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_yz.plot(-Y, Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_xy.plot(X, -Y, color=color, linestyle=':', marker='.', markersize=2)

                # y, z-symmetry
                elif wing.symmetry == 3:
                    axes_xyz.plot(-X, Y, Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_xz.plot(-X, Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_xy.plot(-X, Y, color=color, linestyle=':', marker='.', markersize=2)

    scale_fig(axes_xyz, lims)
    scale_fig(axes_yz, lims, directions='yz')
    scale_fig(axes_xz, lims, directions='xz')
    scale_fig(axes_xy, lims, directions='xy')

    # 2.2. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.annotate(f"aircraft 1 = {aircraft2.uid}\n"
                      + f"aircraft 2 = {aircraft1.uid}\n",
                      xy=(0, 0), xytext=(1, 0), textcoords='axes fraction', va='bottom', ha='right')

    # display additional information

    # 2.3. DISPLAY LABELS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.set_xlabel('x [m]')
    axes_xyz.set_ylabel('y [m]')
    axes_xyz.set_zlabel('z [m]')

    axes_yz.set_xlabel('x [m]')
    axes_yz.set_ylabel('y [m]')

    axes_xz.set_xlabel('x [m]')
    axes_xz.set_ylabel('z [m]')

    axes_xy.set_xlabel('y [m]')
    axes_xy.set_ylabel('z [m]')

    axes_xyz.set_title("{} | {}".format(aircraft1.uid, aircraft2.uid))

    axes_yz.set_title("YZ")
    axes_xz.set_title("XZ")
    axes_xy.set_title("XY")

    figure_2.suptitle("{} | {}".format(aircraft1.uid, aircraft2.uid))

    plt.tight_layout()

    if plt_settings['save']:
        fname1 = os.path.join(plt_settings['plot_dir'], f"geo_overlay3D_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname1)}'")
        figure_1.savefig(fname1, dpi=300)

        fname2 = os.path.join(plt_settings['plot_dir'], f"geo_overlay_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname2)}'")
        figure_2.savefig(fname2, dpi=300)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')


def view_wing(wing, wing_uid, plt_settings, plot='surf', block=True):
    """
    Generate 3D and 2D views of individual wing geometry.

    By default, shows segment vertices and edges. Optionally, shows:

        * GRID (bilinear interpolation of segment surface)
        * SURF (colored bilinear interpolation of segment surface)
        * NORM (display segment normal vectors)

    Args:
        :wing: (object) data structure for selected wing
        :wing_uid: (string) for selected wing
        :block: (bool) halt execution while figure is open
        :plot: (string) additional visualisation features ('grid', 'surf', 'norm')
    """

    logger.info("Generating wing geometry plot...")

    if not wing.state:
        logger.warning("Wing is ill-defined!")

    # 2. 3D VIEW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    figure_xyz = plt.figure(figsize=(12, 12), edgecolor=COLOR1)

    axes_xyz = figure_xyz.add_subplot(111, projection='3d')
    axes_xyz.set_aspect('equal')

    lims = np.array([[+np.inf, +np.inf, +np.inf], [-np.inf, -np.inf, -np.inf]])

    for segment in wing.segment.values():

        points = np.array([segment.vertices['a'],
                           segment.vertices['b'],
                           segment.vertices['c'],
                           segment.vertices['d'],
                           segment.vertices['a']])

        get_limits(points, lims, symm=wing.symmetry)

    size = np.sqrt(np.sum((lims[1] - lims[0])**2.0))
    scale_fig(axes_xyz, lims)

    # 2.1. DISPLAY GEOMETRY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    M = list()
    colormap = cm.get_cmap(COLORMAP) if COLORMAP else None
    C = 0.0

    for segment_uid, segment in wing.segment.items():
        points = np.array([segment.vertices['a'],
                           segment.vertices['b'],
                           segment.vertices['c'],
                           segment.vertices['d'],
                           segment.vertices['a']])

        X = points[:, 0]
        Y = points[:, 1]
        Z = points[:, 2]

        M.append(np.mean(points, axis=0))

        if plot == 'wire':
            XW, YW, ZW = interpolate_quad(points[0], points[1], points[2], points[3], size)
            axes_xyz.plot_wireframe(XW, YW, ZW, color=COLOR1, linewidth=0.2)

        elif plot == 'surf':
            color = colormap(C) if colormap else COLOR5
            XS, YS, ZS = interpolate_quad(points[0], points[1], points[2], points[3], size)
            axes_xyz.plot_surface(XS, YS, ZS, color=color, linewidth=0.2, shade=False, cstride=1, rstride=1)
            C = (C + 1.0/NUM_COLORS) % 1.0

        axes_xyz.plot(X, Y, Z, color=COLOR1, linewidth=0.50, marker='.', markersize=4.0)

        # x, y-symmetry
        if wing.symmetry == 1:
            axes_xyz.plot(X, Y, -Z, color=COLOR5, linewidth=0.5)

        # x, z-symmetry
        elif wing.symmetry == 2:
            axes_xyz.plot(X, -Y, Z, color=COLOR5, linewidth=0.5)

        # y, z-symmetry
        elif wing.symmetry == 3:
            axes_xyz.plot(-X, Y, Z, color=COLOR5, linewidth=0.5)

    num_segments = len(wing.segment)

    if num_segments < MAX_ITEMS_TEXT:
        M = np.mean(M, axis=0)
        text = axes_xyz.text(M[0], M[1], M[2], segment_uid, backgroundcolor='w', size='medium')
        text.set_bbox(dict(color='w', alpha=0.4))

    for control_uid, control in wing.control.items():
        points = np.array([control.abs_vertices['d'],
                           control.abs_vertices['a'],
                           control.abs_vertices['b'],
                           control.abs_vertices['c']])

        X = points[:, 0]
        Y = points[:, 1]
        Z = points[:, 2]

        axes_xyz.plot(X, Y, Z, color=COLOR4, marker='.', linewidth=0.50, markersize=4.0)

        # x, y-symmetry
        if wing.symmetry == 1:
            axes_xyz.plot(X, Y, -Z, color=COLOR4, linewidth=0.5)

        # x, z-symmetry
        elif wing.symmetry == 2:
            axes_xyz.plot(X, -Y, Z, color=COLOR4, linewidth=0.5)

        # y, z-symmetry
        elif wing.symmetry == 3:
            axes_xyz.plot(-X, Y, Z, color=COLOR4, linewidth=0.5)

        texta = axes_xyz.text(X[0], Y[0], Z[0], 'd', backgroundcolor='w', size='medium')
        textb = axes_xyz.text(X[1], Y[1], Z[1], 'a', backgroundcolor='w', size='medium')
        textc = axes_xyz.text(X[2], Y[2], Z[2], 'b', backgroundcolor='w', size='medium')
        textd = axes_xyz.text(X[3], Y[3], Z[3], 'c', backgroundcolor='w', size='medium')
        texta.set_bbox(dict(color='w', alpha=0.4))
        textb.set_bbox(dict(color='w', alpha=0.4))
        textc.set_bbox(dict(color='w', alpha=0.4))
        textd.set_bbox(dict(color='w', alpha=0.4))

    # 2.2. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # display additional information
    axes_xyz.annotate(f"num_segments = {num_segments:02d}", xy=(0, 0),
                      xytext=(1, 0), textcoords='axes fraction', va='bottom',
                      ha='right')

    axes_xyz.set_xlabel('x [m]')
    axes_xyz.set_ylabel('y [m]')
    axes_xyz.set_zlabel('z [m]')
    axes_xyz.set_title(wing_uid)

    plt.tight_layout()

    if plt_settings['save']:
        fname = os.path.join(plt_settings['plot_dir'], f"geo_wing_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname)}'")
        plt.savefig(fname, dpi=300)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')


def view_spanwise(wing, wing_uid, plt_settings, properties=None, block=True):
    """
    View span-wise distribution of geometric properties.

    By default, shows segment vertices and edges.
    Optionally, shows:

        * GRID (bilinear interpolation of segment surface)
        * SURF (colored bilinear interpolation of segment surface)
        * NORM (display segment normal vectors)

    Args:
        :wing: (object) data structure for selected wing
        :wing_uid: (string) name for selected wing
        :properties: (string) selected geometry property (default=None; plots all properties if None)
        :block: (bool) halt execution while figure is open (default=True)
    """

    logger.info("Generating geometry plot...")

    if not wing.state:
        return logger.error(f"Wing '{wing_uid}' is ill-defined!")

    num_segments = len(wing.segment)

    if not num_segments > 1:
        return logger.error(f"Wing '{wing_uid}' only has one segment!")

    if properties is None:
        properties = ['chord', 'alpha', 'beta', 'sweep', 'dihedral']

    figures = list()
    axes = list()

    for i, property in enumerate(properties):
        figures.append(plt.figure(figsize=(16, 6), edgecolor=COLOR1))
        axes.append(figures[i].add_subplot(111))
        axes[i].set_xlim([0.0, 1.0])
        axes[i].set_xlabel('span [m]')
        axes[i].set_ylabel(property)
        axes[i].set_title("{} | {} distribution".format(wing_uid, property))
        axes[i].annotate(f"num_segments = {num_segments:02d}", xy=(0, 0),
                         xytext=(1, 0), textcoords='axes fraction',
                         va='bottom', ha='right')

    # 2.1. DISPLAY GEOMETRY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    for segment_uid, segment in wing.segment.items():
        X = [segment.position['inner'], segment.position['outer']]

        if properties is None:
            properties = list(segment.geometry.keys())

        for p, ax, fig in zip(properties, axes, figures):
            if p in segment.geometry:
                Y = [segment.geometry[p]]*2
            elif p in ['chord', 'alpha', 'beta']:
                Y = [segment.geometry['inner_' + p], segment.geometry['outer_' + p]]
            else:
                raise KeyError(f"Unknown property '{p}'.")

            ax.plot(X, Y, color=COLOR3)
            ax.plot([X[0], X[0]], [0.0, Y[0]], color=COLOR1, linestyle=':', marker='.', markersize=4)
            ax.plot([X[1], X[1]], [0.0, Y[1]], color=COLOR1, linestyle=':', marker='.', markersize=4)

    plt.tight_layout()

    if plt_settings['save']:
        fname = os.path.join(plt_settings['plot_dir'], f"geo_spanwise_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname)}'")
        plt.savefig(fname, dpi=300)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')


def view_segment(segment, segment_uid, plt_settings, plot='surf', block=True):
    """Generate 3D and 2D views of aircraft geometry.

    By default, shows segment vertices and edges.
    Optionally, shows:

        * GRID (bilinear interpolation of segment surface)
        * SURF (colored bilinear interpolation of segment surface)
        * NORM (display segment normal vectors)

    Args:
        :segment: (object) data structure for individual segment
        :segment_uid: (string) name for selected segment
        :block: (bool) halt execution while figure is open
        :plot: (string) additional visualisation features ('grid', 'surf', 'norm')
    """

    logger.info("Generating segment geometry plot...")

    if not segment.state:
        return logger.error("Segment ill-defined!")

    # 2. SETUP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    figure_xyz = plt.figure(figsize=(12, 12), edgecolor=COLOR1)
    axes_xyz = figure_xyz.add_subplot(111, projection='3d')
    axes_xyz.set_aspect('equal')
    lims = np.array([[+np.inf, +np.inf, +np.inf], [-np.inf, -np.inf, -np.inf]])

    points = np.array([segment.vertices['a'],
                       segment.vertices['b'],
                       segment.vertices['c'],
                       segment.vertices['d'],
                       segment.vertices['a']])

    get_limits(points, lims, symm=False)
    size = np.sqrt(np.sum((lims[1] - lims[0])**2.0))
    scale_fig(axes_xyz, lims)

    X = points[:, 0]
    Y = points[:, 1]
    Z = points[:, 2]

    get_limits(points, lims, symm=False)
    size = np.sqrt(np.sum((lims[1] - lims[0])**2.0))
    scale_fig(axes_xyz, lims)

    if plot == 'wire':
        XW, YW, ZW = interpolate_quad(points[0], points[1], points[2], points[3], size)
        axes_xyz.plot_wireframe(XW, YW, ZW, color=COLOR1, linewidth=0.2)

    elif plot == 'surf':
        XS, YS, ZS = interpolate_quad(points[0], points[1], points[2], points[3], size)
        axes_xyz.plot_surface(XS, YS, ZS, color=COLOR5, linewidth=0.2, shade=False, cstride=1, rstride=1)

    axes_xyz.plot(X, Y, Z, color=COLOR1, marker='.', markersize=4)

    for v, n in zip(list(segment.vertices.values()), list(segment.vertices.keys())):
        text = axes_xyz.text(v[0], v[1], v[2], f"{n} ({v[0]:+.3f}, {v[1]:+.3f}, {v[2]:+.3f})", backgroundcolor='w', size='medium')
        text.set_bbox(dict(color='w', alpha=0.4))

    # 2.2. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.annotate("placeholder", xy=(0, 0), xytext=(1, 0), textcoords='axes fraction', va='bottom', ha='right')
    # display additional information

    # 2.3. DISPLAY LABELS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.set_xlabel('x [m]')
    axes_xyz.set_ylabel('y [m]')
    axes_xyz.set_zlabel('z [m]')

    axes_xyz.set_title(segment_uid)

    # 3. SEGMENT AIRFOIL ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    file_ib = segment.airfoils['inner']
    file_ob = segment.airfoils['outer']

    if not os.path.isfile(file_ib):
        logger.error(f"Airfoil {file_ib} not found!")
        return plt.show(block=block)

    if not os.path.isfile(file_ob):
        logger.error(f"Airfoil {file_ob} not found!")
        return plt.show(block=block)

    name_ib = os.path.splitext(file_ib)[1].strip('.')
    name_ob = os.path.splitext(file_ob)[1].strip('.')

    # 3.1 SEGMENT AIRFOIL ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    figure_af = plt.figure(figsize=(12, 8), edgecolor=COLOR1)

    axes_ib = figure_af.add_subplot(211)
    axes_ib.set_aspect('equal')

    axes_ob = figure_af.add_subplot(212)
    axes_ob.set_aspect('equal')

    points_ib = np.genfromtxt(file_ib, skip_header=2)
    points_ob = np.genfromtxt(file_ob, skip_header=2)

    XI = points_ib[:, 0]
    YI = points_ib[:, 1]

    YI_min = YI.min()
    YI_max = YI.max()

    XI_min = XI[YI.argmin()]
    XI_max = XI[YI.argmax()]

    XO = points_ob[:, 0]
    YO = points_ob[:, 1]

    YO_min = YO.min()
    YO_max = YO.max()

    XO_min = XO[YO.argmin()]
    XO_max = XO[YO.argmax()]

    # 2.1. DISPLAY GEOMETRY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_ib.plot(XI, YI, color=COLOR3, linewidth=1.0)
    axes_ib.plot(XI_max, YI_max, color=COLOR1, marker='x', markersize=8.0)
    axes_ib.plot(XI_min, YI_min, color=COLOR1, marker='x', markersize=8.0)

    axes_ob.plot(XO, YO, color=COLOR3, linewidth=1.0)
    axes_ob.plot(XO_max, YO_max, color=COLOR1, marker='x', markersize=8.0)
    axes_ob.plot(XO_min, YO_min, color=COLOR1, marker='x', markersize=8.0)

    text = axes_ib.text(XI_max + 0.025, YI_max, f"MAX_U ({XI_max:+.3f}, {YI_max:+.3f})", backgroundcolor='w', size='medium')
    text.set_bbox(dict(color='w', alpha=0.4))
    text = axes_ib.text(XI_min + 0.025, YI_min, f"MAX_L ({XI_min:+.3f}, {YI_min:+.3f})", backgroundcolor='w', size='medium')
    text.set_bbox(dict(color='w', alpha=0.4))

    text = axes_ob.text(XO_max + 0.025, YO_max, f"MAX_U ({XO_max:+.3f}, {YO_max:+.3f})", backgroundcolor='w', size='medium')
    text.set_bbox(dict(color='w', alpha=0.4))
    text = axes_ob.text(XO_min + 0.025, YO_min, f"MAX_L ({XO_min:+.3f}, {YO_min:+.3f})", backgroundcolor='w', size='medium')
    text.set_bbox(dict(color='w', alpha=0.4))

    # 2.2. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # display additional information
    axes_ib.annotate(f"{name_ib}", xy=(0, 0), xytext=(1, 0), textcoords='axes fraction', va='bottom', ha='right')
    axes_ob.annotate(f"{name_ob}", xy=(0, 0), xytext=(1, 0), textcoords='axes fraction', va='bottom', ha='right')

    axes_ib.set_xlabel('x/c [-]')
    axes_ib.set_ylabel('y/c [-]')
    axes_ib.set_title("inner profile")
    axes_ob.set_xlabel('x/c [-]')
    axes_ob.set_ylabel('y/c [-]')
    axes_ob.set_title("outer profile")
    figure_af.suptitle(f"{segment_uid}")
    figure_af.tight_layout()

    plt.tight_layout()

    if plt_settings['save']:
        fname = os.path.join(plt_settings['plot_dir'], f"geo_segment_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname)}'")
        plt.savefig(fname, dpi=300)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')

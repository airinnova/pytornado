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
# * Aaron Dettmann

"""
Main entry point for plotting

Developed at Airinnova AB, Stockholm, Sweden.
"""

import logging

from . import plottools as pt

from . import downwash as pl_downwash

logger = logging.getLogger(__name__)


def make_all(settings, aircraft, cur_state, vlmdata, lattice):
    """
    Evaluate settings and create plots accordingly

    Args:
        :settings: Settings instance
        :aircraft: Aircraft model
        :vlm_struct: VLM struct
        :cur_state: Current state
        :lattice: Lattice
    """

    plot_settings = {
        "plot_dir": settings.paths('d_plots'),
        "save": settings.settings['plot']['save'],
        "show": settings.settings['plot']['show'],
        "result_keys": settings.settings['plot']['results'],
    }

    # If there is nothing to plot, exit...
    if not any((plot_settings['save'], plot_settings['show'])):
        return

    # Create plots
    if settings.settings['plot']['matrix_downwash']:
        pl_downwash.view_downwash(vlmdata, plot_settings)

    if settings.settings['plot']['geometry']:
        plot_geometry_aircraft(aircraft, plot_settings)

    if settings.settings['plot']['lattice']:
        plot_lattice_aircraft(aircraft, lattice, plot_settings)

    if settings.settings['plot']['results']:
        plot_results_aircraft(aircraft, lattice, cur_state, vlmdata, plot_settings)


def plot_geometry_aircraft(aircraft, plot_settings):
    """
    Generate 2D and 3D views of full aircraft geometry

    Args:
        :aircraft: (object) data structure for aircraft model
        :plot_settings: Plot settings
    """

    logger.info("Generating geometry plot...")
    with pt.plot2d3d(aircraft, 'geometry', plot_settings) as (figure_2d, axes_2d, figure_3d, axes_3d):
        pt.add_CG(axes_2d, axes_3d, aircraft)
        pt.add_wings(axes_2d, axes_3d, aircraft)
        pt.add_controls(axes_2d, axes_3d, aircraft)


def plot_lattice_aircraft(aircraft, lattice, plot_settings):
    """
    Generate 2D and 3D views of the lattice

    Args:
        :aircraft: (object) data structure for aircraft model
        :plot_settings: Plot settings
    """

    logger.info("Generating lattice plot...")
    with pt.plot2d3d(aircraft, 'lattice', plot_settings) as (figure_2d, axes_2d, figure_3d, axes_3d):
        pt.add_CG(axes_2d, axes_3d, aircraft)
        pt.add_controls(axes_2d, axes_3d, aircraft)
        pt.add_lattice(axes_2d, axes_3d, lattice)


def plot_results_aircraft(aircraft, lattice, state, vlmdata, plot_settings):
    """
    Generate results plot

    Args:
        :aircraft: (object) data structure for aircraft model
        :plot_settings: Plot settings
    """

    logger.info("Generating results plot...")
    for key in plot_settings['result_keys']:
        with pt.plot2d3d(aircraft, f'results_{key}', plot_settings) as (_, axes_2d, figure_3d, axes_3d):
            pt.add_freestream_vector(axes_2d, axes_3d, state)
            pt.add_results(axes_2d, axes_3d, figure_3d, vlmdata, lattice, aircraft, key)

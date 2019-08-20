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
PyTornado standard functions

Developed for Airinnova AB, Stockholm, Sweden.
"""

import os
import logging

import commonlibs.logger as hlogger

from pytornado.__version__ import __version__
import pytornado.aero.vlm as vlm
import pytornado.fileio.settings as io_settings
import pytornado.fileio.cpacs as io_cpacs
import pytornado.fileio.model as io_model
import pytornado.fileio.state as io_state
import pytornado.fileio.results as io_results
import pytornado.fileio.deformation as io_deformation
import pytornado.plot.downwash as pl_downwash
import pytornado.plot.geometry as pl_geometry
import pytornado.plot.lattice as pl_lattice
import pytornado.plot.results as pl_results
from pytornado.objects.model import Aircraft
from pytornado.objects.state import FlightState
from pytornado.objects.vlm_struct import VLMData, VLMLattice

logger = logging.getLogger(__name__)

FILE_LOG = os.path.join(os.getcwd(), 'log.txt')
__prog_name__ = 'pytornado'


class StdRunArgs:
    """
    Arguments used in 'standard_run'

    Attributes:
        :run: name of file to be loaded
        :verbose: boolean flag, true for verbose logger setting
        :debug: boolean flag, true for debug logger setting
        :quiet: boolean flag, true for quiet logger setting
    """

    run = None
    verbose = False
    debug = False
    quiet = False


def get_settings(project_basename):
    """
    Read settings and return a settings instance
    """

    logger.info("Getting configuration file...")
    settings = io_settings.load(project_basename)
    return settings


def clean_project_dir(settings):
    """
    Remove old files in project directory

    Args:
        :settings: settings instance
    """

    logger.info("Removing old files...")
    settings.clean()


def standard_run(args):
    """
    Run a standard analysis

    Args:
        :args: arguments (see StdRunArgs())
    """

    # ===== Logging =====
    if args.verbose:
        level = 'info'
    elif args.debug:
        level = 'debug'
    elif args.quiet:
        level = 'quiet'
    else:
        level = 'default'

    hlogger.init(FILE_LOG, level)
    logger = logging.getLogger(__name__)

    # ===== Setup =====
    logger.info(hlogger.decorate(f"{__prog_name__} {__version__}"))

    logger.info("Getting configuration file...")
    settings = io_settings.load(project_basename=args.run)

    # ===== Setup aircraft model and flight state =====
    aircraft = Aircraft()
    if settings.aircraft_is_cpacs:
        io_cpacs.load(aircraft, settings)
    else:
        io_model.load(aircraft, settings)

    state = FlightState()
    io_state.load(state, settings)

    if settings.inputs['deformation']:
        io_deformation.load_deformation(aircraft, settings)

    # ===== Generate lattice =====
    lattice = VLMLattice()
    vlmdata = VLMData()
    vlm.set_autopanels(aircraft, settings)

    # ----- Iterate through the flight states -----
    for i, cur_state in enumerate(state.iter_states()):
        ##########################################################
        # TODO: Don't set refs here. Find better solution!
        cur_state.refs = aircraft.refs
        ##########################################################

        ##########################################################
        # TODO: Find better solution for pre_panelling() function
        make_new_subareas = True if i == 0 else False
        ##########################################################

        vlm.gen_lattice(aircraft, lattice, cur_state, settings, make_new_subareas)

        # ===== VLM =====
        vlm.calc_downwash(lattice, vlmdata)
        vlm.calc_boundary(lattice, cur_state, vlmdata)  # right-hand side terms
        vlm.solver(vlmdata)
        vlm.calc_results(lattice, cur_state, vlmdata)

        # ===== Save results =====
        if 'panelwise' in settings.outputs['save_results']:
            io_results.save_panelwise(cur_state, vlmdata, settings)

        if 'global' in settings.outputs['save_results']:
            io_results.save_glob_results(cur_state, vlmdata, settings)

        if 'loads_with_deformed_mesh' in settings.outputs['save_results']:
            io_results.save_loads(aircraft, settings, cur_state, vlmdata, lattice)

        if 'loads_with_undeformed_mesh' in settings.outputs['save_results']:
            io_results.save_loads(aircraft, settings, cur_state, vlmdata, lattice=None)

        # ===== Generate plots =====
        plt_settings = {
            "plot_dir": settings.dirs['plots'],
            "save": settings.plot['save'],
            "show": settings.plot['show']
        }

        if plt_settings['save'] or plt_settings['show']:
            if settings.plot['results_downwash']:
                pl_downwash.view_downwash(vlmdata, plt_settings)

            if settings.plot['geometry_aircraft']:
                pl_geometry.view_aircraft(aircraft, plt_settings, plot='norm')

            for wing_uid, wing in aircraft.wing.items():
                if wing_uid in settings.plot['geometry_wing']:
                    pl_geometry.view_wing(wing, wing_uid, plt_settings, plot='surf')

                    if settings.plot['geometry_property']:
                        pl_geometry.view_spanwise(wing, wing_uid, plt_settings,
                                                  properties=settings.plot['geometry_property'])

                    for segment_uid, segment in wing.segment.items():
                        if segment_uid in settings.plot['geometry_segment']:
                            pl_geometry.view_segment(segment, segment_uid, plt_settings, plot='wire')

            if settings.plot['lattice_aircraft']:
                pl_lattice.view_aircraft(aircraft, lattice, plt_settings,
                                         opt_settings=settings.plot['lattice_aircraft_optional'])

            if settings.plot['results_panelwise']:
                for result in settings.plot['results_panelwise']:
                    pl_results.view_panelwise(aircraft, cur_state, lattice, vlmdata, result, plt_settings)

        ###############################################
        # TODO: Find better solution
        ###############################################
        # Save AeroPerformance map results
        state.results['Fx'].append(vlmdata.forces['x'])
        state.results['Fy'].append(vlmdata.forces['y'])
        state.results['Fz'].append(vlmdata.forces['z'])
        state.results['FD'].append(vlmdata.forces['D'])
        state.results['FC'].append(vlmdata.forces['C'])
        state.results['FL'].append(vlmdata.forces['L'])
        state.results['Mx'].append(vlmdata.forces['l'])
        state.results['My'].append(vlmdata.forces['m'])
        state.results['Mz'].append(vlmdata.forces['n'])
        ####
        state.results['Cx'].append(vlmdata.coeffs['x'])
        state.results['Cy'].append(vlmdata.coeffs['y'])
        state.results['Cz'].append(vlmdata.coeffs['z'])
        state.results['CD'].append(vlmdata.coeffs['D'])
        state.results['CC'].append(vlmdata.coeffs['C'])
        state.results['CL'].append(vlmdata.coeffs['L'])
        state.results['Cl'].append(vlmdata.coeffs['l'])
        state.results['Cm'].append(vlmdata.coeffs['m'])
        state.results['Cn'].append(vlmdata.coeffs['n'])
        ###############################################


    ###############################################
    # Save aeroperformance map
    io_results.save_aeroperformance_map(state, settings)
    ###############################################

    logger.info(f"{__prog_name__} {__version__} terminated")

    # Return results to caller
    results = {
        "lattice": lattice,
        "vlmdata": vlmdata,
        "state": state
    }
    return results

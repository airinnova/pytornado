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
Generate project directory folder structure with input file templates.

Developed at Airinnova AB, Stockholm, Sweden.
"""


import os
import sys

from pytornado.objects.settings import Settings, PATHS
from pytornado.objects.aircraft import Aircraft
from pytornado.objects.state import FlightState
import pytornado.fileio as io


def setup_wkdir():
    """
    Create a template working directory with a minimal working example

    Notes:
        * The project directory contains all data related to the aircraft model
        * This includes flight state definitions and execution settings
    """

    # We create a separate directory for the template data
    # to avoid potential cluttering the user's directory
    project_dir = PATHS.DIR.TEMPLATE_ROOT

    if os.path.exists(project_dir):
        err_msg = f"""
        The path '{project_dir}' does already exist. Refusing to proceed.
        Please move or delete the folder, then try again.
        """
        print(err_msg, file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Creating template in folder '{project_dir}'...")
        os.makedirs(project_dir)

    project_basename = "template"
    settings_filename = project_basename + ".json"
    aircraft = Aircraft()
    state = FlightState()

    aircraft.uid = 'template_aircraft'
    wing = aircraft.add_wing('template_wing', return_wing=True)
    segment = wing.add_segment('template_segment', return_segment=True)
    control = wing.add_control('template_control', return_control=True)

    # Generate file names and create project directory
    settings = Settings(settings_filename, project_dir, check_ac_file_type=False)

    # ========== Set default values ==========
    # ---------- Settings ----------
    settings.settings['aircraft'] = aircraft.uid + '.json'
    settings.settings['state'] = project_basename + '.json'
    settings.generate_paths()

    settings.settings['vlm_autopanels_s'] = 20
    settings.settings['vlm_autopanels_c'] = 5
    settings.settings['plot']['results'] = ['cp']
    settings.settings['plot']['show'] = True

    # ---------- State ----------
    state.aero['airspeed'] = 100
    state.aero['density'] = 1.225
    state.aero['alpha'] = 2
    state.aero['beta'] = 2
    state.aero['rate_P'] = 0
    state.aero['rate_Q'] = 0
    state.aero['rate_R'] = 0

    # ---------- Aircraft ----------
    aircraft.refs['area'] = 10
    aircraft.refs['span'] = 5
    aircraft.refs['chord'] = 2
    aircraft.refs['gcenter'] = [0, 0, 0]
    aircraft.refs['rcenter'] = [0, 0, 0]

    # ---------- Wing ----------
    wing.symmetry = 2

    # ---------- Segment ----------
    segment.vertices['a'] = [0, 0, 0]
    segment.vertices['b'] = [0, 5, 0]
    segment.vertices['c'] = [2, 5, 0]
    segment.vertices['d'] = [2, 0, 0]
    segment.airfoils['inner'] = 'NACA0000'
    segment.airfoils['outer'] = 'NACA0000'

    # ---------- Control ----------
    control.device_type = 'flap'
    control.deflection = 5
    control.deflection_mirror = -5
    control.segment_uid['inner'] = 'template_segment'
    control.segment_uid['outer'] = 'template_segment'
    control.rel_vertices['eta_inner'] = 0.2
    control.rel_vertices['eta_outer'] = 0.8
    control.rel_vertices['xsi_inner'] = 0.7
    control.rel_vertices['xsi_outer'] = 0.7
    control.rel_hinge_vertices['xsi_inner'] = 0.7
    control.rel_hinge_vertices['xsi_outer'] = 0.7

    # Save settings, state and model file
    io.native.settings.save(settings)
    io.native.state.save(state, settings)
    io.native.aircraft.save(aircraft, settings)


# def cpacs2pytornado(file_cpacs):
#     """Load CPACS file and export to JSON Aircraft and state files.

#     Args:
#         :file_cpacs: (string) absolute path to project directory
#     """

#     project_basename = os.path.splitext(os.path.basename(file_cpacs))[0]
#     file_cpacs = os.path.abspath(file_cpacs)

#     settings = Settings(project_basename, wkdir=os.path.abspath(os.getcwd()))
#     settings.paths('f_aircraft') = file_cpacs

#     aircraft = Aircraft()
#     state = FlightState()

#     # Read the CPACS file
#     io.cpacs.load(aircraft, state, settings)
#     aircraft.generate(check=False)

#     # Modify file extension
#     file_cpacs = file_cpacs.replace('.xml', '.json')
#     file_cpacs = file_cpacs.replace('.XML', '.json')
#     settings.paths('f_aircraft') = file_cpacs

#     # Finally, serialise...
#     io_model.save(aircraft, settings)

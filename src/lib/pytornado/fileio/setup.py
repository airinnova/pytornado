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

import pytornado.fileio.settings as io_settings
import pytornado.fileio.model as io_model
import pytornado.fileio.state as io_state
import pytornado.fileio.cpacs as io_cpacs
from pytornado.objects.settings import Settings, DIR_TEMPLATE_WKDIR
from pytornado.objects.model import Aircraft
from pytornado.objects.state import FlightState


def setup_wkdir():
    """
    Create a template working directory with a minimal working example

    Notes:
        * The project directory contains all data related to the aircraft model
        * This includes flight state definitions and execution settings
    """

    # We create a separate directory for the template data
    # to avoid potential cluttering the user's directory
    wkdir = DIR_TEMPLATE_WKDIR

    if os.path.exists(wkdir):
        msg = f"""
        The path '{wkdir}' does already exist. Refusing to proceed.
        Please move or delete the folder, then try again.
        """
        print(msg, file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Creating template in folder '{wkdir}'...")
        os.makedirs(wkdir)
        os.chdir(wkdir)

    project_basename = "template"
    aircraft = Aircraft()
    state = FlightState()

    aircraft.uid = 'template_aircraft'
    wing = aircraft.add_wing('template_wing', return_wing=True)
    segment = wing.add_segment('template_segment', return_segment=True)
    control = wing.add_control('template_control', return_control=True)

    # Generate file names and create project directory
    settings = Settings(project_basename, wkdir=os.path.abspath(os.getcwd()), make_dirs=False)

    # ========== Set default values ==========
    # ---------- Settings ----------
    settings.inputs['aircraft'] = aircraft.uid + '.json'
    settings.inputs['state'] = project_basename
    settings.generate_file_names()
    settings.make_project_subdirs()
    settings.plot['results_panelwise'] = ['cp']
    settings.outputs['vlm_autopanels_s'] = 20
    settings.outputs['vlm_autopanels_c'] = 5
    settings.outputs['vlm_lattice'] = True
    settings.outputs['vlm_compute'] = True

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
    io_settings.save(settings)
    io_state.save(state, settings)
    io_model.save(aircraft, settings)


def cpacs2pytornado(file_cpacs):
    """Load CPACS file and export to PyTornado AIRCRAFT and STATE files.

    Args:
        :file_cpacs: (string) absolute path to project directory
    """

    project_basename = os.path.splitext(os.path.basename(file_cpacs))[0]
    file_cpacs = os.path.abspath(file_cpacs)

    settings = Settings(project_basename, wkdir=os.path.abspath(os.getcwd()))
    settings.files['aircraft'] = file_cpacs

    aircraft = Aircraft()
    state = FlightState()

    # Read the CPACS file
    io_cpacs.load(aircraft, state, settings)
    aircraft.generate(check=False)

    # Modify file extension
    file_cpacs = file_cpacs.replace('.xml', '.json')
    file_cpacs = file_cpacs.replace('.XML', '.json')
    settings.files['aircraft'] = file_cpacs

    # Finally, serialise...
    io_model.save(aircraft, settings)


##################################################################
##################################################################
# def pytornado2cpacs(file_cpacs, file_state):
#     """
#     Load CPACS file and export to PyTornado AIRCRAFT and STATE files.

#     Args:
#         :file_cpacs: (string) absolute path to project directory
#         :file_state:
#     """

#     settings = Settings()
#     # aircraft = Aircraft()
#     state = FlightState()

#     settings.wkdir = os.getcwd()
#     settings.inputs['cpacs'] = file_cpacs
#     settings.inputs['state'] = file_state

#     io_state.load(state, settings)
#     io_cpacs.save_state(state, settings)
##################################################################
##################################################################

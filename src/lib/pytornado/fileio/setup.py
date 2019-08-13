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

import pytornado.fileio.settings as io_settings
import pytornado.fileio.model as io_model
import pytornado.fileio.state as io_state
import pytornado.fileio.cpacs as io_cpacs
from pytornado.objects.settings import Settings
from pytornado.objects.model import Aircraft
from pytornado.objects.state import FlightState


def setup_wkdir():
    """
    Setup folder structure of user project directory

    Notes:
        * The project directory contains all data related to the aircraft model
        * This includes flight state definitions and execution settings
    """

    project_basename = "template"
    aircraft = Aircraft()
    state = FlightState()

    aircraft.uid = 'template_aircraft'
    aircraft.add_wing('template_wing')
    aircraft.wing['template_wing'].add_segment('template_segment')
    aircraft.wing['template_wing'].add_control('template_control')

    # Generate file names and create project directory
    settings = Settings(project_basename, wkdir=os.path.abspath(os.getcwd()),
                        make_dirs=False)
    settings.inputs['aircraft'] = aircraft.uid + '.json'
    settings.inputs['state'] = project_basename
    settings.generate_file_names()
    settings.make_project_subdirs()

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

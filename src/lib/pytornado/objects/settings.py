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
Data structures for execution settings.

Developed for Airinnova AB, Stockholm, Sweden.
"""

import os
import logging
import shutil

from pytornado.objects.utils import FixedNamespace, FixedOrderedDict
from pytornado.aero.vlm import MIN_AUTOPANELS

logger = logging.getLogger(__name__)

DIR_AIRCRAFT = 'aircraft'
DIR_AIRFOILS = 'airfoils'
DIR_DEFORMATION = 'deformation'
DIR_PLOTS = '_plots'
DIR_RESULTS = '_results'
DIR_SETTINGS = 'settings'
DIR_STATE = 'state'
DIR_TEMPLATE_WKDIR = 'pytornado'


class SettingsDefinitionError(Exception):
    """Raised when properties of SETTINGS are ill-defined"""

    pass


class Settings(FixedNamespace):
    """
    Data structure for the PyTornado execution settings

    Settings defines the tasks to be performed during execution.
    Settings also stores location of project files.

    Attributes:
        :inputs: (dict) provided input data
        :outputs: (dict) expected output data
        :plot: (dict) figures to be generated
        :wkdir: (string) location of project files
    """

    def __init__(self, project_basename, wkdir, settings_dict=None, make_dirs=True):
        """
        Initialise instance of settings.
        """

        make_template_only = True if settings_dict is None else False

        super().__init__()

        # SETTINGS -- user-provided input identifiers
        self.inputs = FixedOrderedDict()
        self.inputs['aircraft'] = None
        self.inputs['state'] = None
        self.inputs['deformation'] = False
        self.inputs['horseshoe_type'] = 2
        self.inputs['epsilon'] = 1e-6
        self.inputs['_do_normal_rotations'] = True
        self.inputs['_deformation_check'] = True
        self.inputs._freeze()

        # SETTINGS -- user-provided analysis tasks
        self.outputs = FixedOrderedDict()
        self.outputs['vlm_autopanels_c'] = None
        self.outputs['vlm_autopanels_s'] = None
        self.outputs['vlm_lattice'] = False
        self.outputs['vlm_compute'] = False
        self.outputs['save_results'] = [
                                        "NO_global",
                                        "NO_panelwise",
                                        "NO_loads_with_undeformed_mesh",
                                        "NO_loads_with_deformed_mesh"]
        self.outputs._freeze()

        # SETTINGS -- user-provided visualisation tasks
        self.plot = FixedOrderedDict()
        self.plot['geometry_aircraft'] = False
        self.plot['geometry_wing'] = None
        self.plot['geometry_segment'] = None
        self.plot['geometry_property'] = None

        self.plot['lattice_aircraft'] = False
        self.plot['lattice_aircraft_optional'] = []
        self.plot['lattice_wing'] = None
        self.plot['lattice_segment'] = None

        self.plot['results_downwash'] = False
        self.plot['results_panelwise'] = None

        self.plot['show'] = True
        self.plot['save'] = False
        self.plot._freeze()

        self.aircraft_name = None

        if not make_template_only:
            self.update_from_dict(**settings_dict)
            self.aircraft_name = os.path.splitext(self.inputs['aircraft'])[0]

        # Project directories (will be converted to abs. paths when wkdir is set)
        self.dirs = {
                "aircraft": DIR_AIRCRAFT,
                "airfoils": DIR_AIRFOILS,
                "deformation": DIR_DEFORMATION,
                "plots": DIR_PLOTS,
                "results": DIR_RESULTS,
                "settings": DIR_SETTINGS,
                "state": DIR_STATE,
                }

        self.files = {}
        self.project_basename = project_basename
        self.wkdir = wkdir

        self.generate_file_names()
        self.make_abs_paths()

        if make_dirs:
            self.make_project_subdirs()

        if not make_template_only:
            ac_file_extension = os.path.splitext(self.files['aircraft'])[-1].lower()
            if ac_file_extension not in ['.xml', '.json']:
                raise ValueError("Aircraft file must have extension '.json' or '.xml'")

            if ac_file_extension.lower() == '.json':
                self.aircraft_is_cpacs = False
            else:
                self.aircraft_is_cpacs = True

        self._freeze()

        if make_template_only is False:
            self.check()

    def generate_file_names(self):
        """Generate file names"""

        self.files = {
                "aircraft": f"{DIR_AIRCRAFT}/{self.inputs['aircraft']}",
                "deformation": f"{DIR_DEFORMATION}/{self.aircraft_name}.json",
                "settings": f"{DIR_SETTINGS}/{self.project_basename}.json",
                "state": f"{DIR_STATE}/{self.inputs['state']}.json",
                "results_global": f"{DIR_RESULTS}/{self.project_basename}_global.json",
                "results_panelwise": f"{DIR_RESULTS}/{self.project_basename}_panelwise.json",
                }

    def make_abs_paths(self):
        """Make filepaths absolute"""

        for key, dirname in self.dirs.items():
            subdir = os.path.basename(dirname)
            self.dirs[key] = os.path.join(self.wkdir, subdir)

        for key, filename in self.files.items():
            self.files[key] = os.path.join(self.wkdir, filename)

    def make_project_subdirs(self):
        """Create project subdirectories"""

        for dirpath in self.dirs.values():
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

    def update_from_dict(self, inputs, outputs, plot):
        """
        Update settings
        """

        for key, value in inputs.items():
            self.inputs[key] = value

        for key, value in outputs.items():
            self.outputs[key] = value

        for key, value in plot.items():
            self.plot[key] = value

    def clean(self):
        """
        Remove old files in project directory
        """

        dir_keys = ['plots', 'results']

        for dir_key in dir_keys:
            abs_dir = self.dirs[dir_key]
            shutil.rmtree(abs_dir, ignore_errors=True)

    def check(self):
        """Check definition of SETTINGS properties and data"""

        logger.debug("Checking settings...")

        # 2. CHECK INPUTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        if self.inputs['aircraft'] is None:
            logger.info("'inputs.aircraft' is not defined")
        elif not isinstance(self.inputs['aircraft'], str):
            raise TypeError("'inputs.aircraft' must be a valid STRING")

        if not self.inputs['aircraft']:
            raise SettingsDefinitionError("Must provide AIRCRAFT file!")

        if self.inputs['state'] is None:
            raise SettingsDefinitionError("must provide CPACS state uID or PyTornado state file!")
        elif not isinstance(self.inputs['state'], str):
            raise TypeError("'inputs.state' must be valid STRING")

        if not isinstance(self.inputs['horseshoe_type'], int) \
                or self.inputs['horseshoe_type'] not in [0, 1, 2]:
            raise ValueError("'horseshoe_type' must be of type int (0, 1, 2)")

        if not isinstance(self.inputs['epsilon'], float) or \
                not (0 < self.inputs['epsilon'] < 1):
            raise ValueError("'epsilon' must be a (small) float in range (0, 1)")

        if not isinstance(self.inputs['_do_normal_rotations'], bool):
            raise ValueError("'_do_normal_rotations' must be 'True' or 'False'")
        if not self.inputs['_do_normal_rotations']:
            logger.warning("Normal rotations are turned off (no controls and airfoils)")

        if not isinstance(self.inputs['_deformation_check'], bool):
            raise ValueError("'_deformation_check' must be 'True' or 'False'")

        # 3. CHECK OUTPUTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        for auto_panel in ['vlm_autopanels_c', 'vlm_autopanels_s']:
            if self.outputs[auto_panel] is None:
                logger.debug(f"'outputs.{auto_panel}' is None")
            elif not isinstance(self.outputs[auto_panel], int):
                raise TypeError(f"'outputs.{auto_panel}' must be integer")
            elif self.outputs[auto_panel] < MIN_AUTOPANELS:
                raise ValueError(f"'outputs.{auto_panel}' must be at least {MIN_AUTOPANELS}")

        if not isinstance(self.outputs['vlm_lattice'], bool):
            raise TypeError("'outputs.vlm_lattice' must be True or False")

        if not isinstance(self.outputs['vlm_compute'], bool):
            raise TypeError("'outputs.vlm_compute' must be True or False")

        # 4. CHECK PLOTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        if not self.plot['geometry_aircraft']:
            logger.info("'geometry_aircraft' not defined")
        elif not isinstance(self.plot['geometry_aircraft'], bool):
            raise TypeError("'plot.geometry_aircraft' must be True or False")

        if isinstance(self.plot['geometry_wing'], str):
            self.plot['geometry_wing'] = [self.plot['geometry_wing']]
        if self.plot['geometry_wing'] is None:
            logger.info("'geometry_wing' not defined")
            self.plot['geometry_wing'] = list()
        elif not isinstance(self.plot['geometry_wing'], list):
            raise TypeError("'plot.geometry_wing' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['geometry_wing']):
            raise TypeError("'plot.geometry_wing' must be LIST of STRING")

        if isinstance(self.plot['geometry_segment'], str):
            self.plot['geometry_segment'] = [self.plot['geometry_segment']]
        if self.plot['geometry_segment'] is None:
            logger.info("'geometry_segment' not defined")
            self.plot['geometry_segment'] = list()
        elif not isinstance(self.plot['geometry_segment'], list):
            raise TypeError("'plot.geometry_segment' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['geometry_segment']):
            raise TypeError("'plot.geometry_segment' must be LIST of STRING")

        if isinstance(self.plot['geometry_property'], str):
            self.plot['geometry_property'] = [self.plot['geometry_property']]
        if self.plot['geometry_property'] is None:
            logger.info("'geometry_property' not defined")
            self.plot['geometry_property'] = list()
        elif not isinstance(self.plot['geometry_property'], list):
            raise TypeError("'plot.geometry_property' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['geometry_property']):
            raise TypeError("'plot.geometry_property' must be LIST of STRING")

        if not isinstance(self.plot['lattice_aircraft'], bool):
            raise TypeError("'plot.lattice_aircraft' must be True or False")

        if isinstance(self.plot['lattice_wing'], str):
            self.plot['lattice_wing'] = [self.plot['lattice_wing']]
        if self.plot['lattice_wing'] is None:
            logger.info("'lattice_wing' not defined")
            self.plot['lattice_wing'] = list()
        elif not isinstance(self.plot['lattice_wing'], list):
            raise TypeError("'plot.lattice_wing' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['lattice_wing']):
            raise TypeError("'plot.lattice_wing' must be LIST of STRING")

        if isinstance(self.plot['lattice_segment'], str):
            self.plot['lattice_segment'] = [self.plot['lattice_segment']]
        if self.plot['lattice_segment'] is None:
            logger.info("'lattice_segment' not defined")
            self.plot['lattice_segment'] = list()
        elif not isinstance(self.plot['lattice_segment'], list):
            raise TypeError("'plot.lattice_segment' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['lattice_segment']):
            raise TypeError("'plot.lattice_segment' must be LIST of STRING")

        if not isinstance(self.plot['results_downwash'], bool):
            raise TypeError("'plot.results_downwash' must be True or False")

        if isinstance(self.plot['results_panelwise'], str):
            self.plot['results_panelwise'] = [self.plot['results_panelwise']]
        if self.plot['results_panelwise'] is None:
            logger.info("'results_panelwise' not defined")
            self.plot['results_panelwise'] = list()
        elif not isinstance(self.plot['results_panelwise'], list):
            raise TypeError("'plot.results_panelwise' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['results_panelwise']):
            raise TypeError("'plot.results_panelwise' must be LIST of STRING")

        if not isinstance(self.plot['show'], bool):
            raise TypeError("'plot.show' must be True or False")
        if not isinstance(self.plot['save'], bool):
            raise TypeError("'plot.save' must be True or False")

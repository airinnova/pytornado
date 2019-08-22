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
from pathlib import Path

from commonlibs.fileio.paths import ProjectPaths

logger = logging.getLogger(__name__)

# ===== Directories =====
# Input directories
DIR_AIRCRAFT = 'aircraft'
DIR_AIRFOILS = 'airfoils'
DIR_DEFORMATION = 'deformation'
DIR_SETTINGS = 'settings'
DIR_STATE = 'state'
# Output directories
DIR_PLOTS = '_plots'
DIR_RESULTS = '_results'
# Template directory name
DIR_TEMPLATE_WKDIR = 'pytornado'

DEFAULT_PLOT_DICT = {
    'geometry_aircraft': (False, bool),
    'geometry_wing': ([], list),
    'geometry_segment': ([], list),
    'geometry_property': ([], list),
    'lattice_aircraft': (False, bool),
    'lattice_aircraft_optional': ([], list),
    'lattice_wing': ([], list),
    'lattice_segment': ([], list),
    'results_downwash': (False, bool),
    'results_panelwise': ([], list),
    'show': (True, bool),
    'save': (False, bool),
}

DEFAULT_SETTINGS = {
    'aircraft': (None, str),
    'state': (None, str),
    'deformation': (None, (None, str)),
    'vlm_autopanels_c': (4, int),
    'vlm_autopanels_s': (4, int),
    'save_results': ([], list),
    'plot': (DEFAULT_PLOT_DICT, dict),
    # Underscore settings are "hidden" settings that generally shouldn't be changed
    '_do_normal_rotations': (True, bool),
    '_deformation_check': (True, bool),
    '_horseshoe_type': (2, int),
    '_epsilon': (1e-6, float),
}

# self.settings['save_results'] = [
#     "NO_global",
#     "NO_panelwise",
#     "NO_loads_with_undeformed_mesh",
#     "NO_loads_with_deformed_mesh"
# ]


class Settings:

    def __init__(self, settings_filename, project_dir, *,
                 settings_dict=None, make_dirs=True, check_ac_file_type=True):
        """
        Data structure with PyTornado execution settings

        Attributes:
            :settings_filename: Name of the settings file
            :project_dir: PyTornado project directory (where all data is expected)
            :settings_dict: Basic settings data as a dictionary
            :make_dirs: (bool) Flag for creation of project directories
        """

        self.project_dir = Path(project_dir).resolve()
        self.project_basename = os.path.splitext(settings_filename)[0]

        # Initialise settings dict
        self.settings = {}
        for key1, (default1, _) in DEFAULT_SETTINGS.items():
            if isinstance(default1, dict):
                self.settings[key1] = {}
                for key2, (default2, _) in default1.items():
                    self.settings[key1][key2] = default2
            else:
                self.settings[key1] = default1

        if settings_dict is not None:
            self.update_from_dict(settings_dict)

        self.paths = None
        self.generate_paths()

        self.aircraft_is_cpacs = None
        if check_ac_file_type:
            self.check_aircraft_file_type()

        if make_dirs:
            self.paths.make_dirs_for_groups('dir')

    def generate_paths(self):
        """
        Initialise the file structure
        """

        # Output subdirectory to structure results from APM analyses
        output_subdir = f"/{self.project_basename}" + "_{counter:03d}"

        # ===== Directories =====
        self.paths = ProjectPaths(self.project_dir)
        self.paths.add_path(uid='d_aircraft', path=DIR_AIRCRAFT, uid_groups='dir')
        self.paths.add_path(uid='d_airfoils', path=DIR_AIRFOILS, uid_groups='dir')
        self.paths.add_path(uid='d_deformation', path=DIR_DEFORMATION, uid_groups='dir')
        self.paths.add_path(uid='d_settings', path=DIR_SETTINGS, uid_groups='dir')
        self.paths.add_path(uid='d_state', path=DIR_STATE, uid_groups='dir')
        # Output directories
        self.paths.add_path(uid='d_plots_TOP', path=DIR_PLOTS, uid_groups=('dir', 'tmp'))
        self.paths.add_path(uid='d_results_TOP', path=DIR_RESULTS, uid_groups=('dir', 'tmp'))
        self.paths.add_path(uid='d_plots', path=DIR_PLOTS+output_subdir, uid_groups=('dir', 'tmp'))
        self.paths.add_path(uid='d_results', path=DIR_RESULTS+output_subdir, uid_groups=('dir', 'tmp'))

        # ===== Files =====
        self.paths.add_subpath(uid_parent='d_aircraft', uid='f_aircraft', path=f"{self.settings['aircraft']}")
        self.paths.add_subpath(uid_parent='d_deformation', uid='f_deformation', path=f"{self.settings['deformation']}")
        self.paths.add_subpath(uid_parent='d_settings', uid='f_settings', path=f"{self.project_basename}.json")
        self.paths.add_subpath(uid_parent='d_state', uid='f_state', path=f"{self.settings['state']}")
        # Output files
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_global', path=f"{self.project_basename}_global.json")
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_panelwise', path=f"{self.project_basename}_global.json")
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_apm_global', path=f"{self.project_basename}_APM.json")

    def check_aircraft_file_type(self):
        """Check whether aircraft is a CPACS or a JSON file"""

        ac_file_extension = self.paths('f_aircraft').suffix.lower()

        if ac_file_extension not in ['.xml', '.json']:
            raise ValueError("Aircraft file must have extension '.json' or '.xml' (CPACS)")

        if ac_file_extension == '.json':
            self.aircraft_is_cpacs = False
        else:
            self.aircraft_is_cpacs = True

    def update_from_dict(self, settings_dict):
        """
        Update settings from dictionary structures

        Args:
            :settings: Dictionary with general settings
            :plot: Dictionary with plot settings
        """

        for key, value in settings_dict.items():
            self.settings[key] = value

        self._check_settings_dict()

    def clean(self):
        """
        Remove old files in project directory
        """

        self.paths.rm_dirs_for_groups('tmp')

    def _check_settings_dict(self):
        """
        Check that settings dictionary contains valid input arguments
        """

        logger.debug("Checking settings...")

        def check_dict(d_template, d_test):
            """
            Check dictionary
            """

            for key, (value, dtype) in d_template.items():
                # Make dtype into tuple
                dtype = (dtype,) if not isinstance(dtype, tuple) else dtype
                if None not in dtype:
                    if not isinstance(d_test[key], dtype):
                        err_msg = f"""
                        Unexpected data type for key '{key}'.
                        Expected {dtype}, got {type(d_test[key])}.
                        """
                        raise TypeError(err_msg)
                if dtype[0] is dict:
                    check_dict(value, d_test[key])

        # Check against template dict
        check_dict(DEFAULT_SETTINGS, self.settings)

        # --------------------------------------------------------------------
        # if not isinstance(self.settings['horseshoe_type'], int) \
        #         or self.settings['horseshoe_type'] not in [0, 1, 2]:
        #     raise ValueError("'horseshoe_type' must be of type int (0, 1, 2)")

        # if not isinstance(self.settings['epsilon'], float) or \
        #         not (0 < self.settings['epsilon'] < 1):
        #     raise ValueError("'epsilon' must be a (small) float in range (0, 1)")
        # --------------------------------------------------------------------

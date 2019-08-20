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

from pytornado.objects.utils import FixedOrderedDict

logger = logging.getLogger(__name__)

DIR_AIRCRAFT = 'aircraft'
DIR_AIRFOILS = 'airfoils'
DIR_DEFORMATION = 'deformation'
DIR_PLOTS = '_plots'
DIR_RESULTS = '_results'
DIR_SETTINGS = 'settings'
DIR_STATE = 'state'
DIR_TEMPLATE_WKDIR = 'pytornado'

#####################
#####################

from pathlib import Path, PurePath
from collections import defaultdict


class ProjectPaths:

    UID_ROOT = 'root'

    def __init__(self, root_dir):
        """
        Class providing tools for filepath handling

        Paths stored and returned in this class are based on the 'Path' object
        from the pathlib standard library, see also:

            * https://docs.python.org/3/library/pathlib.html

        Args:
            :root_dir: Project root directory

        'root_dir' is the project root directory. All other other added to this
        class are assumed to reside inside the 'root_dir'. In other words,
        absolute file paths are assembled based on the 'root_dir'.

        Attributes:
            :abs_paths: Dictionary with absolute paths
            :groups: Dictionary with grouped file UIDs
        """

        self.abs_paths = {}
        self.groups = defaultdict(list)
        self._set_project_root_dir(root_dir)

    def __call__(self, uid):
        """
        Shortcut to return a path

        Args:
            :uid: Path UID
        """

        return self.abs_paths[uid]

    @property
    def root(self):
        """Return the Path object for the project root directory"""

        return self.abs_paths[self.UID_ROOT]

    def _set_project_root_dir(self, root_dir):
        """
        Set the project root directory

        Args:
            :root_dir: Project root directory
        """

        # Save the absolute path
        self.abs_paths[self.UID_ROOT] = Path(root_dir).resolve()

    def add_path(self, uid, path, uid_group=None, is_absolute=False):
        """
        Add a path

        Args:
            :uid: Unique identifier
            :path: Path string
            :uid_group: Optional UID to identify files by groups
            :is_absolute: Flag indicating if given 'path' is absolute
        """

        if uid in self.abs_paths.keys():
            raise ValueError(f"UID '{uid}' already used")

        path = Path(path)

        if not is_absolute:
            path = self.__class__.join_paths(self.root, path)

        self.abs_paths[uid] = path

        if uid_group is not None:
            self.groups[uid_group].append(uid)

    def add_subpath(self, uid_parent, uid, path, uid_group=None):
        """
        Add a child folder or child path to an existing parent path

        Args:
            :uid_parent: UID of the parent directory
            :uid: UID of the new path
            :path: relative path to add
            :uid_group: Optional UID to identify files by groups
        """

        if uid_parent not in self.abs_paths.keys():
            raise ValueError(f"Parent UID '{uid_parent}' not found")

        parent_path = self.abs_paths[uid_parent]
        self.abs_paths[uid] = self.__class__.join_paths(parent_path, path)

        if uid_group is not None:
            self.groups[uid_group].append(uid)

    def format_path(self, uid, *args, **kwargs):
        """
        Run a string format() method on a path and return new path

        Args:
            :uid: Unique identifier

        All other standard arguments and keyword arguments are forwared to the
        format() method of 'str'
        """

        if uid in self.abs_paths.keys():
            raise ValueError(f"Parent UID '{uid_parent}' not found")

        formatted_path = str(self.abs_paths[uid]).format(*args, **kwargs)
        return formatted_path

    @staticmethod
    def join_paths(path1, path2):
        """
        Join two paths

        Args:
            :path1: Leading path
            :path2: Trailing path
        """

        path = PurePath(path1).joinpath(path2)
        return Path(path)

    def iter_group_paths(self, uid_group):
        """
        Return a generator with paths belong to group with given UID

        Args:
            :uid_group: Group UID
        """

        for uid in self.groups[uid_group]:
            yield self.abs_paths[uid]

#####################
#####################


class Settings:

    def __init__(self, project_basename, wkdir, settings_dict=None, make_dirs=True):
        """
        Data structure with execution settings

        Attributes:
            :settings: (dict) provided input data
            :plot: (dict) figures to be generated
            :wkdir: (string) location of project files
        """


        make_template_only = True if settings_dict is None else False

        self.settings = FixedOrderedDict()
        self.settings['aircraft'] = None
        self.settings['state'] = None
        self.settings['deformation'] = False
        self.settings['horseshoe_type'] = 2
        self.settings['epsilon'] = 1e-6
        self.settings['_do_normal_rotations'] = True
        self.settings['_deformation_check'] = True
        self.settings['vlm_autopanels_c'] = None
        self.settings['vlm_autopanels_s'] = None
        self.settings['save_results'] = [
            "NO_global",
            "NO_panelwise",
            "NO_loads_with_undeformed_mesh",
            "NO_loads_with_deformed_mesh"
        ]
        self.settings._freeze()

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
            self.aircraft_name = os.path.splitext(self.settings['aircraft'])[0]

        # Paths
        self.paths = ProjectPaths(wkdir)
        self.paths.add_path(uid='d_aircraft', path=DIR_AIRCRAFT, uid_group='dir')
        self.paths.add_path(uid='d_airfoils', path=DIR_AIRFOILS, uid_group='dir')
        self.paths.add_path(uid='d_deformation', path=DIR_DEFORMATION, uid_group='dir')
        self.paths.add_path(uid='d_plots', path=DIR_PLOTS, uid_group='dir')
        self.paths.add_path(uid='d_results', path=DIR_RESULTS, uid_group='dir')
        self.paths.add_path(uid='d_settings', path=DIR_SETTINGS, uid_group='dir')
        self.paths.add_path(uid='d_state', path=DIR_STATE, uid_group='dir')

        # Files
        self.paths.add_subpath(uid_parent='d_aircraft', uid='f_aircraft', path=f"{self.settings['aircraft']}", uid_group='file')
        self.paths.add_subpath(uid_parent='d_deformation', uid='f_deformation', path=f"{self.aircraft_name}.json", uid_group='file')
        self.paths.add_subpath(uid_parent='d_settings', uid='f_settings', path=f"{project_basename}.json", uid_group='file')
        self.paths.add_subpath(uid_parent='d_state', uid='f_state', path=f"{self.settings['state']}.json", uid_group='file')
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_global', path=f"{project_basename}_global.json", uid_group='file')
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_panelwise', path=f"{project_basename}_global.json", uid_group='file')
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_apm_global', path=f"{project_basename}_APM.json", uid_group='file')
        ####################################################

        if make_dirs:
            self.make_project_subdirs()

        if not make_template_only:
            ac_file_extension = self.paths('f_aircraft').suffix
            if ac_file_extension not in ['.xml', '.json']:
                raise ValueError("Aircraft file must have extension '.json' or '.xml'")

            if ac_file_extension.lower() == '.json':
                self.aircraft_is_cpacs = False
            else:
                self.aircraft_is_cpacs = True

    def make_project_subdirs(self):
        """Create project subdirectories"""

        for dirpath in self.paths.iter_group_paths(uid_group='dir'):
            dirpath.mkdir(parents=True, exist_ok=True)

    def update_from_dict(self, settings, plot):
        """
        Update settings
        """

        for key, value in settings.items():
            self.settings[key] = value

        for key, value in plot.items():
            self.plot[key] = value

###################################################

    # def clean(self):
    #     """
    #     Remove old files in project directory
    #     """

    #     dir_keys = ['plots', 'results']

    #     for dir_key in dir_keys:
    #         abs_dir = self.dirs[dir_key]
    #         shutil.rmtree(abs_dir, ignore_errors=True)

###################################################

    # def check(self):
    #     """Check definition of SETTINGS properties and data"""

    #     logger.debug("Checking settings...")

    #     # 2. CHECK INPUTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #     if self.settings['aircraft'] is None:
    #         logger.info("'settings.aircraft' is not defined")
    #     elif not isinstance(self.settings['aircraft'], str):
    #         raise TypeError("'settings.aircraft' must be a valid STRING")

    #     if not self.settings['aircraft']:
    #         raise ValueError("Must provide AIRCRAFT file!")

    #     if self.settings['state'] is None:
    #         raise ValueError("must provide CPACS state uID or PyTornado state file!")
    #     elif not isinstance(self.settings['state'], str):
    #         raise TypeError("'settings.state' must be valid STRING")

    #     if not isinstance(self.settings['horseshoe_type'], int) \
    #             or self.settings['horseshoe_type'] not in [0, 1, 2]:
    #         raise ValueError("'horseshoe_type' must be of type int (0, 1, 2)")

    #     if not isinstance(self.settings['epsilon'], float) or \
    #             not (0 < self.settings['epsilon'] < 1):
    #         raise ValueError("'epsilon' must be a (small) float in range (0, 1)")

    #     if not isinstance(self.settings['_do_normal_rotations'], bool):
    #         raise ValueError("'_do_normal_rotations' must be 'True' or 'False'")
    #     if not self.settings['_do_normal_rotations']:
    #         logger.warning("Normal rotations are turned off (no controls and airfoils)")

    #     if not isinstance(self.settings['_deformation_check'], bool):
    #         raise ValueError("'_deformation_check' must be 'True' or 'False'")

    #     # 4. CHECK PLOTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #     if not self.plot['geometry_aircraft']:
    #         logger.info("'geometry_aircraft' not defined")
    #     elif not isinstance(self.plot['geometry_aircraft'], bool):
    #         raise TypeError("'plot.geometry_aircraft' must be True or False")

    #     if isinstance(self.plot['geometry_wing'], str):
    #         self.plot['geometry_wing'] = [self.plot['geometry_wing']]
    #     if self.plot['geometry_wing'] is None:
    #         logger.info("'geometry_wing' not defined")
    #         self.plot['geometry_wing'] = list()
    #     elif not isinstance(self.plot['geometry_wing'], list):
    #         raise TypeError("'plot.geometry_wing' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['geometry_wing']):
    #         raise TypeError("'plot.geometry_wing' must be LIST of STRING")

    #     if isinstance(self.plot['geometry_segment'], str):
    #         self.plot['geometry_segment'] = [self.plot['geometry_segment']]
    #     if self.plot['geometry_segment'] is None:
    #         logger.info("'geometry_segment' not defined")
    #         self.plot['geometry_segment'] = list()
    #     elif not isinstance(self.plot['geometry_segment'], list):
    #         raise TypeError("'plot.geometry_segment' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['geometry_segment']):
    #         raise TypeError("'plot.geometry_segment' must be LIST of STRING")

    #     if isinstance(self.plot['geometry_property'], str):
    #         self.plot['geometry_property'] = [self.plot['geometry_property']]
    #     if self.plot['geometry_property'] is None:
    #         logger.info("'geometry_property' not defined")
    #         self.plot['geometry_property'] = list()
    #     elif not isinstance(self.plot['geometry_property'], list):
    #         raise TypeError("'plot.geometry_property' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['geometry_property']):
    #         raise TypeError("'plot.geometry_property' must be LIST of STRING")

    #     if not isinstance(self.plot['lattice_aircraft'], bool):
    #         raise TypeError("'plot.lattice_aircraft' must be True or False")

    #     if isinstance(self.plot['lattice_wing'], str):
    #         self.plot['lattice_wing'] = [self.plot['lattice_wing']]
    #     if self.plot['lattice_wing'] is None:
    #         logger.info("'lattice_wing' not defined")
    #         self.plot['lattice_wing'] = list()
    #     elif not isinstance(self.plot['lattice_wing'], list):
    #         raise TypeError("'plot.lattice_wing' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['lattice_wing']):
    #         raise TypeError("'plot.lattice_wing' must be LIST of STRING")

    #     if isinstance(self.plot['lattice_segment'], str):
    #         self.plot['lattice_segment'] = [self.plot['lattice_segment']]
    #     if self.plot['lattice_segment'] is None:
    #         logger.info("'lattice_segment' not defined")
    #         self.plot['lattice_segment'] = list()
    #     elif not isinstance(self.plot['lattice_segment'], list):
    #         raise TypeError("'plot.lattice_segment' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['lattice_segment']):
    #         raise TypeError("'plot.lattice_segment' must be LIST of STRING")

    #     if not isinstance(self.plot['results_downwash'], bool):
    #         raise TypeError("'plot.results_downwash' must be True or False")

    #     if isinstance(self.plot['results_panelwise'], str):
    #         self.plot['results_panelwise'] = [self.plot['results_panelwise']]
    #     if self.plot['results_panelwise'] is None:
    #         logger.info("'results_panelwise' not defined")
    #         self.plot['results_panelwise'] = list()
    #     elif not isinstance(self.plot['results_panelwise'], list):
    #         raise TypeError("'plot.results_panelwise' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['results_panelwise']):
    #         raise TypeError("'plot.results_panelwise' must be LIST of STRING")

    #     if not isinstance(self.plot['show'], bool):
    #         raise TypeError("'plot.show' must be True or False")
    #     if not isinstance(self.plot['save'], bool):
    #         raise TypeError("'plot.save' must be True or False")

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
Wrapper module for aeroframe
"""

import os
import glob
import shutil
import json

import aeroframe.fileio as io

from pytornado.stdfun import standard_run, StdRunArgs, clean_project_dir, get_settings
from pytornado.objects.settings import DIR_RESULTS, DIR_PLOTS, DIR_DEFORMATION


class AeroWrapper:

    def __init__(self, aeroframe_files):
        """
        API for the "aeroframe" aeroelastic framework

        Args:
            :aeroframe_files: file structure of aeroframe program
        """

        # File structure of aeroframe programme
        self.aeroframe_files = aeroframe_files

        # General execution settings for the standard run
        self.exec_args = self.load_exec_settings()

        # ID for the set file (e.g. "A380" if the set file is called "A380.json")
        self.set_file_id = self.exec_args.run.replace('.json', '')

        # Get an instance of Settings()
        self.goto_cfd()
        self.pytornado_init_settings = get_settings(self.set_file_id)

        # Generate file paths relevant for own program
        self.own_files = AeroWrapperFiles(aeroframe_files, self.set_file_id)

        # Modify settings file
        self.modify_settings_file('outputs.save_results', ["loads_with_undeformed_mesh"])

        # ----- Let user decide, otherwise set sensible defaults -----
        self.modify_settings_file('plot.save', True, dont_overwrite=True)
        self.modify_settings_file('plot.show', False, dont_overwrite=True)

        # Last computed solution
        self.last_solution = None

    def goto_cfd(self):
        """
        Change into the aerodynamics project folder
        """

        os.chdir(self.aeroframe_files.dirs['cfd'])

    def load_exec_settings(self):
        """
        Load the main execution settings for the aerodynamics code

        Returns:
            :args: arguments which can be passed to 'run_analysis'
        """

        settings = io.load_root_settings(self.aeroframe_files)
        settings = settings['cfd_model']['exec_settings']

        args = StdRunArgs()
        args.run = settings['run']
        args.verbose = settings['verbose']
        args.debug = settings['debug']
        args.quiet = settings['quiet']

        return args

    def run_analysis(self, turn_off_deform=False):
        """
        Run a full analysis

        Note:
            * Computed loads are shared

        Args:
            :turn_off_deform: flag which can be used to turn off all deformations for a certain run
        """

        # PyTornado requires the user to run the analysis in the project directory
        self.goto_cfd()

        if turn_off_deform:
            self.set_deformation_off()
        else:
            self.set_deformation_on()
            self.import_shared_deformation()

        self.last_solution = standard_run(self.exec_args)
        self.share_loads()

    def set_deformation_off(self):
        """
        Modify the settings file to turn off all deformations
        """

        self.modify_settings_file('inputs.deformation', False)

    def set_deformation_on(self):
        """
        Modify the settings file to turn on all deformations
        """

        self.modify_settings_file('inputs.deformation', True)

    def share_loads(self):
        """
        Share loads within the framework
        """

        dest_dir = self.aeroframe_files.dirs["shared_from_cfd"]

        # All JSON files in "results" will be copied to shared folder
        os.chdir(self.own_files.dirs['results'])

        for load_file in glob.glob("*.json"):
            shutil.copy(load_file, dest_dir)

    def import_shared_deformation(self):
        """
        Import the deformations from "shared" folder
        """

        shared_def_file = self.aeroframe_files.files['shared_def_file']
        native_def_file = self.own_files.files['native_def_file']

        if not os.path.exists("deformation"):
            os.makedirs("deformation")

        shutil.copyfile(shared_def_file, native_def_file)

    def modify_settings_file(self, setting, value, dont_overwrite=False):
        """
        Modify the PyTornado settings file

        Note:
            * If 'setting' does already exist it will be replaced with 'value'
            * If 'setting' does not exist it will be added

        Args:
            :setting: name of the setting to modify
            :value: value to be set
        """

        settings_subdict, setting = setting.split('.')
        set_file = self.own_files.files['settings_file']

        with open(set_file, 'r') as fp:
            all_settings = json.load(fp)

        if dont_overwrite and setting in all_settings[settings_subdict].keys():
            return

        with open(set_file, 'w') as fp:
            all_settings[settings_subdict][setting] = value
            json.dump(all_settings, fp, indent=4, separators=(',', ': '))

    def clean(self):
        """
        Remove old result file from a previous analysis
        """

        clean_project_dir(self.pytornado_init_settings)


class AeroWrapperFiles:

    def __init__(self, aeroframe_files, set_file_id):
        """
        Files pertinent to the aerodynamics code

        Args:
            :aeroframe_files: file structure of aeroframe program
        """

        self.aeroframe_files = aeroframe_files
        self.set_file_id = set_file_id
        cfd_dir = self.aeroframe_files.dirs['cfd']

        self.files = {
                "settings_file": os.path.join(cfd_dir, f"settings/{self.set_file_id}.json"),
                }

        # TODO: make work with CPACS
        with open(self.files['settings_file'], "r") as fp:
            settings_dict = json.load(fp)

        self.aircraft_name = os.path.splitext(settings_dict['inputs']['aircraft'])[0]

        self.files.update({
                "native_def_file": os.path.join(cfd_dir, f"{DIR_DEFORMATION}/{self.aircraft_name}.json"),
                })

        self.dirs = {
                "results": os.path.join(cfd_dir, DIR_RESULTS),
                "plots": os.path.join(cfd_dir, DIR_PLOTS)
                }

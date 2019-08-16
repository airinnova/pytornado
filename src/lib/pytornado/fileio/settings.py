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
Functions for reading and writing of PyTornado execution settings file.

Developed at Airinnova AB, Stockholm, Sweden.
"""

import os
import logging
import json

from commonlibs.logger import truncate_filepath

from pytornado.objects.settings import Settings
from pytornado.fileio.utils import dump_pretty_json

logger = logging.getLogger(__name__)


def load(project_basename):
    """
    Read PyTornado settings from PyTornado settings file.

    Args:
        :settings: (object) data structure for execution settings
    """

    set_file = os.path.join(os.getcwd(), "settings", f"{project_basename}.json")
    logger.info(f"Reading settings from file '{truncate_filepath(set_file)}'...")

    if not os.path.exists(set_file):
        raise IOError(f"File '{set_file}' not found")

    with open(set_file, 'r') as fp:
        settings_dict = json.load(fp)

    settings = Settings(project_basename=project_basename,
                        wkdir=os.path.abspath(os.getcwd()),
                        settings_dict=settings_dict)
    return settings


def save(settings):
    """
    Write settings to native settings file

    Args:
        :settings: (object) data structure for execution settings
    """

    set_file = settings.files['settings']
    logger.info(f"Saving settings to file '{truncate_filepath(set_file)}'...")

    output = {}

    for key in ['inputs', 'outputs', 'plot']:
        output[key] = dict(getattr(settings, key))

        # Do not save special underscore settings by default
        delete_keys = []
        for sub_key in output[key].keys():
            if sub_key.startswith("_"):
                delete_keys.append(sub_key)

        for sub_key in delete_keys:
            del output[key][sub_key]

    with open(set_file, 'w') as fp:
        dump_pretty_json(output, fp)

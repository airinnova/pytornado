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
Write VLM results back to CPACS

Developed at Airinnova AB, Stockholm, Sweden.
"""

import logging

from commonlibs.logger import truncate_filepath

from pytornado.fileio.cpacs.utils import open_tixi, open_tigl, XPATHS, add_vector

try:
    from pytornado.fileio.cpacs.utils import tixiwrapper, tiglwrapper
except:
    pass

logger = logging.getLogger(__name__)


def save_aeroperformance_map(state, settings):
    """
    Write aeroperformance map results back to CPACS

    Args:
        :state: (object) data structure for operating conditions
        :settings: (object) data structure for execution settings
    """

    state.results

    cpacs_file = settings.paths('f_aircraft')
    logger.info(f"Writing aeroperformance map results to '{truncate_filepath(cpacs_file)}'")

    # open CPACS file, write back to CPACS...
    tixi = open_tixi(cpacs_file)

    cpacs_mappings = {
        ('cl', 'CL'),
        ('cd', 'CD'),
        ('cs', 'CC'),
    }

    for cpacs_key, native_key in cpacs_mappings:
        vector = state.results[native_key]
        xpath = XPATHS.APM(tixi) + "/" + cpacs_key
        add_vector(tixi, xpath, vector)

    tixi.saveDocument(str(cpacs_file))

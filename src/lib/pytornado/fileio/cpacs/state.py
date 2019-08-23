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
Functions for conversion of CPACS aircraft definition to native model

Developed at Airinnova AB, Stockholm, Sweden.
"""

import logging

from pytornado.fileio.cpacs.utils import open_tixi, open_tigl, XPATHS
from pytornado.objects.state import FlightState, ALTITUDE, ALPHA, BETA, MACH, RATE_P, RATE_Q, RATE_R

try:
    from pytornado.fileio.cpacs_utils import tixiwrapper, tiglwrapper
except:
    pass

logger = logging.getLogger(__name__)

# ======================================================================
# AeroPerformanceMap
# ======================================================================


def load(settings):
    """
    Load the flight state from the CPACS aeroperformance map
    """

    cpacs_file = settings.paths('f_aircraft')
    logger.info(f"Loading state from CPACS file: {cpacs_file}...")
    if not cpacs_file.is_file():
        err_msg = f"File '{cpacs_file}' not found or not valid file"
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    tixi = open_tixi(cpacs_file)
    tigl = open_tigl(tixi)

    uid_apm = XPATHS.get_uid_apm(tixi)
    logger.info(f"Using aeroperformance map with UID '{uid_apm}'")

    state_dict = get_aero_dict_from_APM(tixi, uid_apm=uid_apm)
    state = FlightState()
    state.update_from_dict(**state_dict)
    return state


def get_aero_dict_from_APM(tixi, uid_apm):
    """
    Extract the aeroperformance map from CPACS and return an aero dictionary

    Args:
        :tixi: Tixi handle
        :uid_apm: UID of the aeroperformance map
    """

    aero_dict = {
        "aero": {
            ALTITUDE: None,
            ALPHA: None,
            BETA: None,
            MACH: None,
            RATE_P: None,
            RATE_Q: None,
            RATE_R: None,
        }
    }

    # Map the CPACS state names to the PyTornado STATE NAMES
    state_params = {
        'altitude': ALTITUDE,
        'machNumber': MACH,
        'angleOfAttack': ALPHA,
        'angleOfSideslip': BETA,
    }

    vector_lens = set()
    xpath_apm = XPATHS.APM(tixi, uid_apm)
    for cpacs_key, state_key in state_params.items():
        xpath_apm_param = xpath_apm + '/' + cpacs_key
        vector_len = tixi.getVectorSize(xpath_apm_param)
        vector_lens.add(vector_len)
        values = tixi.getFloatVector(xpath_apm_param, vector_len)
        aero_dict['aero'][state_key] = list(values)

    if len(list(vector_lens)) > 1:
        err_msg = f"""
        CPACS AeroPerformanceMap with UID {uid_apm} contains vectors of
        different length. All vectors must have the same number of elements.
        """
        raise ValueError(err_msg)

    # NOTE: Roll rate are not an input parameter in CPACS
    for rate in [RATE_P, RATE_Q, RATE_R]:
        aero_dict['aero'][rate] = [0]*vector_len

    return aero_dict

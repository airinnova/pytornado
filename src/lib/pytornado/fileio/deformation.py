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
Reading the aircraft deformation file.

Developed at Airinnova AB, Stockholm, Sweden.
"""

import os
import logging
import json

import numpy as np
from commonlibs.logger import truncate_filepath
from commonlibs.math.vectors import vector_projection

import pytornado.objects.objecttools as ot

logger = logging.getLogger(__name__)


def load_deformation(aircraft, settings):
    """
    Loads the aircraft deformation file if it exitsts.

    Args:
        :aircraft: (obj) aircraft
        :settings: (obj) settings
    """

    filepath = settings.files['deformation']
    logger.info(f"Reading deformation from file '{truncate_filepath(filepath)}'")

    if not os.path.exists(filepath):
        raise IOError(f"file '{filepath}' not found")

    with open(filepath, 'r') as infile:
        deformation_model = json.load(infile)

    for entry in deformation_model:
        wing_uid = entry['wing']
        segment_uid = entry['segment']
        mirror = entry['mirror']

        aircraft.wing[wing_uid].is_deformed = True
        segment = aircraft.wing[wing_uid].segment[segment_uid]

        if mirror:
            deformation = segment.deformation_mirror = {}
        else:
            deformation = segment.deformation = {}

        deformation['eta'] = []
        deformation['ux'] = []
        deformation['uy'] = []
        deformation['uz'] = []
        deformation['theta'] = []

        for def_entry in entry['deform']:
            eta = def_entry['eta']
            ux, uy, uz, tx, ty, tz = def_entry['deform']
            theta = np.array([tx, ty, tz])

            # Convert twist vector onto rotation axis for deformations with sign
            theta_proj = vector_projection(theta, segment.deformation_rot_axis)
            sign = np.sign(np.dot(theta_proj, segment.deformation_rot_axis))
            theta_scalar = sign*np.linalg.norm(theta_proj)

            deformation['eta'].append(eta)
            deformation['ux'].append(ux)
            deformation['uy'].append(uy)
            deformation['uz'].append(uz)
            deformation['theta'].append(theta_scalar)

    # Process the deformation
    for this_segment, _ in ot.all_segments(aircraft):
        segment = this_segment[2]

        if segment.parent_wing.is_deformed:
            segment.make_deformation_spline_interpolators()

    if not settings.inputs['_deformation_check']:
        logger.warning("Skipping deformation check (there may be discontinuities)")
        return

    # Check continuity
    for this_wing in ot.all_wings(aircraft):
        wing = this_wing[2]

        if wing.is_deformed:
            wing.check_deformation_continuity()

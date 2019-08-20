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
Data structure for aircraft flight state.

Developed for Airinnova AB, Stockholm, Sweden.
"""


import logging

import numpy as np
from numpy import cos, sin, deg2rad
from ambiance import Atmosphere

from pytornado.objects.utils import FixedNamespace, FixedOrderedDict

logger = logging.getLogger(__name__)


AIRSPEED = 'airspeed'
DENSITY = 'density'
ALPHA = 'alpha'
BETA = 'beta'
RATE_P = 'rate_P'
RATE_Q = 'rate_Q'
RATE_R = 'rate_R'

# Fundamental parameters used to define a flight state
STATE_BASE_PARAMS = [
    'airspeed', 'density', 'alpha', 'beta',
    'rate_P', 'rate_Q', 'rate_R'
]

GLOBAL_COEFFS = [
    'Fx', 'Fy', 'Fz',
    'FD', 'FC', 'FL',
    'Mx', 'My', 'Mz',
    'Cx', 'Cy', 'Cz',
    'CD', 'CC', 'CL',
    'Cl', 'Cm', 'Cn',
]

FLIGH_STATE_PROPS = [
    'alpha',
    'beta',
    'rate_P',
    'rate_Q',
    'rate_R',
    'mach',
    'altitude',
    'airspeed',
    'density',
]


class CurrentState:

    def __init__(self):
        """
        Class reflecting the currently analysed state

        Attributes:
            :aero: (dict) see FlightState()
            :refs: (dict) see model.Aircraft()
            :free_stream_velocity_vector: (vector)  free stream vector
        """

        self.aero = None
        self.refs = None
        self.free_stream_velocity_vector = None


class FlightState:

    def __init__(self):
        """
        Data structure for the flight conditions

        Attributes:
            :aero: (dict) aerodynamic operating parameters
            :num_apm_values: (int) Number of values is APM
            :idx_current_state: (int) Index of the current flight state

        Note:
            * The angles 'alpha' and 'beta' are assumed to be given in DEGREES!
              Alpha and beta are user input. The angles stored in this state class
              will not be changed during runtime.
        """

        self.aero = FixedOrderedDict()
        for prop in FLIGH_STATE_PROPS:
            self.aero[prop] = None
        self.aero._freeze()

        self.results = {}
        for param in GLOBAL_COEFFS:
            self.results[param] = []

        # Number of values in the aeroperformance map
        self.num_apm_values = 0
        self.idx_current_state = None

    @property
    def free_stream_velocity_vector(self):
        """Return the free stream velocity vector (incoming flow)"""

        i = self.idx_current_state
        alpha = deg2rad(self.aero['alpha'][i])
        beta = deg2rad(self.aero['beta'][i])
        airspeed = self.aero['airspeed'][i]

        if None in [alpha, beta, airspeed]:
            raise RuntimeError("'alpha', 'beta' and 'airspeed' must be set")

        free_stream_vel = airspeed*np.array([cos(alpha)*cos(beta),
                                             -sin(beta),
                                             sin(alpha)*cos(beta)])
        return free_stream_vel

    def update_from_dict(self, aero):
        """Update state using a dictionary"""

        # ----- Make everything into lists -----
        array_lenghts = set()
        for key, value in aero.items():
            if not isinstance(value, list):
                value = [value]

            array_lenghts.add(len(value))
            self.aero[key] = value

        if len(array_lenghts) > 1:
            raise ValueError("State arrays have different lenghts!")

        self.num_apm_values = int(list(array_lenghts)[0])

        # ----- We can allow different input combinations -----
        all_props = {'airspeed', 'mach', 'density', 'altitude'}
        valid_prop_pairs = [
            {'airspeed', 'density'},
            {'airspeed', 'altitude'},
            {'mach', 'altitude'},
        ]

        is_input = {prop: False for prop in all_props}
        for prop in all_props:
            if self.aero[prop] is not None:
                if all(isinstance(value, (int, float)) for value in self.aero[prop]):
                    is_input[prop] = True

        input_props = set(prop for prop in all_props if is_input[prop] is True)
        if input_props not in valid_prop_pairs:
            err_msg = """
            Invalid combination: You may set:
            (1) 'airspeed' and 'density' or
            (2) 'airspeed' and 'altitude' or
            (3) 'mach' and 'altitude'
            Make sure the remaining values are all set to 'None'.
            """
            raise ValueError(err_msg)

        # ----- Compute airspeed and density if necessary -----
        if is_input['altitude']:
            atmosphere = Atmosphere(self.aero['altitude'])
            density = list(atmosphere.density)
            speed_of_sound = list(atmosphere.speed_of_sound)

        if not is_input['density']:
            self.aero['density'] = density

        if is_input['mach']:
            self.aero['airspeed'] = np.array(self.aero['mach'])*np.array(speed_of_sound)

        self.check_values()

    def check_values(self):
        """Make sure input values have correct format"""

        # Make sure to always use float arrays
        for prop in FLIGH_STATE_PROPS:
            if self.aero[prop] is not None:
                self.aero[prop] = np.array(self.aero[prop], dtype=float)

        # Check that angles are in correct range
        for angle in ['alpha', 'beta']:
            range_is_not_ok = (self.aero['alpha'] < -90) & (self.aero['alpha'] > 90)
            if any(range_is_not_ok):
                raise ValueError(f"Angle '{angle}' must be in range [-90, 90] degrees")

    def iter_states(self):
        """
        Iterator which yields a dictionary for each flight state
        """

        for i in range(0, self.num_apm_values):
            self.idx_current_state = i

            current_state = CurrentState()

            current_aero = FixedOrderedDict()
            for param in STATE_BASE_PARAMS:
                current_aero[param] = float(self.aero[param][i])
            current_aero._freeze()

            current_state.aero = current_aero
            current_state.free_stream_velocity_vector = self.free_stream_velocity_vector
            yield current_state

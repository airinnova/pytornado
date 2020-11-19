#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2019-2020 Airinnova AB and the PyTornado authors
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

# Author: Aaron Dettmann

"""
Model definition
"""

from numbers import Number

from mframework import FeatureSpec, ModelSpec

from ._run import run_model
from ._util import Schemas as S

# =================
# ===== MODEL =====
# =================
mspec = ModelSpec()

# ----- Flight state -----
fspec = FeatureSpec()
fspec.add_prop_spec(
    'airspeed',
    S.pos_number,
    doc="True airspeed [m/s]."
)
fspec.add_prop_spec(
    'alpha',
    {'type': Number, '>': -90, '<': 90},
    doc="Angle of attack [deg]."
)
fspec.add_prop_spec(
    'beta',
    {'type': Number, '>': -90, '<': 90},
    doc="Side-slip angle [deg]."
)
fspec.add_prop_spec(
    'altitude',
    S.any_num,
    doc="Flight altitude [m]. When setting the altitude atmospheric \
         properties such as the ambient *air density* or (if required) *speed \
         of sound* are computed automatically. The ICAO 1993 standard \
         atmosphere is assumed when computing these atmospheric properties."
)
fspec.add_prop_spec(
    'density',
    S.any_num,
    doc="Air density [kg/m³]."
)
fspec.add_prop_spec(
    'mach',
    S.any_num,
    doc="Mach number [1]."
)
fspec.add_prop_spec(
    'rate_P',
    S.any_num,
    doc="Roll rate [rad/s]."
)
fspec.add_prop_spec(
    'rate_Q',
    S.any_num,
    doc="Pitch rate [rad/s]."
)
fspec.add_prop_spec(
    'rate_R',
    S.any_num,
    doc="Yaw rate [rad/s]."
)
mspec.add_feature_spec(
    'state',
    fspec,
    singleton=False,
    required=True,
    doc="Use the ``'state'`` feature to define the aircraft flight state. To \
         compute aerodynamic forces, the true airspeed and ambient air \
         density must be known. There are multiple allowed combinations to \
         define the aircraft speed: \n \
         \n \
         * ``'airspeed'`` and ``'density'`` \n \
         * ``'mach'`` and ``'altitude'`` \n \
         * ``'airspeed'`` and ``'altitude'`` \n \
         \n \
         If you define use 'altitude as input, the ambient atmospheric \
         properties are computed assuming the ICAO 1993 standard atmosphere."
)

# ----- Wing -----
fspec = FeatureSpec()
fspec.add_prop_spec(
    'symmetry',
    {
        'type': int,
        'one_of': [0, 1, 2]
    },
    doc="Define symmetry properties of the wing. **TODO**"
)
fspec.add_prop_spec(
    'segment',
    {
        'type': dict,
        'schema': {
            'vertices': {
                'type': dict,
                'schema': {
                    'a': S.vector3x1,
                    'b': S.vector3x1,
                    'c': S.vector3x1,
                    'd': S.vector3x1,
                },
            },
            'airfoils': {
                'type': dict,
                'schema': {
                    'inner': S.string,
                    'outer': S.string,
                },
            },
        },
    },
    singleton=False,
    uid_required=True,
    doc="Add a wing segment to the aircraft model. **TODO**",
)
fspec.add_prop_spec(
    'control',
    {
        'type': dict,
        'schema': {
            'device_type': {
                'type': str,
                'one_of': ['flap', 'slat'],
            },
            'deflection': S.any_num,
            'deflection_mirror': S.any_num,
            'segment_uids': {
                'inner': S.string,
                'outer': S.string,
            },
            'rel_vertices': {
                'eta_inner': S.any_num,
                'eta_outer': S.any_num,
                'xi_inner': S.any_num,
                'xi_outer': S.any_num,
            },
            'rel_hinge_vertices': {
                'xi_inner': S.any_num,
                'xi_outer': S.any_num,
            },
        },
    },
    singleton=False,
    required=False,
    uid_required=False,
    doc="Add a control surface to the aircraft model. **TODO**'",
)
mspec.add_feature_spec(
    'wing',
    fspec,
    singleton=True,
    required=False,
    doc="Add a wing to the aircraft model. A wing consists of one or multiple \
         segments. There can be control surfaces spanning across the \
         segments. **TODO**"
)

# ----- Deformation -----
fspec = FeatureSpec()
fspec.add_prop_spec(
    'wing_uid',
    S.string,
    doc="**TODO**"
)
# TODO: deformation field
mspec.add_feature_spec(
    'deformation',
    fspec,
    singleton=True,
    required=False,
    doc="Not yet implemented. Deformation field for aeroelastic analyses. **TODO**"
)

# ----- Reference value -----
fspec = FeatureSpec()
fspec.add_prop_spec(
    'area',
    S.pos_number,
    doc="Reference area [m²]."
)
fspec.add_prop_spec(
    'span',
    S.pos_number,
    doc="Reference span [m]."
)
fspec.add_prop_spec(
    'chord',
    S.pos_number,
    doc="Reference chord [m]."
)
fspec.add_prop_spec(
    'gcenter',
    S.vector3x1,
    doc="Reference centre of mass."
)
fspec.add_prop_spec(
    'rcenter',
    S.vector3x1,
    doc="Reference centre of rotation."
)
mspec.add_feature_spec(
    'refs',
    fspec,
    singleton=True,
    required=False,
    doc="Reference values"
)

# ----- Global settings -----
schema_plot = {
    'type': dict,
    'schema': {
        'show': {'type': bool},
        'save': {'type': bool},
        'opt': {'type': list, 'item_types': str},
    },
}
fspec = FeatureSpec()
fspec.add_prop_spec(
    'plot_geometry',
    schema_plot,
    singleton=True,
    required=False,
    doc="Create a geometry plot."
)
fspec.add_prop_spec(
    'plot_lattice',
    schema_plot,
    singleton=True,
    required=False,
    doc="Create a plot of the VLM mesh."
)
fspec.add_prop_spec(
    'plot_results',
    schema_plot,
    singleton=False,
    required=False,
    doc="Create a plot of VLM results."
)
fspec.add_prop_spec(
    'save_dir',
    S.string,
    singleton=True,
    required=False,
    doc="Directory for output files. **TODO**"
)
mspec.add_feature_spec(
    'settings',
    fspec,
    singleton=True,
    required=False,
    doc="Use the ``'settings'`` to define global settings."
)


# ===================
# ===== RESULTS =====
# ===================
rspec = ModelSpec()

# ===== TODO =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'plots',
    {'type': dict},
    doc="Plot files"
)
rspec.add_feature_spec(
    'files',
    fspec,
    singleton=True,
    doc="Output files."
)


mspec.results = rspec


class Model(mspec.user_class):

    def run(self):
        super().run()
        run_model(self)
        return self.results

    @classmethod
    def from_example(cls):
        raise NotImplementedError

    @classmethod
    def from_cpacs(cls):
        raise NotImplementedError

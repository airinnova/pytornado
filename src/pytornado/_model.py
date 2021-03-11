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

"""
Model definition
"""

from enum import Enum
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
    max_items=1,
    doc="True airspeed [m/s]."
)
fspec.add_prop_spec(
    'alpha',
    {'type': Number, '>': -90, '<': 90},
    max_items=1,
    doc="Angle of attack [deg]."
)
fspec.add_prop_spec(
    'beta',
    {'type': Number, '>': -90, '<': 90},
    max_items=1,
    doc="Side-slip angle [deg]."
)
fspec.add_prop_spec(
    'altitude',
    S.any_num,
    required=0,
    max_items=1,
    doc="Flight altitude [m]. When setting the altitude atmospheric \
         properties such as the ambient *air density* or (if required) *speed \
         of sound* are computed automatically. The ICAO 1993 standard \
         atmosphere is assumed when computing these atmospheric properties."
)
fspec.add_prop_spec(
    'density',
    S.any_num,
    required=0,
    max_items=1,
    doc="Air density [kg/m³]."
)
fspec.add_prop_spec(
    'mach',
    S.any_num,
    required=0,
    doc="Mach number [1]."
)
fspec.add_prop_spec(
    'rate_P',
    S.any_num,
    required=0,
    max_items=1,
    doc="Roll rate [rad/s]."
)
fspec.add_prop_spec(
    'rate_Q',
    S.any_num,
    max_items=1,
    doc="Pitch rate [rad/s]."
)
fspec.add_prop_spec(
    'rate_R',
    S.any_num,
    max_items=1,
    doc="Yaw rate [rad/s]."
)
mspec.add_feature_spec(
    'state',
    fspec,
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
    required=0,
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
    required=0,
    uid_required=False,
    doc="Add a control surface to the aircraft model. **TODO**'",
)
mspec.add_feature_spec(
    'wing',
    fspec,
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
    required=0,
    max_items=1,
    doc="Not yet implemented. Deformation field for aeroelastic analyses. **TODO**"
)

# ----- Reference value -----
fspec = FeatureSpec()
fspec.add_prop_spec(
    'area',
    S.pos_number,
    max_items=1,
    doc="Reference area [m²]."
)
fspec.add_prop_spec(
    'span',
    S.pos_number,
    max_items=1,
    doc="Reference span [m]."
)
fspec.add_prop_spec(
    'chord',
    S.pos_number,
    max_items=1,
    doc="Reference chord [m]."
)
fspec.add_prop_spec(
    'gcenter',
    S.vector3x1,
    max_items=1,
    doc="Reference centre of mass."
)
fspec.add_prop_spec(
    'rcenter',
    S.vector3x1,
    max_items=1,
    doc="Reference centre of rotation."
)
mspec.add_feature_spec(
    'refs',
    fspec,
    max_items=1,
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
    max_items=1,
    required=0,
    doc="Create a geometry plot."
)
fspec.add_prop_spec(
    'plot_lattice',
    schema_plot,
    max_items=1,
    required=0,
    doc="Create a plot of the VLM mesh."
)
fspec.add_prop_spec(
    'plot_results',
    schema_plot,
    max_items=1,
    required=0,
    doc="Create a plot of VLM results."
)
fspec.add_prop_spec(
    'save_dir',
    S.string,
    max_items=1,
    required=0,
    doc="Directory for output files. **TODO**"
)
mspec.add_feature_spec(
    'settings',
    fspec,
    max_items=1,
    required=0,
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
    max_items=1,
    doc="Output files."
)


mspec.results = rspec

# ===== MODEL =====


class Builtin(Enum):
    """Built-in models"""

    RECT_WING = 'rect_wing'

    @classmethod
    def to_list(cls):
        return [e.value for e in cls]


class Model(mspec.user_class):

    def run(self):
        super().run()
        run_model(self)
        return self.results

    @classmethod
    def from_example(cls, example=Builtin.RECT_WING.value):
        if example == Builtin.RECT_WING.value:
            return get_rectangular_wing()
        else:
            raise ValueError('unknown model: {example!r}')

    @classmethod
    def from_cpacs(cls):
        raise NotImplementedError


def get_rectangular_wing():
    model = Model()

    state = model.add_feature('state')
    state.set('airspeed', 100)
    state.set('alpha', 5)
    state.set('beta', 0)
    state.set('density', 1.25)
    state.set('rate_P', 0)
    state.set('rate_Q', 0)
    state.set('rate_R', 0)

    wing = model.add_feature('wing')
    wing.add('symmetry', 0)
    segment = {
        'vertices': {
            'a': [0, 0, 0],
            'b': [0, 5, 0],
            'c': [-2, 5, 0],
            'd': [-2, 5, 0],
        }
    }
    wing.add('segment', segment, uid='main_wing')

    refs = model.set_feature('refs')
    refs.set('area', 10)
    refs.set('span', 5)
    refs.set('chord', 2)
    refs.set('gcenter', [0, 0, 0])
    refs.set('rcenter', [0, 0, 0])

    return model

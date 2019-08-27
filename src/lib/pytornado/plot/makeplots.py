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
Main entry point for plotting

Developed at Airinnova AB, Stockholm, Sweden.
"""

from . import downwash as pl_downwash
from . import geometry as pl_geometry
from . import lattice as pl_lattice
from . import results as pl_results


def make_all(settings, aircraft, cur_state, vlmdata, lattice):
    """
    Evaluate settings and create plots accordingly

    Args:
        :settings: Settings instance
        :aircraft: Aircraft model
        :vlm_struct: VLM struct
        :cur_state: Current state
        :lattice: Lattice
    """

    plt_settings = {
        "plot_dir": settings.paths('d_plots'),
        "save": settings.settings['plot']['save'],
        "show": settings.settings['plot']['show']
    }

    if plt_settings['save'] or plt_settings['show']:
        if settings.settings['plot']['results_downwash']:
            pl_downwash.view_downwash(vlmdata, plt_settings)

        if settings.settings['plot']['geometry_aircraft']:
            pl_geometry.view_aircraft(aircraft, plt_settings)

        for wing_uid, wing in aircraft.wing.items():
            if wing_uid in settings.settings['plot']['geometry_wing']:
                pl_geometry.view_wing(wing, wing_uid, plt_settings, plot='surf')

                if settings.settings['plot']['geometry_property']:
                    pl_geometry.view_spanwise(wing, wing_uid, plt_settings,
                                              properties=settings.settings['plot']['geometry_property'])

                for segment_uid, segment in wing.segment.items():
                    if segment_uid in settings.settings['plot']['geometry_segment']:
                        pl_geometry.view_segment(segment, segment_uid, plt_settings, plot='wire')

        if settings.settings['plot']['lattice_aircraft']:
            pl_lattice.view_aircraft(aircraft, lattice, plt_settings,
                                     opt_settings=settings.settings['plot']['lattice_aircraft_optional'])

        if settings.settings['plot']['results_panelwise']:
            for result in settings.settings['plot']['results_panelwise']:
                pl_results.view_panelwise(aircraft, cur_state, lattice, vlmdata, result, plt_settings)

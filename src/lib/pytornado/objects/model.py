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
Data structures for aircraft model and aircraft components.

Developed for Airinnova AB, Stockholm, Sweden.
"""


from collections import OrderedDict
from copy import copy
from math import sqrt, sin, cos, tan, asin, atan2, degrees, radians
import logging
import os

import numpy as np
from scipy.interpolate import CubicSpline
from commonlibs.math.vectors import get_plane_line_intersect, rotate_vector_around_axis

from pytornado.objects.utils import FixedNamespace, FixedOrderedDict
from pytornado.objects.airfoils import Airfoil, MorphAirfoil
from pytornado.fileio.airfoil_from_file import import_airfoil_data

# Global unit vectors
X_axis = np.array([1, 0, 0])
Y_axis = np.array([0, 1, 0])
Z_axis = np.array([0, 0, 1])

TOL = 1.0e-02

MIN_XSI_LIMIT = 0.01
MIN_ETA_LIMIT = 0.01

logger = logging.getLogger(__name__)


class ComponentDefinitionError(Exception):
    """Raised during AIRCRAFT generation when COMPONENT is ill-defined."""

    pass


class Aircraft(FixedNamespace):
    """
    Data structure for the PyTornado aircraft model.

        * AIRCRAFT has a hierarchical structure of components.
        * AIRCRAFT has WING components, contained in AIRCRAFT.WING OrderedDict.
        * Components are accessed using their unique identifier, must be a STRING.
        * AIRCRAFT represents the entire aircraft.

    Attributes:
        :name: (string) AIRCRAFT model identifier
        :version: (string) AIRCRAFT model iteration identifier
        :aircraft: (dict) AIRCRAFT reference values
        :wing: (dict) AIRCRAFT components: WING
        :size: (float) AIRCRAFT geometry size measure
        :area: (float) AIRCRAFT surface area
        :state: (bool) AIRCRAFT component definition state
    """

    def __init__(self):
        """
        Initialise instance of AIRCRAFT.

        AIRCRAFT inherits from FIXEDNAMESPACE.
        Upon initialisation, attributes of AIRCRAFT are created and fixed.
        Only existing attributes may be modified afterward.
        """

        super().__init__()

        self.uid = None

        self.reset()
        self._freeze()

    @property
    def has_deformed_wings(self):
        """
        True if any wing are deformed
        """

        for wing in self.wing.values():
            if wing.is_deformed:
                return True
        return False

    def turn_off_all_deformation(self):
        """
        Master switch which turns off all deformation
        """

        for wing in self.wing.values():
            wing.is_deformed = False

    def turn_on_all_deformation(self):
        """
        Master switch which turns on all deformation
        """

        for wing in self.wing.values():
            if wing.was_deformed:
                wing.is_deformed = True

    def add_wing(self, wing_uid, return_wing=False):
        """
        Update AIRCRAFT.WING with new WING component.

        Args:
            :wing_uid: (string) identifier for wing
            :return_wing: (bool) returns handle to new wing if TRUE (default: FALSE)

        Returns:
            (?) NONE or AIRCRAFT.WING[NAME_WING]
        """

        if not wing_uid:
            raise ComponentDefinitionError("Empty uid string!")
        elif wing_uid in self.wing:
            raise ValueError(f"wing '{wing_uid}' is already defined!")

        self.wing.update({wing_uid: Wing(wing_uid)})

        return self.wing[wing_uid] if return_wing else None

    def generate(self, check=True):
        """
        Generate AIRCRAFT model from provided data.

        Procedure is as follows:
            * check if AIRCRAFT properties are correctly defined.
            * generate WING components and sub-components.
            * generate AIRCRAFT SIZE and AREA.
        """

        logger.debug(f"Generating aircraft '{self.uid}'...")

        # 1. CHECK PROPERTIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        if not self.uid:
            raise ComponentDefinitionError("'name' is not defined.")
        elif not isinstance(self.uid, str):
            raise TypeError("name' must be valid STRING.")

        if not self.version:
            raise ComponentDefinitionError("'version' is not defined.")
        elif not isinstance(self.uid, str):
            raise TypeError("version' must be valid STRING.")

        if check:
            self.check_refs()

        # 2. GENERATE WING COMPONENTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        self.area = 0.0
        bbox = np.zeros((2, 3))
        uids = list()

        for wing_uid, wing in self.wing.items():
            logger.debug(f"Generating wing '{wing_uid}'...")

            # CHECK DATA and generate SEGMENT, CONTROL, AREA, SPAN
            wing.generate()

            # aircraft area as sum of wing areas
            self.area += wing.area
            uids.append(wing_uid)

            for segment_uid, segment in wing.segment.items():
                # segment vertices
                points = np.array(list(segment.vertices.values()))
                points_min = points.min(axis=0)
                points_max = points.max(axis=0)

                indices_min = points_min < bbox[0, :]
                indices_max = points_max > bbox[1, :]

                # update bounding box
                bbox[0, indices_min] = points_min[indices_min]
                bbox[1, indices_max] = points_max[indices_max]

                # segment center weighted by area
                center = 0.25*sum(points)

                # account for symmetry
                if wing.symmetry == 1:
                    if -points_max[2] < bbox[0, 2]:
                        bbox[0, 2] = -points_max[2]

                    if -points_min[2] > bbox[1, 2]:
                        bbox[1, 2] = -points_min[2]

                    center[2] = 0.0

                if wing.symmetry == 2:
                    if -points_max[1] < bbox[0, 1]:
                        bbox[0, 1] = -points_max[1]

                    if -points_min[1] > bbox[1, 1]:
                        bbox[1, 1] = -points_min[1]

                    center[1] = 0.0

                if wing.symmetry == 3:
                    if -points_max[0] < bbox[0, 0]:
                        bbox[0, 0] = -points_max[0]

                    if -points_min[0] > bbox[1, 0]:
                        bbox[1, 0] = -points_min[0]

                    center[0] = 0.0

                if segment_uid in uids:
                    raise ComponentDefinitionError("duplicate component name '{}'!".format(segment_uid))

                uids.append(wing_uid)

        # approx. characteristic size of aircraft (diagonal of bbox)
        self.size = np.linalg.norm(bbox[1, :] - bbox[0, :])
        self.state = True

    def check_refs(self):
        """Check type and value of properties in WING.REFS."""

        logger.info("Checking reference values...")

        # 1. CHECK REFERENCE VALUES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        if self.refs['gcenter'] is None:
            raise ComponentDefinitionError("'refs.gcenter' is not defined.")
        elif isinstance(self.refs['gcenter'], (list, np.ndarray)) and len(self.refs['gcenter']) == 3:

            if not isinstance(self.refs['gcenter'][0], (float, int)):
                raise TypeError("x-coordinate of 'self.gcenter' must be FLOAT.")
            if not isinstance(self.refs['gcenter'][1], (float, int)):
                raise TypeError("y-coordinate of 'self.gcenter' must be FLOAT.")
            if not isinstance(self.refs['gcenter'][2], (float, int)):
                raise TypeError("z-coordinate of 'self.gcenter' must be FLOAT.")

            # convert to NUMPY array
            self.refs['gcenter'] = np.array(self.refs['gcenter'], dtype=float, order='C')

        else:
            raise TypeError("'self.gcenter' must be ARRAY of FLOAT [X, Y, Z].")

        if self.refs['rcenter'] is None:
            raise ComponentDefinitionError("'refs.rcenter' is not defined.")
        elif isinstance(self.refs['rcenter'], (list, np.ndarray)) and len(self.refs['rcenter']) == 3:

            if not isinstance(self.refs['rcenter'][0], (float, int)):
                raise TypeError("x-coordinate of 'self.rcenter' must be FLOAT.")
            if not isinstance(self.refs['rcenter'][1], (float, int)):
                raise TypeError("y-coordinate of 'self.rcenter' must be FLOAT.")
            if not isinstance(self.refs['rcenter'][2], (float, int)):
                raise TypeError("z-coordinate of 'self.rcenter' must be FLOAT.")

            # convert to MUMPY array
            self.refs['rcenter'] = np.array(self.refs['rcenter'], dtype=float, order='C')

        else:
            raise TypeError("'self.rcenter' must be ARRAY of FLOAT [X, Y, Z].")

        if self.refs['area'] is None:
            raise ComponentDefinitionError("'refs.area' is not defined.")
        elif not isinstance(self.refs['area'], (float, int)):
            raise TypeError("'refs.area' must be positive FLOAT.")
        elif not self.refs['area'] >= 0.0:
            raise ValueError("'refs.area' must be positive.")
        else:
            self.refs['area'] = float(self.refs['area'])

        if self.refs['span'] is None:
            raise ComponentDefinitionError("'refs.span' is not defined.")
        elif not isinstance(self.refs['span'], (float, int)):
            raise TypeError("'refs.span' must be positive FLOAT.")
        elif not self.refs['span'] >= 0.0:
            raise ValueError("'refs.span' must be positive.")
        else:
            self.refs['span'] = float(self.refs['span'])

        if self.refs['chord'] is None:
            raise ComponentDefinitionError("'refs.chord' is not defined.")
        elif not isinstance(self.refs['chord'], (float, int)):
            raise TypeError("'refs.chord' must be positive FLOAT.")
        elif not self.refs['chord'] >= 0.0:
            raise ValueError("'refs.chord' must be positive.")
        else:
            self.refs['chord'] = float(self.refs['chord'])

    def reset(self):
        """
        Re-initialise AIRCRAFT properties and data.

        This deletes all components of AIRCRAFT.
        """

        # PROPERTY -- user-provided model identifier
        self.uid = "AIRCRAFT"
        # PROPERTY -- user-provided version identifier
        self.version = "VERSION0"

        # DATA -- calculated total wing span and area
        self.size = None
        self.area = None

        # COMPONENTS -- user-defined lifting surfaces
        self.wing = OrderedDict()

        # PROPERTIES -- user-provided reference values
        self.refs = FixedOrderedDict()
        self.refs['area'] = None
        self.refs['span'] = None
        self.refs['chord'] = None
        self.refs['gcenter'] = None
        self.refs['rcenter'] = None
        self.refs._freeze()

        # component definition state
        self.state = False


class Wing(FixedNamespace):
    """
    Data structure for AIRCRAFT component: WING.

        * WING is a component of AIRCRAFT.
        * WING has WINGSEGMENT components, contained in WING.SEGMENT OrderedDict.
        * WING has WINGCONTROL components, contained in WING.CONTROL OrderedDict.
        * Components are accessed using their unique identifier, must be a STRING.
        * WING represents a lifting surface.

    Attributes:
        :span: (float) total span of WINGSEGMENT components
        :area: (float) total area of WINGSEGMENT components
        :segment: (dict) WING components: WINGSEGMENT
        :control: (dict) WING components: WINGCONTROL
        :symmetry: (int) WING symmetry property (0: none; 1: yz; 2: xz; 3: xy)
        :state: (bool) WING attribute definition state
    """

    def __init__(self, wing_uid):
        """
        Initialise instance of WING.

        WING inherits from FIXEDNAMESPACE.
        Upon initialisation, attributes of WING are created and fixed.
        Only existing attributes may be modified afterward.
        """

        super().__init__()

        # PROPERTY -- user-provided symmetry flag
        self.uid = wing_uid
        self.symmetry = None

        # DATA -- calculated total wing span and area
        self.span = None
        self.area = None

        # COMPONENTS -- user-defined lifting surface segments
        # COMPONENTS -- user-defined control surfaces
        self.segment = OrderedDict()
        self.control = OrderedDict()

        # By default wings are not deformed
        # Flag used to toggle between deformed/undeformed state
        self.is_deformed = False
        self.was_deformed = False

        # component definition state
        self.state = False

        self._freeze()

    @property
    def is_deformed(self):
        return self._is_deformed

    @is_deformed.setter
    def is_deformed(self, is_deformed):
        self._is_deformed = is_deformed

        if self.is_deformed is True:
            self.was_deformed = True

    def add_segment(self, segment_uid, return_segment=False):
        """
        Update WING.SEGMENT with new SEGMENT component.

        Args:
            :segment_uid: (string) segment identifier
            :return_segment: (bool) returns handle to new SEGMENT if TRUE (default: FALSE)

        Returns:
            (?) NONE or WING.SEGMENT[NAME_SEGMENT]
        """

        if not segment_uid:
            raise ComponentDefinitionError("Empty name string!")
        elif segment_uid in self.segment.keys():
            raise ValueError(f"segment '{segment_uid}' already exists!")

        self.segment.update({segment_uid: WingSegment(self, segment_uid)})
        return self.segment[segment_uid] if return_segment else None

    def add_control(self, control_uid, return_control=False):
        """
        Update WING.CONTROL with new CONTROL component.

        Args:
            :control_uid: (string) control identifier
            :return_control: (bool) returns handle to new CONTROL if TRUE (default: FALSE)

        Returns:
            (?) NONE or WING.CONTROL[NAME_CONTROL]
        """

        if not control_uid:
            raise ComponentDefinitionError("empty name string!")
        elif control_uid in self.control.keys():
            raise ValueError(f"Control '{control_uid}' already exists!")

        self.control.update({control_uid: WingControl(self, control_uid)})

        return self.control[control_uid] if return_control else None

    def generate(self):
        """
        Generate WING data and components.

        Procedure is as follows:
            * Check if WING properties are correctly defined.
            * Generate WINGSEGMENT VERTICES, GEOMETRY, AREA and WING SPAN, AREA.
            * Generate WINGSEGMENT POSITION.
            * Check if WINGSEGMENT components form continuous WING.
            * Check if WINGCONTROL components or nearly coincide.
            * Generate WINGCONTROL VERTICES.
        """

        # 1. CHECK WING PROPERTIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        if self.symmetry is None:
            raise ComponentDefinitionError("'symmetry' is not defined.")
        elif not isinstance(self.symmetry, int):
            raise TypeError("'symmetry' must be an INTEGER.")
        elif self.symmetry not in [0, 1, 2, 3]:
            raise ValueError("'symmetry' must be 0, 1, 2 or 3.")

        # 2. GENERATE SEGMENTS, WING SPAN, WING AREA ~~~~~~~~~~~~~~~~~~~~~~ #

        self.area = 0.0
        self.span = 0.0

        for segment_uid, segment in self.segment.items():
            logger.debug(f"Generating segment '{segment_uid}'...")

            # CHECK DATA and generate VERTICES, GEOMETRY, AREA
            segment.generate()

            self.span += abs(segment.geometry['span'])
            self.area += segment.area

        # 2. CALCULATE SEGMENT POSITIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        segments = list(self.segment.values())
        pos = 0.0

        for segment in segments:
            segment.position['inner'] = pos/self.span
            pos += segment.geometry['span']
            segment.position['outer'] = pos/self.span

        # 3. CHECK WING CONTINUITY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        wing_continuous = True

        for i in range(len(segments) - 1):
            # segment edge directions
            segm_1 = segments[i]
            segm_2 = segments[i + 1]

            a1d1 = abs(segm_1.vertices['d'] - segm_1.vertices['a'])
            a1d1 = a1d1/np.linalg.norm(a1d1)

            b1c1 = abs(segm_1.vertices['c'] - segm_1.vertices['b'])
            b1c1 = b1c1/np.linalg.norm(b1c1)

            a2d2 = abs(segm_2.vertices['d'] - segm_2.vertices['a'])
            a2d2 = a2d2/np.linalg.norm(a2d2)

            b2c2 = abs(segm_2.vertices['c'] - segm_2.vertices['b'])
            b2c2 = b2c2/np.linalg.norm(b2c2)

            # cross-segment vertex-to-vertex directions
            a1c2 = abs(segm_2.vertices['c'] - segm_1.vertices['a'])
            a1c2 = a1c2/np.linalg.norm(a1c2) if np.linalg.norm(a1c2) else np.zeros(3)

            d1c2 = abs(segm_2.vertices['c'] - segm_1.vertices['d'])
            d1c2 = d1c2/np.linalg.norm(d1c2) if np.linalg.norm(d1c2) else np.zeros(3)

            b1d2 = abs(segm_2.vertices['d'] - segm_1.vertices['b'])
            b1d2 = b1d2/np.linalg.norm(b1d2) if np.linalg.norm(b1d2) else np.zeros(3)

            c1d2 = abs(segm_2.vertices['d'] - segm_1.vertices['c'])
            c1d2 = c1d2/np.linalg.norm(c1d2) if np.linalg.norm(c1d2) else np.zeros(3)

            b1c2 = abs(segm_2.vertices['c'] - segm_1.vertices['b'])
            b1c2 = b1c2/np.linalg.norm(b1c2) if np.linalg.norm(b1c2) else np.zeros(3)

            c1c2 = abs(segm_2.vertices['c'] - segm_1.vertices['c'])
            c1c2 = c1c2/np.linalg.norm(c1c2) if np.linalg.norm(c1c2) else np.zeros(3)

            a1d2 = abs(segm_2.vertices['d'] - segm_1.vertices['a'])
            a1d2 = a1d2/np.linalg.norm(a1d2) if np.linalg.norm(a1d2) else np.zeros(3)

            d1d2 = abs(segm_2.vertices['d'] - segm_1.vertices['d'])
            d1d2 = d1d2/np.linalg.norm(d1d2) if np.linalg.norm(d1d2) else np.zeros(3)

            segm_continuous = False

            if np.linalg.norm(a2d2 - b1c1) < TOL:
                # B1C1 and A2D2 have same orientation
                if np.linalg.norm(a2d2 - b1d2) < TOL or np.linalg.norm(a2d2 - c1d2) < TOL:
                    # B1C1 and A2D2 collinear

                    # if not np.linalg.norm(b1d2) + np.linalg.norm(c1d2) > np.linalg.norm(b1c1):
                    #     #   B1C1 overlaps A2D2

                    segm_continuous = True
                    logger.debug("edge {}-{} is continous (root-to-tip).".format(i, i + 1))

            elif np.linalg.norm(b2c2 - a1d1) < TOL:
                # A1D1 and B2C2 have same orientation
                if np.linalg.norm(b2c2 - a1c2) < TOL or np.linalg.norm(b2c2 - d1c2) < TOL:
                    # A1D1 and B2C2 collinear

                    # if not np.linalg.norm(a1c2) + np.linalg.norm(d1c2) > np.linalg.norm(a1d1):
                    #     #   A1D1 overlaps B2C2

                    segm_continuous = True
                    logger.debug("edge {}-{} is continous (tip-to-root).".format(i, i + 1))

            elif np.linalg.norm(b2c2 - b1c1) < TOL:
                # B1C1 and B2C2 have same orientation
                if np.linalg.norm(b2c2 - b1c2) < TOL or np.linalg.norm(b2c2 - c1c2) < TOL:
                    # B1C1 and B2C2 collinear

                    # if not np.linalg.norm(b1c2) + linalg.norm(c1c2) > np.linalg.norm(b1c1):
                    #     #   B1C1 overlaps B2C2

                    segm_continuous = True
                    logger.debug("edge {}-{} is continous (with discontinuous normal!).".format(i, i + 1))

            elif np.linalg.norm(a2d2 - a1d1) < TOL:
                # A1D1 and A2D2 have same orientation
                if np.linalg.norm(a2d2 - a1d2) < TOL or np.linalg.norm(a2d2 - d1d2) < TOL:
                    # A1D1 and A2D2 collinear

                    # if np.linalg.norm(a1d2) + np.linalg.norm(d1d2) > np.rm(d1d2) <= max_dist:
                    #     #   A1D1 overlaps A2D2

                    segm_continuous = True
                    logger.debug("edge {}-{} is continous (with discontinuous normal!).".format(i, i + 1))

            if not segm_continuous:
                logger.warning("edge {}-{} is discontinuous.".format(i, i + 1))

            wing_continuous &= segm_continuous

        if not wing_continuous:
            logger.warning("wing is discontinuous!")

        # TODO | improve continuity check, currently only collinearity

        self.state = True

    def check_deformation_continuity(self):
        """
        Check the continuity of the wing deformation.

        The deformation at the border of two neighbouring segments must be
        the same. Otherwise, there will be "gaps" in the wing which we will
        refuse to model.
        """

        logger.info("Checking continuity of wing deformation...")

        # Make a list of neighbouring segments of the wing
        segment_list = []
        for segment_uid, segment in self.segment.items():
            segment_list.append([segment_uid, segment])

        # Check that deformations at neighbouring segments are the same
        for i in range(0, len(segment_list)-1):
            segment_uid_inner, segment_inner = segment_list[i]
            segment_uid_outer, segment_outer = segment_list[i+1]

            for def_prop in ['ux', 'uy', 'uz', 'theta']:
                # NON-MIRRORED SIDE
                def_value_inner = segment_inner.deformation[def_prop](1.0)
                def_value_outer = segment_outer.deformation[def_prop](0.0)

                if def_value_inner != def_value_outer:
                    raise ComponentDefinitionError(
                            "Deformation ('{}') on non-mirrored wing is not continuous between segments ('{}', '{}')"
                            .format(def_prop, segment_uid_inner, segment_uid_outer))

                # MIRRORED SIDE
                def_value_inner = segment_inner.deformation_mirror[def_prop](1.0)
                def_value_outer = segment_outer.deformation_mirror[def_prop](0.0)

                if def_value_inner != def_value_outer:
                    raise ComponentDefinitionError(
                            "Deformation ('{}') on mirrored wing is not continuous between segments ('{}', '{}')"
                            .format(def_prop, segment_uid_inner, segment_uid_outer))


class WingSegment(FixedNamespace):
    """
    Data structure for WING component: WINGSEGMENT.

    WINGSEGMENT is a component of WING.
    Components are accessed using their unique identifier, must be a STRING.

    WINGSEGMENT represents a quadrilateral segment of lifting surface.

    Attributes:
        :area: (float) WINGSEGMENT surface area
        :position: (dict) WINGSEGMENT span-wise position in WING
        :vertices: (dict) WINGSEGMENT corner point coordinates
        :geometry: (dict) WINGSEGMENT geometric properties
        :airfoil: (dict) WINGSEGMENT wing section coordinates
        :panels: (dict) WINGSEGMENT discretization properties
        :state: (bool) WINGSEGMENT definition state
    """

    def __init__(self, wing, uid):
        """
        Initialise instance of WINGSEGMENT.

        WINGSEGMENT inherits from FIXEDNAMESPACE.
        Upon initialisation, attributes of WINGSEGMENT are created and fixed.
        Only existing attributes may be modified afterward.
        """

        super().__init__()

        self.parent_wing = wing
        self.uid = uid

        # DATA: calculated segment area
        self.area = None

        # DATA: calculated position in wing (span) and lattice (index)
        self.position = FixedOrderedDict()
        self.position['inner'] = None
        self.position['outer'] = None
        self.position['panel'] = None
        self.position._freeze()

        # PROPERTIES: provided or calculated segment area
        self.vertices = FixedOrderedDict()
        self.vertices['a'] = None
        self.vertices['b'] = None
        self.vertices['c'] = None
        self.vertices['d'] = None
        self.vertices._freeze()

        # PROPERTIES: provided or calculated segment properties
        self.geometry = FixedOrderedDict()
        self.geometry['inner_chord'] = None
        self.geometry['inner_alpha'] = None
        self.geometry['inner_beta'] = None
        self.geometry['inner_axis'] = None
        self.geometry['outer_chord'] = None
        self.geometry['outer_alpha'] = None
        self.geometry['outer_beta'] = None
        self.geometry['outer_axis'] = None
        self.geometry['span'] = None
        self.geometry['sweep'] = None
        self.geometry['dihedral'] = None
        self.geometry._freeze()

        # PROPERTIES: provided airfoil names
        self.airfoils = FixedOrderedDict()
        self.airfoils['inner'] = None
        self.airfoils['outer'] = None
        self.airfoils._freeze()

        # Derived
        self.segment_airfoil = None

        # PROPERTIES: provided discretisation settings
        self.panels = FixedOrderedDict()
        self.panels['num_c'] = None
        self.panels['num_s'] = None
        self.panels._freeze()

        # Deformed state of the segment
        self.deformation = None
        self.deformation_mirror = None

        # Subdivisions (by default always one "division")
        self.subdivision = OrderedDict()
        subdivision_rel_vertices = {}
        subdivision_rel_vertices['eta_a'] = 0.0
        subdivision_rel_vertices['eta_b'] = 1.0
        subdivision_rel_vertices['eta_c'] = 1.0
        subdivision_rel_vertices['eta_d'] = 0.0
        self.subdivision.update({0: WingSegmentSubdivision(self, subdivision_rel_vertices)})

        # state of component definition (see CHECK)
        self.state = False

        self._freeze()

    @property
    def normal_vector(self):
        """Segment normal vector (not normalised)"""

        a = self.vertices['a']
        b = self.vertices['b']
        d = self.vertices['d']

        ab = b - a
        ad = d - a

        return np.cross(ab, ad)

    @property
    def main_direction(self):
        """
        Direction of segment

        * Perpendicular to line AD (not normalised)
        * Points roughly from AD to BC
        """

        a = self.vertices['a']
        d = self.vertices['d']

        ad = d - a

        return np.cross(ad, self.normal_vector)

    @property
    def deformation_rot_axis(self):
        """
        Rotation axis for computation of deformed segments

        Note:
            * It is assumed that panels generally are oriented in global x-direction
        """

        m = self.main_direction
        dot_my = np.dot(m, Y_axis)
        dot_mz = np.dot(m, Z_axis)

        if dot_my > dot_mz:
            return Y_axis
        else:
            return Z_axis

    @property
    def symmetry(self):
        """Symmetry inherited from parent wing"""

        return self.parent_wing.symmetry

    def _import_airfoils(self):
        """
        Import airfoil data, and create a corresponding segment airfoil object

        The airfoils can be imported from:

            * x, y coordinates stored in a file
            * NACA4 definition
        """

        # Stores inner and outer airfoil object
        airfoil_dict = {}

        for position in ['inner', 'outer']:
            airfoil_definition = str(self.airfoils[position])

            import_from_file = False
            import_from_NACA = False

            if os.path.isfile(airfoil_definition):
                logger.info("Importing airfoil from file: '{:s}'".format(airfoil_definition))
                import_from_file = True
            elif airfoil_definition.upper().startswith('NACA'):
                airfoil_definition = airfoil_definition.upper()
                logger.info("Importing airfoil from NACA definition ({:s})".format(airfoil_definition))
                import_from_NACA = True
            else:
                raise ValueError("Airfoil input data neither a valid file " +
                                 f"nor NACA definition:\n{airfoil_definition}")

            if import_from_file:
                upper, lower = import_airfoil_data(airfoil_definition)
                airfoil_dict[position] = Airfoil(upper, lower)
            elif import_from_NACA:
                naca_digits = str(airfoil_definition).upper().strip('NACA')
                airfoil_dict[position] = Airfoil.NACA4(naca_digits)

        # Create a segment airfoil as a "morphable" airfoil
        self.segment_airfoil = MorphAirfoil(airfoil_dict['inner'], airfoil_dict['outer'])

    def add_subdivision(self, eta_a, eta_d, ignore_inval_eta=False):
        """
        Add a subdivision for the current segment.

        Note:
            * A new division will not be created if:
                * a division already exists at same position
                * a division line is very close to an existing division
            * In both cases the cases a handle to the already existing division
              will be returned.

        Args:
            :eta_a: (float) upper relative position of the division line
            :eta_d: (float) upper relative position of the division line
            :ignore_inval_eta: (bool) optional parameter to ignore invalid eta values

        Returns:
            :subvivision: (obj) newly created subdivision object
        """

        # Do not even try to proceed if eta is not within reasonable range
        if eta_a <= 0 or eta_a >= 1:
            logger.warning(f"Cannot add subdivision at eta = {eta_a:.1f}")

            if ignore_inval_eta:
                return None
            else:
                raise ValueError("eta must be in range (0, 1)")

        idx_new = len(self.subdivision)
        idx_prev, prev_subdivision, prev_is_on_border = self._get_subdiv_at_eta(eta_a)

        if prev_is_on_border:
            logger.debug(f"Refusing to create new division at existing division (eta_a = {eta_a:.3f})")
            return self.subdivision[idx_prev]

        if (eta_a - prev_subdivision.rel_vertices['eta_a']) < MIN_ETA_LIMIT:
            logger.debug("Refusing to create a subdivision close to existing division "
                         "(Delta eta_a = {:.3f})".format(eta_a - prev_subdivision.rel_vertices['eta_a']))
            return self.subdivision[idx_prev]

        # Relative vertices of new subdivision
        subdivision_rel_vertices = {}
        subdivision_rel_vertices['eta_a'] = eta_a
        subdivision_rel_vertices['eta_b'] = prev_subdivision.rel_vertices['eta_b']
        subdivision_rel_vertices['eta_c'] = prev_subdivision.rel_vertices['eta_c']
        subdivision_rel_vertices['eta_d'] = eta_d
        self.subdivision.update({idx_new: WingSegmentSubdivision(self, subdivision_rel_vertices)})

        eta_a_prev = prev_subdivision.rel_vertices['eta_a']
        eta_b_prev = prev_subdivision.rel_vertices['eta_b']

        # Update relative vertices of old subdivision
        prev_subdivision.rel_vertices['eta_b'] = eta_a
        prev_subdivision.rel_vertices['eta_c'] = eta_d

        # Inherit flap from previous subdivision
        if 'flap' in self.subdivision[idx_prev].subarea.keys():
            xsi1_prev = prev_subdivision.subarea['flap'].rel_vertices['xsi_a']
            xsi2_prev = prev_subdivision.subarea['flap'].rel_vertices['xsi_b']

            xsi_h1_prev = prev_subdivision.subarea['flap'].rel_hinge_vertices['xsi_h1']
            xsi_h2_prev = prev_subdivision.subarea['flap'].rel_hinge_vertices['xsi_h2']

            xsi_sdl = xsi_interpol(self.vertices, (eta_a_prev, xsi1_prev), (eta_b_prev, xsi2_prev), eta_a)
            xsi_h_sdl = xsi_interpol(self.vertices, (eta_a_prev, xsi_h1_prev), (eta_b_prev, xsi_h2_prev), eta_a)

            prev_sd_par_cntrl = prev_subdivision.subarea['flap'].parent_control
            self.subdivision[idx_new]._add_subarea(prev_sd_par_cntrl, xsi_sdl, xsi2_prev, xsi_h_sdl, xsi_h2_prev)
            prev_subdivision._update_subarea('flap', xsi1_prev, xsi_sdl, xsi_h1_prev, xsi_h_sdl)

        # Inherit slat from previous subdivision
        if 'slat' in self.subdivision[idx_prev].subarea.keys():
            xsi1_prev = prev_subdivision.subarea['slat'].rel_vertices['xsi_d']
            xsi2_prev = prev_subdivision.subarea['slat'].rel_vertices['xsi_c']

            xsi_h1_prev = prev_subdivision.subarea['slat'].rel_hinge_vertices['xsi_h1']
            xsi_h2_prev = prev_subdivision.subarea['slat'].rel_hinge_vertices['xsi_h2']

            xsi_sdl = xsi_interpol(self.vertices, (eta_a_prev, xsi1_prev), (eta_b_prev, xsi2_prev), eta_a)
            xsi_h_sdl = xsi_interpol(self.vertices, (eta_a_prev, xsi_h1_prev), (eta_b_prev, xsi_h2_prev), eta_a)

            prev_sd_par_cntrl = prev_subdivision.subarea['slat'].parent_control
            self.subdivision[idx_new]._add_subarea(prev_sd_par_cntrl, xsi_sdl, xsi2_prev, xsi_h_sdl, xsi_h2_prev)
            prev_subdivision._update_subarea('slat', xsi1_prev, xsi_sdl, xsi_h1_prev, xsi_h_sdl)

        return self.subdivision[idx_new]

    def _get_subdiv_at_eta(self, eta):
        """
        Get the subdivision and subdivision index at a specified eta position.

        Args:
            :eta: (float) eta position

        Returns:
            :idx: (int) subdivision index of subdivision object at eta position
            :subdivision: (obj) subdivision object at eta position
            :is_on_border: (bool) flag which indicates if eta is on edge of existing subdivision

        Note:
            * If 'is_on_border' is True, the subdivision with eta_a == eta is returned
        """

        for idx, subdivision in self.subdivision.items():
            if subdivision.rel_vertices['eta_a'] <= eta < subdivision.rel_vertices['eta_b']:
                if eta == subdivision.rel_vertices['eta_a']:
                    logger.debug("There is a subdivision line at requested position (eta = {:.3f})".format(eta))
                    return idx, subdivision, True
                else:
                    return idx, subdivision, False

    def _get_outer_neighbour_subdiv(self, eta_a):
        """
        Get the outer subdivision neighbour for a given eta_a.

        Returns:
            :outer_neighbour: (obj) outer neighbour or None if no neighbour found
        """

        # Account for numerical inaccuracies
        eta_a += MIN_ETA_LIMIT/10

        eta_diff_min = 1
        outer_neighbour = None

        for subdivision in self.subdivision.values():
            eta_diff = eta_a - subdivision.rel_vertices['eta_a']

            if eta_diff_min > eta_diff >= 0:
                eta_diff_min = eta_diff
                outer_neighbour = subdivision

        return outer_neighbour

    def add_subdivision_for_control(self, eta_a, eta_b, parent_control, xsi1, xsi2, xsi_h1=None, xsi_h2=None):
        """
        Add a subdivision for with a control device for a specified range.

        Args:
            :eta_a: (float) inner eta position of control surface
            :eta_b: (float) outer eta position of control surface
            :parent_control: (obj) reference to the parent control surface
            :xsi1: (float) inner xsi position of control surface
            :xsi2: (float) outer xsi position of control surface
            :xsi_h1: (float) [optional] inner position of the hinge line (=xsi1 if not specified)
            :xsi_h2: (float) [optional] outer position of the hinge line (=xsi2 if not specified)

        Returns:
            :sd_list: (obj-list) list of subdivision objects
        """

        if xsi_h1 is None:
            xsi_h1 = xsi1
            logger.warning("Hinge position xsi_h1 is not defined (assuming xsi1).")

        if xsi_h2 is None:
            xsi_h2 = xsi2
            logger.warning("Hinge position xsi_h2 is not defined (assuming xsi2).")

        # Add a first subdivision (sd1) beginning at eta_a
        if eta_a == 0:
            sd1 = self.subdivision[0]
        else:
            sd1 = self.add_subdivision(eta_a, eta_a)

        # Where does sd1 end? (i.e. what is the eta_b position?)
        eta_b_sd1 = sd1.rel_vertices['eta_b']

        # Make a list of subdivisions incl. inner and outer positions of the subareas
        sd_list = [[sd1, xsi1, xsi2, xsi_h1, xsi_h2]]

        # CASE 1: Newly created subdivisions ends exactly on desired line
        if eta_b == eta_b_sd1:
            pass

        # CASE 2: There is no more subdivisions before eta_b
        elif eta_b < eta_b_sd1:
            self.add_subdivision(eta_b, eta_b)

        # CASE 3: The newly created subdivision ends before desired line
        elif eta_b > eta_b_sd1:
            outer_neighbour = self._get_outer_neighbour_subdiv(eta_b_sd1)
            eta_b_rn = outer_neighbour.rel_vertices['eta_b']

            # Update inner and outer coordinates for subarea lines
            xsi_div = xsi_interpol(self.vertices, (eta_a, xsi1), (eta_b, xsi2), eta_b_sd1)
            xsi_h_div = xsi_interpol(self.vertices, (eta_a, xsi_h1), (eta_b, xsi_h2), eta_b_sd1)

            # xsi2 for the first subdivision must be updated
            sd_list[0][2] = xsi_div
            sd_list[0][4] = xsi_h_div

            # Assume the control for outer neighbour will span from xsi_div to xsi2
            sd_list.append([outer_neighbour, xsi_div, xsi2, xsi_h_div, xsi_h2])

            # If the outer neighbour cannot accommodate the control we have to continue
            n = 0
            while eta_b > eta_b_rn:
                outer_neighbour = self._get_outer_neighbour_subdiv(eta_b_rn)
                eta_b_rn = outer_neighbour.rel_vertices['eta_b']
                eta_b_ln = sd_list[-1][0].rel_vertices['eta_b']

                xsi_div = xsi_interpol(self.vertices, (eta_a, xsi1), (eta_b, xsi2), eta_b_ln)
                xsi_h_div = xsi_interpol(self.vertices, (eta_a, xsi_h1), (eta_b, xsi_h2), eta_b_ln)

                sd_list[-1][2] = xsi_div
                sd_list[-1][4] = xsi_h_div
                sd_list.append([outer_neighbour, xsi_div, xsi2, xsi_h_div, xsi_h2])

                n += 1
                if n > 1/MIN_ETA_LIMIT:
                    logger.error("Too many loops")
                    raise RuntimeError("Too many loops")

            # If the last outer neighbour is larger than required, make a subdivision
            if eta_b < outer_neighbour.rel_vertices['eta_b']:
                self.add_subdivision(eta_b, eta_b)

        # Add subarea for all subdivisions
        for row in sd_list:
            subdivision, xsi1, xsi2, xsi_h1, xsi_h2 = row
            subdivision._add_subarea(parent_control, xsi1, xsi2, xsi_h1, xsi_h2)

        return sd_list[:][0]

    def make_deformation_spline_interpolators(self):
        """
        Convert the discretised deformation to cubic spline interpolators.

        If the deformation for the mirrored side has not been set, it is
        assumed to be the same as on the "main" (non-mirrored) side.
        """

        eta = self.deformation['eta']
        ux = self.deformation['ux']
        uy = self.deformation['uy']
        uz = self.deformation['uz']
        theta = self.deformation['theta']

        # Make cubic spline interpolators
        self.deformation['ux'] = CubicSpline(eta, ux)
        self.deformation['uy'] = CubicSpline(eta, uy)
        self.deformation['uz'] = CubicSpline(eta, uz)
        self.deformation['theta'] = CubicSpline(eta, theta)

        if self.symmetry and self.deformation_mirror is None:
            logger.warning("Deformation of mirrored side is not defined. Using non-mirrored side.")
            self.deformation_mirror = self.deformation
        elif self.symmetry and self.deformation_mirror is not None:
            eta = self.deformation_mirror['eta']
            ux = self.deformation_mirror['ux']
            uy = self.deformation_mirror['uy']
            uz = self.deformation_mirror['uz']
            theta = self.deformation_mirror['theta']

            self.deformation_mirror['ux'] = CubicSpline(eta, ux)
            self.deformation_mirror['uy'] = CubicSpline(eta, uy)
            self.deformation_mirror['uz'] = CubicSpline(eta, uz)
            self.deformation_mirror['theta'] = CubicSpline(eta, theta)
        elif not self.symmetry and self.deformation_mirror is not None:
            raise ComponentDefinitionError("Deformation for mirrored side was defined, but wing has no symmetry.")

    def get_deformed_segment_point(self, eta, xsi, mirror=False):
        """
        Return a point of the deformed segment based on relative coordinates
        of the undeformed segment.

        Args:
            :eta: (float) eta coordinate
            :xsi: (float) xsi coordinate

        Returns:
            :point: segment point in the deformed mesh
        """

        # Deformations on the mirrored and non-mirrored wing can be different
        if mirror:
            deformation = self.deformation_mirror
        else:
            deformation = self.deformation

        ux = deformation['ux']
        uy = deformation['uy']
        uz = deformation['uz']
        theta = deformation['theta']

        a = self.vertices['a']
        b = self.vertices['b']
        c = self.vertices['c']
        d = self.vertices['d']

        p_upper = a + eta*(b - a)
        p_lower = d + eta*(c - d)

        # Vector from (u)pper to (l)ower side (on MAIN side)
        d_u2l = p_lower - p_upper
        d_u2l_rot = rotate_vector_around_axis(d_u2l, self.deformation_rot_axis, theta(eta))

        # First, mirror upper reference point accross the symmetry plane
        if mirror:
            p_upper = mirror_point(p_upper, self.symmetry)

        # Then, interpolate segment point with translation/rotation at p_upper
        point = p_upper + np.array([ux(eta), uy(eta), uz(eta)]) + xsi*d_u2l_rot
        return point

    def generate(self):
        """
        Compute WINGSEGMENT VERTICES, GEOMETRY, AREA from provided data.

        Procedure is as follows:
            * check if WINGSEGMENT properties are correctly defined.
            * check if WINGSEGMENT definition is complete.
            * generate WINGSEGMENT VERTICES, GEOMETRY, AREA if possible.

        Points are computed from geometric properties specified in GEOMETRY.
        At least one of A, B, C, D must be defined as reference point.

        Will compute corresponding properties in GEOMETRY given points A, D.
        Will compute corresponding properties in GEOMETRY given points B, C.
        Will compute all properties in GEOMETRY given points A, B, C, D.

        No other combination of properties and coordinates is accepted.

        Correct ordering of the vertices A, B, C, D is enforced:
            * A = (x_min, y_min, z_a) or A = (x_min, y_a, z_min) if vertical
            * B = (x_min, y_max, z_b) or B = (x_min, y_a, z_max) if vertical
            * C = (x_max, y_max, z_c) or C = (x_max, y_a, z_max) if vertical
            * D = (x_max, y_min, z_d) or D = (x_max, y_a, z_min) if vertical
        """

        # 1. CHECK SEGMENT PROPERTIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        self.check_vertices()
        self.check_geometry()
        self.check_airfoils()
        self.check_panels()

        # 2. CHECK PROVIDED GEOMETRIC PROPERTIES ~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        if all(v for v in self.geometry.values()):
            # all geometric properties provided
            required = ['a', 'b', 'c', 'd', 'ad', 'bc', 'abcd']

        elif all(v for k, v in self.geometry.items() if 'inner_' not in k):
            # all geometric properties provided except for inner edge
            required = ['ad', 'abcd']

        elif all(v for k, v in self.geometry.items() if 'outer_' not in k):
            # all geometric properties provided except for outer edge
            required = ['bc', 'abcd']

        elif any(v for v in self.geometry.values()):
            # some geometric properties provided, but not enough
            required = ['abcd']

        else:
            # no geometric properties provided
            required = ['abcd']

        # 3. CHECK PROVIDED VERTEX COORDINATES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # string of keys of correctly-defined vertices
        provided = ''.join(sorted(k for k, v in self.vertices.items() if v is not None))

        if not provided:
            raise ComponentDefinitionError("no reference point provided.")

        if provided not in ['a', 'b', 'c', 'd', 'ad', 'bc', 'abcd']:
            raise ComponentDefinitionError("unsupported segment definition.")

        logger.info("Reference points provided: {}".format(', '.join(c for c in provided)))
        for point in provided:
            logger.info(f"--> Point {point.upper()} = {self.vertices[point]}")

        # 4. CHECK COMPONENT DEFINITION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # provided inputs are insufficient to generate segment geometry
        if provided not in required:
            self.state = False
            raise ComponentDefinitionError("geometric properties of segment ill-defined.")

        # 5. GENERATE A, D-EDGE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        if not ('a' in provided and 'd' in provided):
            # generate edge A, D from provided properties

            logger.debug("Computing chord AD...")

            tan_ai = tan(radians(self.geometry['inner_alpha']))
            cos_bi = cos(radians(self.geometry['inner_beta']))
            sin_bi = sin(radians(self.geometry['inner_beta']))

            r_i = self.geometry['inner_chord']/sqrt(1.0 + tan_ai**2.0*cos_bi**2.0)

            a_x = +0.0
            a_y = +0.0
            a_z = +0.0
            # point A

            d_x = +r_i*cos_bi
            d_y = +r_i*sin_bi
            d_z = -r_i*cos_bi*tan_ai
            # point D relative to point A

        else:
            # compute properties of edge A, D from provided coordinates
            logger.debug("Computing properties of chord BC...")

            # point A
            a_x = +0.0
            a_y = +0.0
            a_z = +0.0

            # point D relative to point A
            d_x = self.vertices['d'][0] - self.vertices['a'][0]
            d_y = self.vertices['d'][1] - self.vertices['a'][1]
            d_z = self.vertices['d'][2] - self.vertices['a'][2]

            r_i = sqrt(d_x*d_x + d_y*d_y)

            self.geometry['inner_chord'] = sqrt(d_x*d_x + d_y*d_y + d_z*d_z)

            cos_bi = +d_x/r_i
            sin_bi = +d_y/r_i

            self.geometry['inner_beta'] = -degrees(asin(sin_bi))
            # atan2 handles singularity
            self.geometry['inner_alpha'] = -degrees(atan2(d_z, r_i*cos_bi))

            tan_ai = tan(radians(self.geometry['inner_alpha']))

            logger.debug("--> Inner_chord = {}.".format(self.geometry['inner_chord']))
            logger.debug("--> Inner_alpha = {}.".format(self.geometry['inner_alpha']))
            logger.debug("--> Inner_beta = {}.".format(self.geometry['inner_beta']))

        # 2. GENERATE B, C-EDGE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        if not ('a' in provided and 'b' in provided):
            # generate B, C from geometric properties

            logger.debug("Computing chord BC...")

            tan_ao = tan(radians(self.geometry['outer_alpha']))
            cos_bo = cos(radians(self.geometry['outer_beta']))
            sin_bo = sin(radians(self.geometry['outer_beta']))

            r_o = self.geometry['outer_chord']/sqrt(1.0 + tan_ao*tan_ao*cos_bo*cos_bo)

            # point B
            b_x = +0.0
            b_y = +0.0
            b_z = +0.0

            # point C relative to point B
            c_x = +r_o*cos_bo
            c_y = +r_o*sin_bo
            c_z = -r_o*cos_bo*tan_ao

        else:
            # compute properties of B, C-edge from provided coordinates
            logger.debug("Computing chord BC...")

            # point B
            b_x = +0.0
            b_y = +0.0
            b_z = +0.0

            # point C relative to point B
            c_x = self.vertices['c'][0] - self.vertices['b'][0]
            c_y = self.vertices['c'][1] - self.vertices['b'][1]
            c_z = self.vertices['c'][2] - self.vertices['b'][2]

            r_o = sqrt(c_x*c_x + c_y*c_y)

            self.geometry['outer_chord'] = sqrt(c_x*c_x + c_y*c_y + c_z*c_z)

            cos_bo = +c_x/r_o
            sin_bo = +c_y/r_o

            # atan2 handles singularity
            self.geometry['outer_beta'] = -degrees(asin(sin_bo))
            self.geometry['outer_alpha'] = -degrees(atan2(c_z, r_o*cos_bo))

            tan_ao = tan(radians(self.geometry['outer_alpha']))

            logger.debug("--> Outer_chord = {}.".format(self.geometry['outer_chord']))
            logger.debug("--> Outer_alpha = {}.".format(self.geometry['outer_alpha']))
            logger.debug("--> Outer_beta = {}.".format(self.geometry['outer_beta']))

        # 7. GENERATE EDGES A-B AND D-C ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # set default
        if self.geometry['inner_axis'] is None:
            self.geometry['inner_axis'] = 0.25
        if self.geometry['outer_axis'] is None:
            self.geometry['outer_axis'] = 0.25

        # axi_x = r_i*self.geometry['inner_axis']*cos_bi
        axi_y = r_i*self.geometry['inner_axis']*sin_bi
        axi_z = r_i*self.geometry['inner_axis']*cos_bi*tan_ai
        # offset of point A wrt axis point (dihedral line) on AD

        # axo_x = r_o*self.geometry['outer_axis']*cos_bo
        axo_y = r_o*self.geometry['outer_axis']*sin_bo
        axo_z = r_o*self.geometry['outer_axis']*cos_bo*tan_ao
        # offset of point B wrt axis point (dihedral line) on BC

        # relative y, z-offset between axis on B, C-edge and axis on A, B-edge
        axs_y = axo_y - axi_y
        axs_z = axo_z - axi_z

        logger.debug("--> Inner_axis = {}.".format(self.geometry['inner_axis']))
        logger.debug("--> Outer_axis = {}.".format(self.geometry['outer_axis']))

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        if provided == 'abcd':
            # compute spanwise properties from A, B, C, D

            logger.debug("Computing span-wise properties...")

            b_x = self.vertices['b'][0] - self.vertices['a'][0]
            b_y = self.vertices['b'][1] - self.vertices['a'][1]
            b_z = self.vertices['b'][2] - self.vertices['a'][2]

            c_x = self.vertices['b'][0] - self.vertices['a'][0]
            c_y = self.vertices['b'][1] - self.vertices['a'][1]
            c_z = self.vertices['b'][2] - self.vertices['a'][2]

            # span measured at leading edge
            self.geometry['span'] = sqrt(b_y*b_y + b_z*b_z)
            # sweep applied at leading edge
            self.geometry['sweep'] = degrees(atan2(b_x, self.geometry['span']))
            # dihedral applied along axis
            self.geometry['dihedral'] = degrees(atan2((b_z + axs_z), (b_y + axs_y)))

            logger.debug("--> Dihedral = {}".format(self.geometry['dihedral']))
            logger.debug("--> Sweep = {}".format(self.geometry['sweep']))
            logger.debug("--> Span = {}".format(self.geometry['span']))

        else:
            # position edge B-C wrt edge A-D
            logger.debug("Computing span-wise edges AB and CD...")

            cos_d = cos(radians(self.geometry['dihedral']))
            sin_d = sin(radians(self.geometry['dihedral']))
            tan_s = tan(radians(self.geometry['sweep']))

            # effective geometric dihedral of leading edge
            axr = axs_z*cos_d - axs_y*sin_d
            dihedral_ax = radians(self.geometry['dihedral']) - asin(axr/self.geometry['span'])

            b_x += self.geometry['span']*tan_s
            b_y += self.geometry['span']*cos(dihedral_ax)
            b_z += self.geometry['span']*sin(dihedral_ax)

            c_x += self.geometry['span']*tan_s
            c_y += self.geometry['span']*cos(dihedral_ax)
            c_z += self.geometry['span']*sin(dihedral_ax)

            # first point in user-provided points serves as reference
            point = provided[0]

            # used to set reference to [0.0, 0.0, 0.0] in relative coord
            adjust = {'a': [a_x, a_y, a_z],
                      'b': [b_x, b_y, b_z],
                      'c': [c_x, c_y, c_z],
                      'd': [d_x, d_y, d_z]}

            # translate [0.0, 0.0, 0.0] by absolute position of reference
            a_x += self.vertices[point][0] - adjust[point][0]
            a_y += self.vertices[point][1] - adjust[point][1]
            a_z += self.vertices[point][2] - adjust[point][2]

            b_x += self.vertices[point][0] - adjust[point][0]
            b_y += self.vertices[point][1] - adjust[point][1]
            b_z += self.vertices[point][2] - adjust[point][2]

            c_x += self.vertices[point][0] - adjust[point][0]
            c_y += self.vertices[point][1] - adjust[point][1]
            c_z += self.vertices[point][2] - adjust[point][2]

            d_x += self.vertices[point][0] - adjust[point][0]
            d_y += self.vertices[point][1] - adjust[point][1]
            d_z += self.vertices[point][2] - adjust[point][2]

            # invert span-wise orientation for negative span
            if self.geometry['span'] < 0:
                a_x, b_x, c_x, d_x = b_x, a_x, d_x, c_x
                a_y, b_y, c_y, d_y = b_y, a_y, d_y, c_y
                a_z, b_z, c_z, d_z = b_z, a_z, d_z, c_z

            # invert span-wise orientation for x < -90.0 or x > +90.0
            if abs(self.geometry['dihedral']) > 90.0:
                a_x, b_x, c_x, d_x = b_x, a_x, d_x, c_x
                a_y, b_y, c_y, d_y = b_y, a_y, d_y, c_y
                a_z, b_z, c_z, d_z = b_z, a_z, d_z, c_z

            # invert ib chord-wise orientation for negative ib chord
            if self.geometry['inner_chord'] < 0:
                a_x, b_x, c_x, d_x = d_x, b_x, c_x, a_x
                a_y, b_y, c_y, d_y = d_y, b_y, c_y, a_y
                a_z, b_z, c_z, d_z = d_z, b_z, c_z, a_z

            # invert ib chord-wise orientation for x < -90.0 or x > +90.0
            if abs(self.geometry['inner_alpha']) > 90.0:
                a_x, b_x, c_x, d_x = d_x, b_x, c_x, a_x
                a_y, b_y, c_y, d_y = d_y, b_y, c_y, a_y
                a_z, b_z, c_z, d_z = d_z, b_z, c_z, a_z

            # invert ib chord-wise orientation for x < -90.0 or x > +90.0
            if abs(self.geometry['inner_beta']) > 90.0:
                a_x, b_x, c_x, d_x = d_x, b_x, c_x, a_x
                a_y, b_y, c_y, d_y = d_y, b_y, c_y, a_y
                a_z, b_z, c_z, d_z = d_z, b_z, c_z, a_z

            # invert ob chord-wise orientation for negative ob chord
            if self.geometry['outer_chord'] < 0:
                a_x, b_x, c_x, d_x = a_x, c_x, b_x, d_x
                a_y, b_y, c_y, d_y = a_y, c_y, b_y, d_y
                a_z, b_z, c_z, d_z = a_z, c_z, b_z, d_z

            # invert ob chord-wise orientation for x < -90.0 or x > +90.0
            if abs(self.geometry['outer_alpha']) > 90.0:
                a_x, b_x, c_x, d_x = a_x, c_x, b_x, d_x
                a_y, b_y, c_y, d_y = a_y, c_y, b_y, d_y
                a_z, b_z, c_z, d_z = a_z, c_z, b_z, d_z

            # invert ob chord-wise orientation for x < -90.0 or x > +90.0
            if abs(self.geometry['outer_beta']) > 90.0:
                a_x, b_x, c_x, d_x = a_x, c_x, b_x, d_x
                a_y, b_y, c_y, d_y = a_y, c_y, b_y, d_y
                a_z, b_z, c_z, d_z = a_z, c_z, b_z, d_z

            self.vertices['a'] = [a_x, a_y, a_z]
            self.vertices['b'] = [b_x, b_y, b_z]
            self.vertices['c'] = [c_x, c_y, c_z]
            self.vertices['d'] = [d_x, d_y, d_z]

        # 8. GENERATE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        logger.debug(f"--> Vertex a = {self.vertices['a']}.")
        logger.debug(f"--> Vertex b = {self.vertices['b']}.")
        logger.debug(f"--> Vertex c = {self.vertices['c']}.")
        logger.debug(f"--> Vertex d = {self.vertices['d']}.")

        self.area = 0.5*self.geometry['span']*(self.geometry['inner_chord'] + self.geometry['outer_chord'])

        # Generate airfoil object
        self._import_airfoils()

        self.state = True

    def check_vertices(self):
        """Check type and value of properties in WINGSEGMENT.VERTICES."""

        logger.info("Checking vertex coordinates...")

        # 1. CHECK DEFINITION OF VERTICES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        for key, val in self.vertices.items():

            if val is None:
                logger.info("Vertex '{}' is NONE (not defined).".format(key))

            elif isinstance(val, (list, np.ndarray)) and len(val) == 3:

                if not isinstance(val[0], (float, int)):
                    raise TypeError("x-coordinate of vertex '{}' must be FLOAT.".format(key))
                if not isinstance(val[1], (float, int)):
                    raise TypeError("y-coordinate of vertex '{}' must be FLOAT.".format(key))
                if not isinstance(val[2], (float, int)):
                    raise TypeError("z-coordinate of vertex '{}' must be FLOAT.".format(key))

                # convert to NUMPY array
                self.vertices[key] = np.array(val, dtype=float, order='C')

            else:
                raise TypeError("vertex '{}' must be ARRAY of FLOAT [X, Y, Z].".format(key))

    def check_geometry(self):
        """Check type and value of properties in WINGSEGMENT.GEOMETRY."""

        logger.info("Checking geometric properties...")

        # 1. CHECK DEFINITION OF GEOMETRIC PROPERTIES ~~~~~~~~~~~~~~~~~~~~~ #

        # inner chord
        if self.geometry['inner_chord'] is None:
            logger.info("'inner_chord' is NONE (not defined).")
        elif not isinstance(self.geometry['inner_chord'], (float, int)):
            raise TypeError("'inner_chord' must be FLOAT.")
        else:
            self.geometry['inner_chord'] = float(self.geometry['inner_chord'])

        # outer chord
        if self.geometry['outer_chord'] is None:
            logger.info("'outer_chord is NONE (not defined).")
        elif not isinstance(self.geometry['outer_chord'], (float, int)):
            raise TypeError("'outer_chord' must be FLOAT.")
        else:
            self.geometry['outer_chord'] = float(self.geometry['outer_chord'])

        # inner alpha
        if self.geometry['inner_alpha'] is None:
            logger.info("'inner_alpha' is NONE (not defined).")
        elif not isinstance(self.geometry['inner_alpha'], (float, int)):
            raise TypeError("'inner_alpha' must be FLOAT.")
        elif not -90.0 <= self.geometry['inner_alpha'] <= +90.0:
            raise ValueError("'inner_alpha' must be between -90.0 and +90.0 [deg].")
        else:
            self.geometry['inner_alpha'] = float(self.geometry['inner_alpha'])

        # outer alpha
        if self.geometry['outer_alpha'] is None:
            logger.info("'outer_alpha' is NONE (not defined).")
        elif not isinstance(self.geometry['outer_alpha'], (float, int)):
            raise TypeError("'outer_alpha' must be FLOAT.")
        elif not -90.0 <= self.geometry['outer_alpha'] <= +90.0:
            raise ValueError("'outer_alpha' must be between -90.0 and +90.0 [deg].")
        else:
            self.geometry['outer_alpha'] = float(self.geometry['outer_alpha'])

        # inner beta
        if self.geometry['inner_beta'] is None:
            logger.info("'inner_beta' is NONE (not defined).")
        elif not isinstance(self.geometry['inner_beta'], (float, int)):
            raise TypeError("'inner_beta' must be FLOAT.")
        elif not -90.0 <= self.geometry['inner_beta'] <= +90.0:
            raise ValueError("'inner_beta' must be between -90.0 and +90.0 [deg].")
        else:
            self.geometry['inner_beta'] = float(self.geometry['inner_beta'])

        # outer beta
        if self.geometry['outer_beta'] is None:
            logger.info("'outer_beta' is NONE (not defined).")
        elif not isinstance(self.geometry['outer_beta'], (float, int)):
            raise TypeError("'outer_beta' must be FLOAT.")
        elif not -90.0 <= self.geometry['outer_beta'] <= +90.0:
            raise ValueError("'outer_beta' must be between -90.0 and +90.0 [deg].")
        else:
            self.geometry['outer_beta'] = float(self.geometry['outer_beta'])

        # inner axis
        if self.geometry['inner_axis'] is None:
            self.geometry['inner_axis'] = 0.25
        elif not isinstance(self.geometry['inner_axis'], (float, int)):
            raise TypeError("'inner_axis' must be FLOAT.")
        elif not +0.0 <= self.geometry['inner_axis'] <= +1.0:
            raise ValueError("'inner_axis' must be between +0.0 and +1.0 [chord fraction].")
        else:
            self.geometry['inner_axis'] = float(self.geometry['inner_axis'])

        # outer axis
        if self.geometry['outer_axis'] is None:
            self.geometry['outer_axis'] = 0.25
        elif not isinstance(self.geometry['outer_axis'], (float, int)):
            raise TypeError("'outer_axis' must be FLOAT.")
        elif not +0.0 <= self.geometry['outer_axis'] <= +1.0:
            raise ValueError("'outer_axis' must be between +0.0 and +1.0 [chord fraction].")
        else:
            self.geometry['outer_axis'] = float(self.geometry['outer_axis'])

        # span
        if self.geometry['span'] is None:
            logger.info("'span' is NONE (not defined).")
        elif not isinstance(self.geometry['span'], (float, int)):
            raise TypeError("'span' must be FLOAT.")
        else:
            self.geometry['span'] = float(self.geometry['span'])

        # sweep
        if self.geometry['sweep'] is None:
            logger.info("'sweep' is NONE (not defined).")
        elif not isinstance(self.geometry['sweep'], (float, int)):
            raise TypeError("'sweep' must be FLOAT.")
        elif not -90.0 < self.geometry['sweep'] < +90.0:
            raise ValueError("'sweep' must be between -90.0 and +90.0 [deg].")
        else:
            self.geometry['sweep'] = float(self.geometry['sweep'])

        # dihedral
        if self.geometry['dihedral'] is None:
            logger.info("'dihedral' is NONE (not defined).")
        elif not isinstance(self.geometry['dihedral'], (float, int)):
            raise TypeError("'dihedral' must be FLOAT.")
        elif not -180.0 < self.geometry['dihedral'] <= +180.0:
            raise ValueError("'dihedral' must be between -180.0 and +180.0 [deg].")
        else:
            self.geometry['dihedral'] = float(self.geometry['dihedral'])

    def check_airfoils(self):
        """Check type and value of properties in WINGSEGMENT.AIRFOILS."""

        logger.info("Checking airfoil properties...")

        # inner foil
        if self.airfoils['inner'] is None:
            raise ComponentDefinitionError("inner wing profile is not defined.")
        elif not isinstance(self.airfoils['inner'], str):
            raise TypeError("'airfoil.inner' must be FILENAME.")

        # outer foil
        if self.airfoils['outer'] is None:
            raise ComponentDefinitionError("outer wing profile is not defined.")
        elif not isinstance(self.airfoils['outer'], str):
            raise TypeError("'airfoil.outer' must be FILENAME.")

    def check_panels(self):
        """Check type and value of properties in WINGSEGMENT.PANELS."""

        logger.info("Checking discretisation properties...")

        for panel_number in ['num_c', 'num_s']:
            if self.panels[panel_number] is None:
                logger.debug(f"'{panel_number}' is None (not defined)")
            elif not isinstance(self.panels[panel_number], int):
                raise TypeError(f"'{panel_number}' must be positive integer")
            elif not self.panels[panel_number] > 0:
                raise ValueError(f"{panel_number} must be positive")

############################################################
############################################################
############################################################
# ==> DEPRECATED METHOD
    # def get_point(self, coord_s, coord_c):
    #     """
    #     Returns X, Y, Z of point at local coordinates S, C.

    #     Args:
    #         :coord_s: (float) span- wise fraction of the quadrilateral
    #         :coord_c: (float) chord-wise fraction of the quadrilateral

    #     Returns:
    #         :point: (numpy) X, Y, Z-coordinates of point
    #     """

    #     if any(v for v in self.vertices.values() if v is None):
    #         raise ComponentDefinitionError("method 'get_point' requires vertices A, B, C, D.")

    #     alfa1 = self.vertices['a'][0]
    #     alfa2 = self.vertices['b'][0] - self.vertices['a'][0]
    #     alfa3 = self.vertices['d'][0] - self.vertices['a'][0]
    #     alfa4 = self.vertices['a'][0] - self.vertices['b'][0] + self.vertices['c'][0] - self.vertices['d'][0]

    #     beta1 = self.vertices['a'][1]
    #     beta2 = self.vertices['b'][1] - self.vertices['a'][1]
    #     beta3 = self.vertices['d'][1] - self.vertices['a'][1]
    #     beta4 = self.vertices['a'][1] - self.vertices['b'][1] + self.vertices['c'][1] - self.vertices['d'][1]

    #     gama1 = self.vertices['a'][2]
    #     gama2 = self.vertices['b'][2] - self.vertices['a'][2]
    #     gama3 = self.vertices['d'][2] - self.vertices['a'][2]
    #     gama4 = self.vertices['a'][2] - self.vertices['b'][2] + self.vertices['c'][2] - self.vertices['d'][2]

    #     x = alfa1 + alfa2*coord_s + alfa3*coord_c + alfa4*coord_s*coord_c
    #     y = beta1 + beta2*coord_s + beta3*coord_c + beta4*coord_s*coord_c
    #     z = gama1 + gama2*coord_s + gama3*coord_c + gama4*coord_s*coord_c

    #     return np.array([x, y, z])
############################################################
############################################################
############################################################


class WingControl(FixedNamespace):
    """
    Data structure for WING component: WINGCONTROL.

    WINGCONTROL is a component of WING.
    Components are accessed using their unique identifier, must be a STRING.

    WINGCONTROL represents a quadrilateral control device.

    WINGCONTROL does not have a GENERATE() method.
    VERTICES are calculated in the GENERATE() method of WING.

    Attributes:
        :device: (string) WINGCONTROL device type
        :deflection: (float) WINGCONTROL deflection angle
        :vertices: (dict) WINGCONTROL vertex coordinates
        :geometry: (dict) WINGCONTROL geometric properties
        :state: (bool) WINGCONTROL definition state
    """

    def __init__(self, parent_wing, control_uid):
        """
        Initialise instance of WINGCONTROL.

        Upon initialisation, attributes of WINGCONTROL are created and fixed.
        Only existing attributes may be modified afterward.
        """

        super().__init__()

        self.parent_wing = parent_wing
        self.uid = control_uid

        self.device_type = None
        self.deflection = None
        self.deflection_mirror = None

        # Name of the section on which the inner and outer part of the control section lies on
        self.segment_uid = FixedOrderedDict()
        self.segment_uid['inner'] = None
        self.segment_uid['outer'] = None
        self.segment_uid._freeze()

        self.rel_vertices = FixedOrderedDict()
        self.rel_vertices['eta_inner'] = None
        self.rel_vertices['eta_outer'] = None
        self.rel_vertices['xsi_inner'] = None
        self.rel_vertices['xsi_outer'] = None
        self.rel_vertices._freeze()

        self.rel_hinge_vertices = FixedOrderedDict()
        self.rel_hinge_vertices['xsi_inner'] = None
        self.rel_hinge_vertices['xsi_outer'] = None
        self.rel_hinge_vertices._freeze()

        # PROPERTIES -- provided relative position of hinge ends
        self.panels = FixedOrderedDict()
        self.panels['num_c'] = None
        self.panels._freeze()

        # component definition state
        self.state = False
        self._freeze()

    @property
    def symmetry(self):
        """Symmetry inherited from parent wing"""

        return self.parent_wing.symmetry

    @property
    def abs_vertices(self):
        """Get absolute coordinates of the control"""

        inner_seg_name = self.segment_uid['inner']
        outer_seg_name = self.segment_uid['outer']
        inner_seg_vertices = self.parent_wing.segment[inner_seg_name].vertices
        outer_seg_vertices = self.parent_wing.segment[outer_seg_name].vertices

        eta_inner = self.rel_vertices['eta_inner']
        xsi_inner = self.rel_vertices['xsi_inner']
        eta_outer = self.rel_vertices['eta_outer']
        xsi_outer = self.rel_vertices['xsi_outer']

        if self.device_type == 'flap':
            a_abs = get_abs_segment_point_coords(inner_seg_vertices, eta_inner, xsi_inner)
            b_abs = get_abs_segment_point_coords(outer_seg_vertices, eta_outer, xsi_outer)
            c_abs = get_abs_segment_point_coords(outer_seg_vertices, eta_outer, 1)
            d_abs = get_abs_segment_point_coords(inner_seg_vertices, eta_inner, 1)

        elif self.device_type == 'slat':
            a_abs = get_abs_segment_point_coords(inner_seg_vertices, eta_inner, 0)
            b_abs = get_abs_segment_point_coords(outer_seg_vertices, eta_outer, 0)
            c_abs = get_abs_segment_point_coords(outer_seg_vertices, eta_outer, xsi_outer)
            d_abs = get_abs_segment_point_coords(inner_seg_vertices, eta_inner, xsi_inner)

        return {'a': a_abs, 'b': b_abs, 'c': c_abs, 'd': d_abs}

    @property
    def abs_hinge_vertices(self):
        """Get absolute hinge coordinates of the control"""

        inner_seg_name = self.segment_uid['inner']
        outer_seg_name = self.segment_uid['outer']
        inner_seg_vertices = self.parent_wing.segment[inner_seg_name].vertices
        outer_seg_vertices = self.parent_wing.segment[outer_seg_name].vertices

        eta_inner = self.rel_vertices['eta_inner']
        eta_outer = self.rel_vertices['eta_outer']
        xsi_inner = self.rel_hinge_vertices['xsi_inner']
        xsi_outer = self.rel_hinge_vertices['xsi_outer']

        p1 = get_abs_segment_point_coords(inner_seg_vertices, eta_inner, xsi_inner)
        p2 = get_abs_segment_point_coords(outer_seg_vertices, eta_outer, xsi_outer)

        return {'p_inner': p1, 'p_outer': p2}

    def check(self):
        """Check definition of WINGCONTROL properties and data"""

        logger.info("Checking geometric properties...")

        # NOTE: segment name is checked at segment level

        # CHECK DEVICE TYPE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        if self.device_type is None:
            raise ComponentDefinitionError("'device' is not defined.")
        elif not isinstance(self.device_type, str):
            raise TypeError("'device' must be STRING.")
        elif self.device_type not in ['slat', 'flap']:
            raise ValueError("'device' must be 'slat' or 'flap'.")

        # CHECK GEOMETRY PROPERTIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        for rel_coord in self.rel_vertices.values():
            if not isinstance(rel_coord, (float, int)):
                raise TypeError("Values in 'rel_vertices' must be in of type 'float' or 'int'")
            elif 0 < rel_coord > 1:
                raise ValueError("Values in 'rel_vertices' must be in range [0, 1].")

        if (self.segment_uid['inner'] == self.segment_uid['outer']) and \
                (self.rel_vertices['eta_outer'] <= self.rel_vertices['eta_inner']):
            raise ValueError("'eta_outer' must be greater than 'eta_inner'")

        for rel_coord in self.rel_hinge_vertices.values():
            if not isinstance(rel_coord, (float, int)):
                raise TypeError("Values in 'rel_hinge_vertices' must be in of type 'float' or 'int'")
            elif 0 < rel_coord > 1:
                raise ValueError("Values in 'rel_hinge_vertices' must be in range [0, 1].")

        # CHECK DEFLECTION ANGLE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        if self.deflection is None:
            raise ComponentDefinitionError("'deflection' is not defined.")
        elif not isinstance(self.deflection, (float, int)):
            raise TypeError("'deflection' must be FLOAT.")
        elif not -90.0 <= self.deflection <= +90.0:
            raise ValueError("'deflection' must be between -90.0 and +90.0 [deg].")
        else:
            self.deflection = float(self.deflection)

        if self.deflection_mirror is None:
            if self.symmetry != 0:
                logger.warning(f"Control '{self.uid:s}': 'deflection_mirror' is not set, " +
                               "but wing has symmetry. Will use 'deflection'")
                self.deflection_mirror = self.deflection
        elif self.symmetry == 0:
            logger.warning(f"Control '{self.uid:s}': 'deflection_mirror' is set, " +
                           "but wing has no symmetry. Value will be ignored.")
        elif not isinstance(self.deflection_mirror, (float, int)):
            raise TypeError("'deflection' must be FLOAT.")
        elif not -90.0 <= self.deflection_mirror <= +90.0:
            raise ValueError("'deflection' must be between -90.0 and +90.0 [deg].")
        else:
            self.deflection_mirror = float(self.deflection_mirror)

        # CHECK PANEL PROPERTIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        if self.panels['num_c'] is None:
            logger.debug("'num_c' is None (not defined)")
        elif not isinstance(self.panels['num_c'], int):
            raise TypeError("'num_c' must be positive integer")
        elif not self.panels['num_c'] > 0:
            raise ValueError("'num_c' must be positive")


class WingSegmentSubdivision(FixedNamespace):
    """
    WingSegmentSubdivision is a "child class" of WingSegment.

    This object further divides each WingSegment into chordwise strips. This
    simplifies the meshing of the wing surface when there are leading and
    trailing edge devices. Subdivisions can also be geometrically transformed
    (translation and rotation). This makes it possible to perform a analyses on
    a deformed surface mesh, which is of particular interest for aeroelastic
    analyses.

    WingSegmentSubdivision are quadrilateral segments.

    Attributes:
        :segment: (obj) reference to the parent segment object
        :rel_vertices: (dict) relative coordinates of the subdivision defined by eta coordinates
        :subarea: (dict) dictionary containing subareas of a subdivision
    """

    def __init__(self, segment, rel_vertices):
        """
        Initialisation of the WingSegmentSubdivision

        Args:
            :segment: (obj) parent object (segment)
            :rel_vertices: (dict) relative coordinates of the subdivision (eta)
        """

        super().__init__()

        # Keep a reference about the parents outer vertices
        self.parent_segment = segment
        self.parent_wing = self.parent_segment.parent_wing

        # Relative vertices of the subdivision (w.r.t. segment)
        self.rel_vertices = FixedOrderedDict()
        self.rel_vertices['eta_a'] = rel_vertices['eta_a']
        self.rel_vertices['eta_b'] = rel_vertices['eta_b']
        self.rel_vertices['eta_c'] = rel_vertices['eta_c']
        self.rel_vertices['eta_d'] = rel_vertices['eta_d']
        self.rel_vertices._freeze()

        # Subareas (by default always a 'segment' subarea)
        self.subarea = OrderedDict()
        subarea_segment_rel_vertices = {}
        subarea_segment_rel_vertices['xsi_a'] = 0.0
        subarea_segment_rel_vertices['xsi_b'] = 0.0
        subarea_segment_rel_vertices['xsi_c'] = 1.0
        subarea_segment_rel_vertices['xsi_d'] = 1.0
        self.subarea.update({'segment': WingSegmentSubdivisionSubarea(self,
                            subarea_segment_rel_vertices, subarea_type='segment')})

        self._freeze()

    @property
    def symmetry(self):
        """Symmetry inherited from parent wing"""

        return self.parent_wing.symmetry

    def abs_vertices(self, mirror):
        """
        Get absolute coordinates of the subdivision.

        Absolute coordinates are only computed upon request based on the parent
        geometry (segment) and transformation directives if defined.

        Wing deformations are taken into account.

        Args:
            :mirror: (bool) flag to whether to return the mirrored or non-mirrored side

        Returns:
            :abs_vertices: (dict) absolute subdivision vertices
        """

        if self.parent_wing.is_deformed:
            eta_a = self.rel_vertices['eta_a']
            eta_b = self.rel_vertices['eta_b']
            eta_c = self.rel_vertices['eta_c']
            eta_d = self.rel_vertices['eta_d']

            a_abs = self.parent_segment.get_deformed_segment_point(eta_a, 0, mirror)
            b_abs = self.parent_segment.get_deformed_segment_point(eta_b, 0, mirror)
            c_abs = self.parent_segment.get_deformed_segment_point(eta_c, 1, mirror)
            d_abs = self.parent_segment.get_deformed_segment_point(eta_d, 1, mirror)

            if mirror:
                a_abs, b_abs, c_abs, d_abs = order_mirrored_vertex_points((a_abs, b_abs, c_abs, d_abs), self.symmetry)
        else:
            a = self.parent_segment.vertices['a']
            b = self.parent_segment.vertices['b']
            c = self.parent_segment.vertices['c']
            d = self.parent_segment.vertices['d']

            eta_a = self.rel_vertices['eta_a']
            eta_b = self.rel_vertices['eta_b']
            eta_c = self.rel_vertices['eta_c']
            eta_d = self.rel_vertices['eta_d']

            a_abs = a + eta_a*(b - a)
            b_abs = a + eta_b*(b - a)
            c_abs = d + eta_c*(c - d)
            d_abs = d + eta_d*(c - d)

            if mirror:
                a_abs, b_abs, c_abs, d_abs = mirror_vertices((a_abs, b_abs, c_abs, d_abs), self.symmetry)

        return {'a': a_abs, 'b': b_abs, 'c': c_abs, 'd': d_abs}

    def _add_subarea(self, parent_control, xsi1, xsi2, xsi_h1=None, xsi_h2=None):
        """
        Add a subarea to the current subdivision (intended for internal use only).

        Note:
            * If a subarea is added, the 'segment' subarea is updated
              automatically. The 'segment' subarea should NOT be modified manually.

        Args:
            :parent_control: (obj) reference to the parent control object
            :xsi1: (float) inner xsi position of the area division
            :xsi2: (float) outer xsi position of the area division
            :xsi_h1: (float) [optional] inner position of the hinge line (=xsi1 if not specified)
            :xsi_h2: (float) [optional] outer position of the hinge line (=xsi2 if not specified)

        Returns:
            :subarea: newly created subarea object
        """

        device_type = parent_control.device_type

        if device_type not in ['slat', 'flap']:
            raise ValueError("Unknown device type {:s}".format(str(device_type)))

        if device_type in self.subarea.keys():
            raise ValueError("Subdivision already has subarea for type {:s}".format(device_type))

        if xsi_h1 is None:
            xsi_h1 = xsi1
            logger.warning("Hinge position xsi_h1 is not defined (assuming xsi1).")

        if xsi_h2 is None:
            xsi_h2 = xsi2
            logger.warning("Hinge position xsi_h2 is not defined (assuming xsi2).")

        for xsi in [xsi2, xsi1]:
            if (xsi <= 0 or xsi >= 1):
                raise ValueError("xsi must be in range (0, 1). Given xsi = {:.2e}".format(xsi))

        for xsi in [xsi_h1, xsi_h2]:
            if (xsi < 0 or xsi > 1):
                raise ValueError("xsi_h must be in range [0, 1]. Given xsi = {:.2e}".format(xsi))

        if 'slat' in self.subarea.keys():
            if self.subarea['slat'].rel_vertices['xsi_d'] + MIN_XSI_LIMIT > xsi1 \
                    or self.subarea['slat'].rel_vertices['xsi_c'] + MIN_XSI_LIMIT > xsi2:
                raise ValueError("Refusing to create overlapping subareas")

        if 'flap' in self.subarea.keys():
            if xsi1 + MIN_XSI_LIMIT > self.subarea['flap'].rel_vertices['xsi_a']  \
                    or xsi2 + MIN_XSI_LIMIT > self.subarea['flap'].rel_vertices['xsi_b']:
                raise ValueError("Refusing to create overlapping subareas")

        if device_type == 'slat':
            subarea_segment_rel_vertices = {}
            subarea_segment_rel_vertices['xsi_a'] = 0.0
            subarea_segment_rel_vertices['xsi_b'] = 0.0
            subarea_segment_rel_vertices['xsi_c'] = xsi1
            subarea_segment_rel_vertices['xsi_d'] = xsi2
            self.subarea.update({device_type: WingSegmentSubdivisionSubarea(self,
                                subarea_segment_rel_vertices, subarea_type='slat')})

            self.subarea['segment'].rel_vertices['xsi_a'] = xsi1
            self.subarea['segment'].rel_vertices['xsi_b'] = xsi2

        elif device_type == 'flap':
            subarea_segment_rel_vertices = {}
            subarea_segment_rel_vertices['xsi_a'] = xsi1
            subarea_segment_rel_vertices['xsi_b'] = xsi2
            subarea_segment_rel_vertices['xsi_c'] = 1.0
            subarea_segment_rel_vertices['xsi_d'] = 1.0
            self.subarea.update({device_type: WingSegmentSubdivisionSubarea(self,
                                subarea_segment_rel_vertices, subarea_type='flap')})

            self.subarea['segment'].rel_vertices['xsi_c'] = xsi2
            self.subarea['segment'].rel_vertices['xsi_d'] = xsi1

        # Update the relative hinge positions and add reference to parent control object
        self.subarea[device_type]._add_hinge_line(xsi_h1, xsi_h2)
        self.subarea[device_type]._add_parent_control(parent_control)

        return self.subarea[device_type]

    def _transform(self, le_translation, le_rotation):
        """
        Perform a coordinate transformation for the current subdivision.

        Args:
            :le_translation: (float) leading edge translation
            :le_rotation: (float) leading edge rotation
        """

        pass

    def _update_subarea(self, device_type, xsi1, xsi2, xsi_h1, xsi_h2):
        """
        Update an existing subarea and keep consistency with other subareas.

        Args:
            :device_type: (str) 'flap' or 'slat'
            :xsi1: (float) inner xsi position of the area division
            :xsi2: (float) outer xsi position of the area division
            :xsi_h1: (float) relative position of the inner hinge point
            :xsi_h2: (float) relative position of the outer hinge point
        """

        # TODO: add checks ??

        if device_type == 'slat':
            self.subarea['slat'].rel_vertices['xsi_c'] = xsi2
            self.subarea['slat'].rel_vertices['xsi_d'] = xsi1

            self.subarea['segment'].rel_vertices['xsi_a'] = xsi1
            self.subarea['segment'].rel_vertices['xsi_b'] = xsi2

            self.subarea['slat'].rel_hinge_vertices['xsi_h1'] = xsi_h1
            self.subarea['slat'].rel_hinge_vertices['xsi_h2'] = xsi_h2

        elif device_type == 'flap':
            self.subarea['flap'].rel_vertices['xsi_a'] = xsi1
            self.subarea['flap'].rel_vertices['xsi_b'] = xsi2

            self.subarea['segment'].rel_vertices['xsi_c'] = xsi2
            self.subarea['segment'].rel_vertices['xsi_d'] = xsi1

            self.subarea['flap'].rel_hinge_vertices['xsi_h1'] = xsi_h1
            self.subarea['flap'].rel_hinge_vertices['xsi_h2'] = xsi_h2


class WingSegmentSubdivisionSubarea(FixedNamespace):
    """
    WingSegmentSubdivisionSubarea is a "child class" of WingSegmentSubdivision.

    This object provides the basic geometric definition of subareas within a
    segment subdivision. Subareas are defined by their xsi coordinates within
    the subdivision. Absolute coordinates can be computed by calling the parent
    objects.

    Attributes:
        :_subdivision: (obj) reference to the parent subdivision object
        :rel_vertices: (dict) relative coordinates of the subarea defined by xsi coordinates
        :rel_hinge: (dict) relative coordinates of the hinge line (only for subarea of type {'flap', 'slat'})
        :parent_control: (obj) reference to the parent control object (only for subarea of type {'flap', 'slat'})
    """

    def __init__(self, subdivision, rel_vertices, subarea_type):
        """
        Initialise the WingSegmentSubdivisionSubarea.

        Args:
            :subdivision: (obj) parent object (subdivision)
            :rel_vertices: (dict) relative coordinates of the subarea (xsi)
        """

        super().__init__()

        # Keep a reference about the parent object (subdivision)
        self.parent_subdivision = subdivision
        self.parent_segment = self.parent_subdivision.parent_segment
        self.parent_wing = self.parent_subdivision.parent_segment.parent_wing

        self.type = subarea_type

        # Relative position of vertices
        self.rel_vertices = FixedOrderedDict()
        self.rel_vertices['xsi_a'] = rel_vertices['xsi_a']
        self.rel_vertices['xsi_b'] = rel_vertices['xsi_b']
        self.rel_vertices['xsi_c'] = rel_vertices['xsi_d']
        self.rel_vertices['xsi_d'] = rel_vertices['xsi_c']
        self.rel_vertices._freeze()

        # For subareas of type 'slat' and 'flap'
        # - Relative position of hinge line
        # - Parent control device
        self.rel_hinge = None
        self.parent_control = None

        self._freeze()

    @property
    def rel_length(self):
        """
        Return the average 'xsi length' of the subarea

        Returns:
            :xsi_avg: (float) average xsi length
        """

        xsi_a = self.rel_vertices['xsi_a']
        xsi_b = self.rel_vertices['xsi_b']
        xsi_c = self.rel_vertices['xsi_c']
        xsi_d = self.rel_vertices['xsi_d']

        return 0.5*((xsi_c + xsi_d) - (xsi_a + xsi_b))

    @property
    def symmetry(self):
        """
        Get symmetry property of subarea (inherited from parent wing).

        Returns:
            :symmetry: (int) symmetry property
        """

        return self.parent_wing.symmetry

    @property
    def segment_vertices(self):
        """
        Get segments coordinates of the parent segment.

        Returns:
            :vertices: (dict) dictionary segment vertices
        """

        return self.parent_subdivision.parent_segment.vertices

    def abs_vertices(self, mirror):
        """
        Get absolute coordinates of subarea vertices.

        Wing deformations are taken into account.

        Args:
            :mirror: (bool) optional flag, if true mirror is returned

        Returns:
            :abs_vertices: (dict) dictionary with absolute coordinates of subarea vertices
        """

        subdivision_vertices = self.parent_subdivision.abs_vertices(mirror)

        a_sd = subdivision_vertices['a']
        b_sd = subdivision_vertices['b']
        c_sd = subdivision_vertices['c']
        d_sd = subdivision_vertices['d']

        xsi_a = self.rel_vertices['xsi_a']
        xsi_b = self.rel_vertices['xsi_b']
        xsi_c = self.rel_vertices['xsi_c']
        xsi_d = self.rel_vertices['xsi_d']

        if mirror:
            xsi_a, xsi_b, xsi_c, xsi_d = order_mirrored_vertex_points((xsi_a, xsi_b, xsi_c, xsi_d), self.symmetry)

        a_abs = a_sd + xsi_a*(d_sd - a_sd)
        b_abs = b_sd + xsi_b*(c_sd - b_sd)
        c_abs = b_sd + xsi_c*(c_sd - b_sd)
        d_abs = a_sd + xsi_d*(d_sd - a_sd)

        return {'a': a_abs, 'b': b_abs, 'c': c_abs, 'd': d_abs}

    def abs_hinge_vertices(self, mirror):
        """
        Get absolute coordinates of subarea hinge points.

        Wing deformations are taken into account.

        Args:
            :mirror: (bool) optional flag, if true mirror is returned

        Returns:
            :abs_hinge_vertices: (dict) dictionary with absolute hinge coordinates of subarea vertices
        """

        subdivision_vertices = self.parent_subdivision.abs_vertices(mirror)

        a_sd = subdivision_vertices['a']
        b_sd = subdivision_vertices['b']
        c_sd = subdivision_vertices['c']
        d_sd = subdivision_vertices['d']

        xsi_h1 = self.rel_hinge_vertices['xsi_h1']
        xsi_h2 = self.rel_hinge_vertices['xsi_h2']

        # Only in case of type 2 symmetry, the xsi coordinates should be swapped
        if mirror and self.symmetry == 2:
            xsi_h1, xsi_h2 = xsi_h2, xsi_h1

        p_inner = a_sd + xsi_h1*(d_sd - a_sd)
        p_outer = b_sd + xsi_h2*(c_sd - b_sd)

        return {'p_inner': p_inner, 'p_outer': p_outer}

    def abs_hinge_axis(self, mirror):
        """
        Get the hinge axis vector in the global coordinate system.

        Wing deformations are taken into account.

        Args:
            :mirror: (bool) optional flag, if true mirror axis is returned

        Returns:
            :abs_hinge_axis: absolute hinge axis in global system
        """

        hinge_vertices = self.abs_hinge_vertices(mirror)
        p_inner = hinge_vertices['p_inner']
        p_outer = hinge_vertices['p_outer']

        return p_outer - p_inner

    def abs_camber_line_rot_axis_vertices(self, mirror):
        """
        Get the rotation axis for the camber line.

        Note:
            * The rotation axis is defined by two points.

        Args:
            :mirror: (bool) optional flag, if true mirror axis is returned

        Returns:
            :abs_vertices: absolute axis vertices in global system
        """

        subarea_vertices = self.abs_vertices(mirror)

        a = subarea_vertices['a']
        b = subarea_vertices['b']
        d = subarea_vertices['d']

        ab = b - a
        ad = d - a

        subarea_normal = np.cross(ab, ad)
        rot_axis = np.cross(subarea_normal, ad)

        p_inner = a
        p_outer = a + rot_axis/np.linalg.norm(rot_axis)

        return {'p_inner': p_inner, 'p_outer': p_outer}

    def abs_camber_line_rot_axis(self, mirror):
        """
        Get the axis vector for camber line rotations in the global coordinate system.

        Wing deformations are taken into account.

        Args:
            :mirror: (bool) optional flag, if true mirror axis is returned

        Returns:
            :abs_axis: absolute axis in global system
        """

        axis_vertices = self.abs_camber_line_rot_axis_vertices(mirror)
        p_inner = axis_vertices['p_inner']
        p_outer = axis_vertices['p_outer']

        return p_outer - p_inner

    def _add_hinge_line(self, xsi_h1, xsi_h2):
        """
        Add a hinge to the subdivision.

        Args:
            :xsi_h1: (float) relative position of the inner hinge point
            :xsi_h2: (float) relative position of the outer hinge point
        """

        self._unfreeze()
        self.rel_hinge_vertices = FixedOrderedDict()
        self.rel_hinge_vertices['xsi_h1'] = xsi_h1
        self.rel_hinge_vertices['xsi_h2'] = xsi_h2
        self.rel_hinge_vertices._freeze()
        self._freeze()

    def _add_parent_control(self, control_object):
        """
        Add a reference to the parent control device.

        Args:
            :control_object: (obj) control object to which the subarea belongs
        """

        # TODO: add tests ???

        self.parent_control = control_object

    def get_xsi_for_collocation_points(self, num_panels):
        """
        Return the relative xsi coordinates of a panel collocation points

        Note:
            * This functions assumes that all panels are linearly spaced!
            * Work for mirrored/non-mirrored subareas

        Args:
            :num_panels: number of panels on a segment subdivision

        Returns:
            :segment_xsi: list with xsi values of the collocation points
        """

        xsi_mid_ab = (self.rel_vertices['xsi_a'] + self.rel_vertices['xsi_b'])/2
        xsi_mid_cd = (self.rel_vertices['xsi_c'] + self.rel_vertices['xsi_d'])/2

        segment_xsi = []
        for i in range(num_panels):
            # Collocation points have a relative chordwise location of 0.75
            xsi = xsi_mid_ab + ((i + 0.75)/num_panels)*(xsi_mid_cd - xsi_mid_ab)
            segment_xsi.append(xsi)

        return segment_xsi


def get_abs_segment_point_coords(segment_vertices, eta, xsi):
    """
    Compute the absolute coordinates for a point on a segment

    Warning:
        * The function does only work for UNDEFORMED segments!

    Args:
        :segment_vertices: (dict) segment vertices
        :rel_coords: (dict) relative coordinates (eta, xsi)

    Returns:
        :p: (ndarray) absolute coordinates
    """

    a = segment_vertices['a']
    b = segment_vertices['b']
    c = segment_vertices['c']
    d = segment_vertices['d']

    a_eta = a + eta*(b - a)
    d_eta = d + eta*(c - d)

    return a_eta + xsi*(d_eta - a_eta)


def xsi_interpol(segment_vertices, rel_inner, rel_outer, eta):
    """
    Return the linear interpolation of xsi value based on relative segment coordinates

    Args:
        :segment_vertices: (dict) segment vertices
        :rel_inner: (tuple) eta and xsi coordinates of the inner position
        :rel_outer: (tuple) eta and xsi coordinates of the outer position
        :eta: (float) eta position at which xsi is to be interpolated

    Return:
        :xsi_interpol: (float) interpolated value for xsi
    """

    eta_inner, xsi_inner = rel_inner
    eta_outer, xsi_outer = rel_outer

    p_inner = get_abs_segment_point_coords(segment_vertices, eta_inner, xsi_inner)
    p_outer = get_abs_segment_point_coords(segment_vertices, eta_outer, xsi_outer)
    insegment_direction = p_inner - p_outer

    p_upper = get_abs_segment_point_coords(segment_vertices, eta, 0)
    p_lower = get_abs_segment_point_coords(segment_vertices, eta, 1)

    a = segment_vertices['a']
    b = segment_vertices['b']
    d = segment_vertices['d']

    segment_normal = np.cross(b-a, d-a)
    intersect_plane_normal = np.cross(segment_normal, p_lower-p_upper)

    p_intersect = get_plane_line_intersect(intersect_plane_normal, p_upper, insegment_direction, p_inner)
    xsi_interpol = np.linalg.norm(p_intersect-p_upper)/np.linalg.norm(p_lower-p_upper)

    return xsi_interpol


def mirror_point(point, plane):
    """
    Mirror a point in 3D space about a symmetry plane.

    Args:
        :point: point
        :plane: (str) plane ('xy', 'xz' or 'yz')
    """

    point = copy(point)

    if plane == 'xy' or plane == 1:
        point[2] = -point[2]
    elif plane == 'xz' or plane == 2:
        point[1] = -point[1]
    elif plane == 'yz' or plane == 3:
        point[0] = -point[0]
    else:
        raise ValueError("Invalid plane (plane: {})".format(plane))

    return point


def order_mirrored_vertex_points(vertices, plane):
    """
    Order mirrored vertex points to keep consistent global system

    Args:
        :vertices: (tuple) vertices like (a, b, c, d)
        :plane: (str) plane ('xy', 'xz' or 'yz')

    Returns:
        :ordered_vertices: (tuple) ordered vertices
    """

    a, b, c, d = vertices

    if plane == 'xy' or plane == 1:
        pass
    elif plane == 'xz' or plane == 2:
        a, b, c, d = b, a, d, c
    elif plane == 'yz' or plane == 3:
        a, b, c, d = d, c, b, a
    else:
        raise ValueError("Invalid plane (plane: {})".format(plane))

    return (a, b, c, d)


def mirror_vertices(vertices, plane):
    """
    Mirror vertices and keep vertex points consistently ordered.

    This is a wrapper combining the mirroring and ordering.

    Args:
        :vertices: (tuple) vertices like (a, b, c, d)
        :plane: (str) plane ('xy', 'xz' or 'yz')

    Returns:
        :ordered_vertices: (tuple) ordered vertices
    """

    a, b, c, d = vertices

    a = mirror_point(a, plane)
    b = mirror_point(b, plane)
    c = mirror_point(c, plane)
    d = mirror_point(d, plane)

    return order_mirrored_vertex_points((a, b, c, d), plane)

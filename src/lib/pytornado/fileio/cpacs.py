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

# TODO:
# *** Extract flight state from CPACS (AEROPERFORMANCE MAPS)
# *** Write back to CPACS

import os
import logging
import numpy as np

from pytornado.fileio.utils import parse_str
from pytornado.objects.model import ComponentDefinitionError
from pytornado.objects.objecttools import all_controls, all_wings

# ----- (START) Temporary fix -----
from pytornado.fileio.cpacs_patch import PATCH_getControlSurfaceCount, PATCH_getControlSurfaceUID
# ----- (END) Temporary fix -----

logger = logging.getLogger(__name__)

TIXI_INSTALLED = True
try:
    import tixi3.tixi3wrapper as tixiwrapper
    tixiwrapper.Tixi = tixiwrapper.Tixi3
    tixiwrapper.TixiException = tixiwrapper.Tixi3Exception
except ImportError:
    TIXI_INSTALLED = False

TIGL_INSTALLED = True
try:
    import tigl3.tigl3wrapper as tiglwrapper
    tiglwrapper.Tigl = tiglwrapper.Tigl3
except ImportError:
    TIGL_INSTALLED = False

# ----- CPACS paths -----
XPATH_MODEL = '/cpacs/vehicles/aircraft/model'
XPATH_REFS = XPATH_MODEL + '/reference'
XPATH_WINGS = XPATH_MODEL + '/wings'
XPATH_AIRFOILS = '/cpacs/vehicles/profiles/wingAirfoils'
XPATH_APMAP = '/cpacs/vehicles/aircraft/analyes/aeroPerformanceMap'
XPATH_TOOLSPEC = '/cpacs/toolspecific/CEASIOMpy/PyTornado'

XPATH_CONTROL = XPATH_WINGS \
    + '/wing[{0:d}]/componentSegments/componentSegment[{1:d}]' \
    + '/controlSurfaces/{3:s}EdgeDevices/{3:s}EdgeDevice[{2:d}]'

XPATH_TOOLSPEC_CONTROL = XPATH_TOOLSPEC + '/controlDevices'


COORD_FORMAT = '%+.7f'


def open_tixi(cpacs_file):
    """
    Return a Tixi handle

    Args:
        :cpacs_file: CPACS file path

    Returns:
        :tixi: Tixi handle
    """

    logger.debug("Checking Tixi installation...")
    if not TIXI_INSTALLED:
        err_msg = """
        Unable to import Tixi. Please make sure Tixi is accessible to Python.
        Please refer to the documentation to check supported versions of Tixi.
        """
        logger.error(err_msg)
        raise ModuleNotFoundError(err_msg)

    tixi = tixiwrapper.Tixi()
    tixi.open(cpacs_file)
    return tixi


def open_tigl(tixi):
    """
    Return a Tigl handle

    Args:
        :tixi: Tixi handle

    Returns:
        :tigl: Tigl handle
    """

    logger.debug("Checking Tigl installation...")
    if not TIGL_INSTALLED:
        err_msg = """
        Unable to import Tigl. Please make sure Tigl is accessible to Python.
        Please refer to the documentation to check supported versions of Tigl.
        """
        logger.error(err_msg)
        raise ModuleNotFoundError(err_msg)

    tigl = tiglwrapper.Tigl()
    # On argument 'uid' from Tigl documentation: The UID of the configuration
    # that should be loaded by TIGL. Could be NULL or an empty string if the
    # data set contains only one configuration.
    tigl.open(tixi, uid='')
    return tigl


def get_segment_mid_point(tigl, idx_wing, idx_segment, eta, xsi):
    """
    Return a mid point for a segment

    Args:
        :tigl: Tigl handle
        :idx_wing: Wing index
        :idx_segment: Segment index
        :eta: Relative segment coordinate
        :xsi: Relative segment coordinate
    """

    lower = tigl.wingGetLowerPoint(idx_wing, idx_segment, eta, xsi)
    upper = tigl.wingGetUpperPoint(idx_wing, idx_segment, eta, xsi)
    mid_point = [(l + u)/2.0 for l, u in zip(lower, upper)]
    return mid_point


def get_aircraft_name(aircraft, tixi):
    """
    Extract the aircraft name from CPACS and add it to the aircraft model

    Args:
        :aircraft: Aircraft model
        :tixi: Tixi handle
    """

    if tixi.checkElement(XPATH_MODEL):
        aircraft_uid = parse_str(tixi.getTextAttribute(XPATH_MODEL, 'uID'))
        logger.debug(f"Aircraft name: '{aircraft.uid}'")
    else:
        logger.warning(f"Could not find path '{XPATH_MODEL}'")
        aircraft_uid = 'NAME_NOT_FOUND'

    aircraft.uid = aircraft_uid


def get_aircraft_wings(aircraft, settings, tixi, tigl):
    """
    Extract aircraft wings including airfoils and controls

    Args:
        :aircraft: Aircraft model
        :tixi: Tixi handle
        :tigl: Tigl handle
    """

    logger.info("Loading aircraft wings...")
    if not tixi.checkElement(XPATH_WINGS):
        err_msg = f"""
        Could not find path '{XPATH_WINGS}'.
        The aircraft must have at least one wing.
        """
        logger.error(err_msg)
        raise ValueError(err_msg)

    # ---------- Iterate through wings ----------
    num_wings = tixi.getNamedChildrenCount(XPATH_WINGS, 'wing')
    for idx_wing in range(1, num_wings + 1):
        xpath_wing = XPATH_WINGS + f"/wing[{idx_wing}]"

        try:
            wing_uid = parse_str(tixi.getTextAttribute(xpath_wing, 'uID'))
        except tixiwrapper.TixiException:
            wing_uid = f'WING{idx_wing:02}'

        logger.debug(f"Wing name: '{wing_uid}'")

        aircraft.add_wing(wing_uid)
        aircraft.wing[wing_uid].symmetry = tigl.wingGetSymmetry(idx_wing)

        # For each wing we set segment and control data
        get_aircraft_wing_segments(aircraft, settings, xpath_wing, wing_uid, idx_wing, tixi, tigl)
        get_aircraft_controls(aircraft, wing_uid, idx_wing, tixi, tigl)

def get_aircraft_wing_segments(aircraft, settings, xpath_wing, wing_uid, idx_wing, tixi, tigl):
    """
    Extract a wing segment for a given wing

    Args:
        :aircraft: Aircraft model
        :settings: Settings object
        :xpath_wing: CPACS wing path
        :idx_wing: Wing index
        :tixi: Tixi handle
        :tigl: Tigl handle
    """

    xpath_segments = xpath_wing + '/segments'
    if not tixi.checkElement(xpath_segments):
        err_msg = f"Could not find path '{xpath_segments}'"
        logger.error(err_msg)
        raise ValueError(err_msg)

    logger.debug(f"Loading segments of wing '{wing_uid}'...")

    # ---------- Iterate through segments of given wing ----------
    num_segments = tixi.getNamedChildrenCount(xpath_segments, 'segment')
    for idx_segment in range(1, num_segments + 1):
        node_segment = xpath_segments + f"/segment[{idx_segment}]"

        try:
            segment_uid = parse_str(tixi.getTextAttribute(node_segment, 'uID'))
        except tixiwrapper.TixiException:
            segment_uid = f"{wing_uid}_SEGMENT{idx_segment:02}"

        logger.debug(f"Loading segment '{segment_uid}'...")

        aircraft.wing[wing_uid].add_segment(segment_uid)

        # Get the absolute segment vertices
        a = get_segment_mid_point(tigl, idx_wing, idx_segment, eta=0, xsi=0)
        b = get_segment_mid_point(tigl, idx_wing, idx_segment, eta=1, xsi=0)
        c = get_segment_mid_point(tigl, idx_wing, idx_segment, eta=1, xsi=1)
        d = get_segment_mid_point(tigl, idx_wing, idx_segment, eta=0, xsi=1)

        #########################################################################
        ## TODO: Put this in "objects.model!?"
        #########################################################################
        # Re-order vertices
        # * A, D should be at root and B, C at tip
        # * This is done so that the segments (thus panel normals point in the correct direction)
        if b[1] - a[1] < 0.0 or (b[1] == a[1] and b[2] - a[2] < 0.0):
            a, b, c, d = b, a, c, d
        if c[1] - d[1] < 0.0 or (c[1] == d[1] and c[2] - d[2] < 0.0):
            a, b, c, d = a, b, d, c
        if d[0] - a[0] < 0.0:
            a, b, c, d = d, b, c, a
        if c[0] - b[0] < 0.0:
            a, b, c, d = a, c, b, d
        #########################################################################
        #########################################################################
        #########################################################################

        aircraft.wing[wing_uid].segment[segment_uid].vertices['a'] = a
        aircraft.wing[wing_uid].segment[segment_uid].vertices['b'] = b
        aircraft.wing[wing_uid].segment[segment_uid].vertices['c'] = c
        aircraft.wing[wing_uid].segment[segment_uid].vertices['d'] = d

        # ----- Set airfoils -----
        get_aircraft_airfoils(aircraft, settings, tigl, wing_uid, segment_uid, idx_wing, idx_segment)


def get_aircraft_controls(aircraft, wing_uid, idx_wing, tixi, tigl):
    """
    Extract the controls surfaces

    Args:
        :aircraft: Aircraft model
        :wing_uid: Name of the wing
        :idx_wing: Index of the wing
        :tixi: Tixi handle
        :tigl: Tigl handle

    .. warning::

        * CPACS3 changed the control surface defintions!
        * In Tigl 3.0.0 some fuctions for controlSurfaces are missing
          (currently we use a workaround, see PATCH_* functions)
        * In CPACS3 relative coordinates can be defined based on a 'section' or
          'componentSegment', currently we assume the old definition (based on
          'componentSegment')
    """

    # Abbreviate long function name
    tigl.get_eta_xsi = tigl.wingComponentSegmentPointGetSegmentEtaXsi

    # ---------- Iterate through component sections (contain control surfaces) ----------
    num_comp_sections = tigl.wingGetComponentSegmentCount(idx_wing)
    for idx_comp_section in range(1, num_comp_sections + 1):
        name_comp_section = tigl.wingGetComponentSegmentUID(idx_wing, idx_comp_section)

        # ---------- Iterate through controls ----------
        # PATCHED # for idx_control in range(1, tigl.getControlSurfaceCount(name_comp_section) + 1):
        num_controls = PATCH_getControlSurfaceCount(tixi, name_comp_section)
        for idx_control in range(1, num_controls + 1):
            for device_pos in ('leading', 'trailing'):
                # PATCHED # control_uid = tigl.getControlSurfaceUID(name_comp_section, idx_control)
                control_uid = PATCH_getControlSurfaceUID(tixi, name_comp_section, idx_control)
                logger.debug(f"Wing {idx_wing:d} has control '{control_uid:s}'")
                node_control = XPATH_CONTROL.format(idx_wing, idx_comp_section, idx_control, device_pos)

                # Try to read the relative coordinates for each control (eta, xsi)
                # ======================================================
                # TODO: does tixi.getDoubleElement() raise an error???
                # ======================================================
                try:
                    # Control vertices
                    etaLE_ib = tixi.getDoubleElement(node_control + "/outerShape/innerBorder/etaLE/eta")
                    etaTE_ib = tixi.getDoubleElement(node_control + "/outerShape/innerBorder/etaTE/eta")
                    xsiLE_ib = tixi.getDoubleElement(node_control + "/outerShape/innerBorder/xsiLE/xsi")
                    etaLE_ob = tixi.getDoubleElement(node_control + "/outerShape/outerBorder/etaLE/eta")
                    etaTE_ob = tixi.getDoubleElement(node_control + "/outerShape/outerBorder/etaTE/eta")
                    xsiLE_ob = tixi.getDoubleElement(node_control + "/outerShape/outerBorder/xsiLE/xsi")

                    # Hinge parameters
                    hingeXsi_ib = tixi.getDoubleElement(node_control + "/path/innerHingePoint/hingeXsi")
                    hingeXsi_ob = tixi.getDoubleElement(node_control + "/path/outerHingePoint/hingeXsi")

                except tixiwrapper.TixiException:
                    logger.debug(f"No control data found for NODE {node_control:s}")
                    continue

                if device_pos == 'leading':
                    # Enforcing parallelism between control edges and x-axis
                    xsiLE_ib = 0.0
                    xsiLE_ob = 0.0

                    # Relative coordinates of control w.r.t. component segment
                    _, segment_uid_inner, eta_inner, xsi_inner = tigl.get_eta_xsi(name_comp_section, etaTE_ib, xsiTE_ib)
                    _, segment_uid_outer, eta_outer, xsi_outer = tigl.get_eta_xsi(name_comp_section, etaTE_ob, xsiTE_ob)

                    # Relative coordinates of control hinge line w.r.t. component segment
                    _, _, _, xsi_h1 = tigl.get_eta_xsi(name_comp_section, etaTE_ib, hingeXsi_ib)
                    _, _, _, xsi_h2 = tigl.get_eta_xsi(name_comp_section, etaTE_ob, hingeXsi_ob)

                elif device_pos == 'trailing':
                    xsiTE_ib = 1.0
                    xsiTE_ob = 1.0

                    # Relative coordinates of control w.r.t. component segment
                    _, segment_uid_inner, eta_inner, xsi_inner = tigl.get_eta_xsi(name_comp_section, etaLE_ib, xsiLE_ib)
                    _, segment_uid_outer, eta_outer, xsi_outer = tigl.get_eta_xsi(name_comp_section, etaLE_ob, xsiLE_ob)

                    # Relative coordinates of control hinge line w.r.t. component segment
                    _, _, _, xsi_h1 = tigl.get_eta_xsi(name_comp_section, etaLE_ib, hingeXsi_ib)
                    _, _, _, xsi_h2 = tigl.get_eta_xsi(name_comp_section, etaLE_ob, hingeXsi_ob)

                # ADD WING CONTROL AND SET ATTRIBUTES
                control = aircraft.wing[wing_uid].add_control(control_uid, return_control=True)
                control.device_type = 'flap' if device_pos == 'trailing' else 'slat'

                # Set DEFAULT deflection to 0
                control.deflection = 0

                control.rel_vertices['eta_inner'] = eta_inner
                control.rel_vertices['xsi_inner'] = xsi_inner
                control.rel_vertices['eta_outer'] = eta_outer
                control.rel_vertices['xsi_outer'] = xsi_outer

                control.rel_hinge_vertices['xsi_inner'] = xsi_h1
                control.rel_hinge_vertices['xsi_outer'] = xsi_h2

                control.segment_uid['inner'] = segment_uid_inner
                control.segment_uid['outer'] = segment_uid_outer

    # ----- CONTROL SURFACE DEFLECTION -----
    try:
        n_control_dev = tixi.getNamedChildrenCount(XPATH_TOOLSPEC_CONTROL, 'controlDevice')
    except:
        n_control_dev = 0

    for idx_control in range(1, n_control_dev + 1):
        node_control_device = XPATH_TOOLSPEC_CONTROL + '/controlDevice[{}]'.format(idx_control)
        control_uid = tixi.getTextAttribute(node_control_device, 'uID')
        deflection = 0
        deflection_mirror = None

        try:
            deflection = tixi.getDoubleElement(node_control_device + '/deflection')
        except tixiwrapper.TixiException:
            logger.error("Unable to read 'deflection' for control '{:s}'".format(control_uid))

        try:
            deflection_mirror = tixi.getDoubleElement(node_control_device + '/deflectionMirror')
        except:
            logger.warning("Unable to read 'deflection_mirror' for control '{:s}'".format(control_uid))

        deflection_is_set = False

        for this_wing in all_wings(aircraft):
            wing = this_wing[2]

            if control_uid in wing.control.keys():
                wing.control[control_uid].deflection = deflection
                wing.control[control_uid].deflection_mirror = deflection_mirror
                deflection_is_set = True
                break

        if not deflection_is_set:
            logger.error("Could not set deflection for control '{:s}'".format(control_uid))
            raise ComponentDefinitionError("Control '{:s}' not found".format(control_uid))

    # ----- CONTROL CHECKS -----
    for this_control, _ in all_controls(aircraft):
        this_control[2].check()


def get_aircraft_airfoils(aircraft, settings, tigl, wing_uid, segment_uid, idx_wing, idx_segment):
    """
    Extract the aircraft airfoils

    Args:
        :aircraft: Aircraft model
        :settings: Settings object
        :tigl: Tigl handle
        :segment_uid: Name of the segment
        :idx_wing: Index of the wing
        :idx_segment: Index of the segment
    """

    for position in ['inner', 'outer']:
        if position == 'inner':
            tigl_func = tigl.wingGetInnerSectionAndElementIndex
        else:
            tigl_func = tigl.wingGetOuterSectionAndElementIndex

        idx_section, idx_elem = tigl_func(idx_wing, idx_segment)
        name_airfoil = parse_str(tigl.wingGetProfileName(idx_wing, idx_section, idx_elem))
        if not name_airfoil:
            err_msg = f"""
            CPACS error: Could not extract {position} airfoil name
            * Wing: {idx_wing}
            * Segment: {idx_section}
            """
            raise ValueError(msg)

        file_airfoil = f"blade.{name_airfoil}"
        file_airfoil = os.path.join(settings.dirs['airfoils'], file_airfoil)
        aircraft.wing[wing_uid].segment[segment_uid].airfoils[position] = file_airfoil


def write_airfoil_files(settings, tixi):
    """
    Extract airfoil data from CPACS and write airfoil files

    Args:
        :settings: Settings object
        :tixi: Tixi handle
    """

    logger.debug("Extracting airfoil data...")
    num_airfoils = tixi.getNumberOfChilds(XPATH_AIRFOILS)
    for i in range(1, num_airfoils + 1):
        node_airfoil = XPATH_AIRFOILS + f"/wingAirfoil[{i}]"
        node_data = node_airfoil + "/pointList"

        try:
            name_airfoil = parse_str(tixi.getTextElement(node_airfoil + '/name'))
        except tixiwrapper.TixiException:
            name_airfoil = f'AIRFOIL{i:02d}'

        file_airfoil = os.path.join(settings.dirs['airfoils'], f"blade.{name_airfoil}")

        # Convert string to numpy array
        coords_x = np.fromstring(tixi.getTextElement(node_data + '/x'), sep=';')
        coords_z = np.fromstring(tixi.getTextElement(node_data + '/z'), sep=';')
        coords = np.transpose([coords_x, coords_z])

        logger.info(f"Copying airfoil {name_airfoil} to file...")
        np.savetxt(file_airfoil, coords, header=f"{name_airfoil}", fmt=COORD_FORMAT)


def get_aircraft_refs(aircraft, tixi):
    """
    Extract the aircraft reference values

    Args:
        :aircraft: Aircraft model
        :tixi: Tixi handle

    .. warning::

        * 'rcenter' is same as 'gcenter'
        * Currently there is only one reference length in CPACS
    """

    aircraft.refs['gcenter'] = np.zeros(3, dtype=float, order='C')
    aircraft.refs['gcenter'][0] = tixi.getDoubleElement(XPATH_REFS + '/point/x')
    aircraft.refs['gcenter'][1] = tixi.getDoubleElement(XPATH_REFS + '/point/y')
    aircraft.refs['gcenter'][2] = tixi.getDoubleElement(XPATH_REFS + '/point/z')

    aircraft.refs['rcenter'] = np.zeros(3, dtype=float, order='C')
    aircraft.refs['rcenter'][0] = tixi.getDoubleElement(XPATH_REFS + '/point/x')
    aircraft.refs['rcenter'][1] = tixi.getDoubleElement(XPATH_REFS + '/point/y')
    aircraft.refs['rcenter'][2] = tixi.getDoubleElement(XPATH_REFS + '/point/z')

    aircraft.refs['area'] = tixi.getDoubleElement(XPATH_REFS + '/area')
    aircraft.refs['span'] = tixi.getDoubleElement(XPATH_REFS + '/length')
    aircraft.refs['chord'] = tixi.getDoubleElement(XPATH_REFS + '/length')


def load(aircraft, state, settings):
    """
    Get aircraft model, flight state and settings data from a CPACS file

    Args:
        :aircraft: Aircraft model
        :state: (object) Data structure for flight state
        :settings: Settings object
    """

    cpacs_file = settings.files['aircraft']
    logger.info(f"Loading aircraft from CPACS file: {cpacs_file}...")
    if not os.path.exists(cpacs_file):
        err_msg = f"File '{cpacs_file}' not found"
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    tixi = open_tixi(cpacs_file)
    tigl = open_tigl(tixi)

    # Reset the aircraft model
    aircraft.reset()

    # Extract CPACS data and add to aircraft model
    get_aircraft_name(aircraft, tixi)
    get_aircraft_wings(aircraft, settings, tixi, tigl)
    write_airfoil_files(settings, tixi)
    get_aircraft_refs(aircraft, tixi)

    tixi.close()

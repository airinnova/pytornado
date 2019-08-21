#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

import numpy as np
import pytest

from pytornado.stdfun import StdRunArgs, standard_run


HERE = os.path.abspath(os.path.dirname(__file__))

def test_panel_forces():
    """
    Check that panel forces are located at the correct positions
    """

    testdir = "test1"

    args = StdRunArgs()
    args.run = os.path.join(HERE, testdir, 'settings', 'test.json')
    standard_run(args)

    # -------------------------------------------------------------------------
    # Panel forces should act at theses coordinates
    # -------------------------------------------------------------------------

    path = os.path.join(HERE, testdir, "_results/test_000/loads_UID_wing1.json")
    with open(path, "r") as fp:
        loads = json.load(fp)

    exp_coords = np.array([
            [0.25, 0.25, 0],
            [0.125, 0.75, 0],
            [0.625, 0.75, 0],
            ])

    for entry, exp_coord in zip(loads, exp_coords):
        assert np.testing.assert_array_equal(entry['coord'], exp_coord) is None

    # -------------------------------------------------------------------------
    # Make sure panel forces sum up correctly
    # -------------------------------------------------------------------------

    Fx = 0
    Fy = 0
    Fz = 0
    for entry in loads:
        fx, fy, fz, _, _, _ = entry['load']

        Fx += fx
        Fy += fy
        Fz += fz

    path = os.path.join(HERE, testdir, "_results/test_000/test_global.json")
    with open(path, "r") as fp:
        glob_results = json.load(fp)

    assert Fx == pytest.approx(glob_results['global_forces']['x'])
    assert Fy == pytest.approx(glob_results['global_forces']['y'])
    assert Fz == pytest.approx(glob_results['global_forces']['z'])

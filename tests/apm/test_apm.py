#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

from pytest import approx, raises

from pytornado.stdfun import StdRunArgs, standard_run


HERE = os.path.abspath(os.path.dirname(__file__))
WKDIR = "wkdir"
SETTINGS_FILE = os.path.join(HERE, WKDIR, 'settings', 'template.json')
STATE_FILE = os.path.join(HERE, WKDIR, 'state', 'template.json')

ARGS = StdRunArgs()
ARGS.run = SETTINGS_FILE


def set_state_file(state):
    """Write a state file"""

    with open(STATE_FILE, "w") as fp:
        json.dump(state, fp)


def test_basic_analysis():
    """
    Check that panel forces are located at the correct positions
    """

    # ----- Single value input -----
    state = {
        "aero":
        {
            "airspeed": 100,
            "density": 1.225,
            "alpha": 0,
            "beta": 0,
            "rate_P": 0,
            "rate_Q": 0,
            "rate_R": 0,
            }
        }

    set_state_file(state)
    results = standard_run(ARGS)
    # assert

    # ----- Table input -----
    state = {
        "aero":
        {
            "airspeed": [100, 100],
            "density": [1.225, 1.225],
            "alpha": [0, 5],
            "beta": [0, 0],
            "rate_P": [0, 0],
            "rate_Q": [0, 0],
            "rate_R": [0, 0],
            }
        }

    set_state_file(state)
    results = standard_run(ARGS)
    print(results['state'].aero)
    print(results['state'].results)
    # assert

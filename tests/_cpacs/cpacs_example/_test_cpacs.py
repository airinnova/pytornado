#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

from pytest import approx, raises

from pytornado.stdfun import StdRunArgs, standard_run


HERE = os.path.abspath(os.path.dirname(__file__))
WKDIR = "wkdir"
SETTINGS_FILE = os.path.join(HERE, WKDIR, 'settings', 'D150_AGILE_Hangar.json')
STATE_FILE = os.path.join(HERE, WKDIR, 'state', 'example.json')

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

    os.chdir(os.path.join(HERE, WKDIR))

    state = {
        "aero":
        {
            "airspeed": None,
            "density": None,
            "mach": None,
            "altitude": None,
            "alpha": 0,
            "beta": 0,
            "rate_P": 0,
            "rate_Q": 0,
            "rate_R": 0,
            }
        }

    # Combination 1
    state['aero']['airspeed'] = 100
    state['aero']['density'] = 1.225
    state['aero']['mach'] = None
    state['aero']['altitude'] = None
    set_state_file(state)
    results = standard_run(ARGS)
    assert results['state'].aero['airspeed'] == approx(100)
    assert results['state'].aero['density'] == approx(1.225)

    # # Combination 2
    # state['aero']['airspeed'] = 100
    # state['aero']['density'] = None
    # state['aero']['mach'] = None
    # state['aero']['altitude'] = 0
    # set_state_file(state)
    # results = standard_run(ARGS)
    # assert results['state'].aero['airspeed'] == approx(100)
    # assert results['state'].aero['density'] == approx(1.225)

    # # Combination 3
    # state['aero']['airspeed'] = None
    # state['aero']['density'] = None
    # state['aero']['mach'] = 1
    # state['aero']['altitude'] = 0
    # set_state_file(state)
    # results = standard_run(ARGS)
    # assert results['state'].aero['airspeed'] == approx(340.2939)
    # assert results['state'].aero['density'] == approx(1.225)

    # # Invalid combination
    # state['aero']['airspeed'] = 100
    # state['aero']['density'] = None
    # state['aero']['mach'] = 1
    # state['aero']['altitude'] = 0
    # set_state_file(state)

    # with raises(ValueError):
    #     standard_run(ARGS)

if __name__ == '__main__':
    test_basic_analysis()

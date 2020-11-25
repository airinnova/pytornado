#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from pytornado.stdfun.run import StdRunArgs, standard_run


HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = "pytornado"
SETTINGS_FILE = os.path.join(HERE, PROJECT_DIR, 'settings', 'template.json')
STATE_FILE = os.path.join(HERE, PROJECT_DIR, 'state', 'example.json')

ARGS = StdRunArgs()
ARGS.run = SETTINGS_FILE


def test_basic_analysis():
    """
    Check that panel forces are located at the correct positions
    """

    results = standard_run(ARGS)

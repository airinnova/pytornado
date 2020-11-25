#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import os
import json

from pytornado.stdfun.run import standard_run, StdRunArgs
import pytornado.stdfun.setup as project_setup
from pytornado.objects.settings import PATHS


def test_plotting():
    """
    Make sure that all plot functions run and image files are generated
    """

    shutil.rmtree(PATHS.DIR.TEMPLATE_ROOT, ignore_errors=True)
    project_dir = project_setup.setup_wkdir()

    # ----- Modify settings file -----
    settings_file = os.path.join(project_dir, PATHS.DIR.SETTINGS, 'template.json')
    with open(settings_file, 'r') as fp:
        settings = json.load(fp)

    for plot_name in ['geometry', 'lattice', 'matrix_downwash', 'results']:
        settings['plot'][plot_name]['save'] = True
        settings['plot'][plot_name]['show'] = False

    with open(settings_file, 'w') as fp:
        json.dump(settings, fp)

    # ----- Run PyTornado -----
    standard_run(args=StdRunArgs(run=settings_file))

    # ----- Checks -----
    plot_dir = os.path.join(project_dir, PATHS.DIR.PLOTS, 'template_000')
    created_files = [f for f in os.listdir(plot_dir) if os.path.isfile(os.path.join(plot_dir, f))]

    # Check that file have correct suffix
    assert all([f.endswith('.png') for f in created_files])

    # Check that number of created plots is correct
    assert len(created_files) == 7

    # ----- Clean up -----
    shutil.rmtree(project_dir, ignore_errors=True)

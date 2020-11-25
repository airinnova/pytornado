#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
from pathlib import Path

import pytornado.database.tools as dbtools

def which(program):
    """
    Emulate 'which'

    See:

    https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def test_bin_exists():
    """
    Test that main executable exists and is executable
    """

    assert which('pytornado') is not None

    # Just make sure this runs without error
    os.system('pytornado -h')
    os.system('pytornado --help')


def test_basic_usage():
    """
    Test option to create minimal example
    """

    # Paths
    project_dir = Path('pytornado')
    settings_file = Path(os.path.join(project_dir, 'settings', 'template.json'))
    results_dir = Path(os.path.join(project_dir, '_results'))
    plot_dir = Path(os.path.join(project_dir, '_plots'))

    shutil.rmtree(project_dir, ignore_errors=True)

    # ------ Create basic example test case -----
    os.system('pytornado -v --make-example')
    assert project_dir.is_dir()

    # ------ Make sure it runs -----
    with open(settings_file, "r") as fp:
        settings = json.load(fp)
    settings['plot']['results']['show'] = False
    settings['plot']['results']['save'] = True
    with open(settings_file, "w") as fp:
        json.dump(settings, fp)
    os.system(f"pytornado -v --clean --run {settings_file}")
    os.system(f"pytornado -v --run {settings_file}")
    assert plot_dir.is_dir()
    assert results_dir.is_dir()

    # ------ Test the cleaning -----
    os.system(f"pytornado --clean-only --run {settings_file}")
    assert settings_file.is_file() is True
    assert plot_dir.is_dir() is False
    assert results_dir.is_dir() is False

    shutil.rmtree(project_dir, ignore_errors=True)


def test_database():
    """
    Test that all aircraft in the database can be loaded and run
    """

    # Paths
    project_dir = Path('pytornado')
    shutil.rmtree(project_dir, ignore_errors=True)

    # ------ Iterate through all aircraft in database -----
    for aircraft in dbtools.list_aircraft_names():
        print(f"Testing aircraft '{aircraft}'")
        os.system(f"pytornado -v --mdb {aircraft}")
        assert project_dir.is_dir()

        settings_file = Path(os.path.join(project_dir, 'settings', f'{aircraft}.json'))
        results_dir = Path(os.path.join(project_dir, '_results'))
        plot_dir = Path(os.path.join(project_dir, '_plots'))

        # ------ Make sure it runs -----
        with open(settings_file, "r") as fp:
            settings = json.load(fp)
        settings['plot']['results']['show'] = False
        settings['plot']['results']['save'] = True
        with open(settings_file, "w") as fp:
            json.dump(settings, fp)
        os.system(f"pytornado -v --clean --run {settings_file}")
        os.system(f"pytornado -v --run {settings_file}")
        assert plot_dir.is_dir()
        assert results_dir.is_dir()

        # ------ Test the cleaning -----
        os.system(f"pytornado --clean-only --run {settings_file}")
        assert settings_file.is_file() is True
        assert plot_dir.is_dir() is False
        assert results_dir.is_dir() is False

        shutil.rmtree(project_dir, ignore_errors=True)

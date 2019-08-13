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
Functions for visualisation of PyTornado aircraft geometry.

Developed at Airinnova AB, Stockholm, Sweden.
"""


import os
import logging

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from commonlibs.logger import truncate_filepath

from pytornado.plot.utils import get_date_str, COLOR1, COLORMAP

logger = logging.getLogger(__name__)


def view_downwash(vlmdata, plt_settings, block=True):
    """Visualise matrix of downwash factors.

    Args:
        :vlmdata: (object) data structure for VLM analysis data
        :block: (bool) halt execution while figure is open
    """

    logger.info("Generating downwash plot...")

    if not isinstance(vlmdata.matrix_downwash, np.ndarray):
        return logger.error("downwash factor matrix is empty!")

    # 2.1. DISPLAY MATRIX ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    colormap = cm.get_cmap(COLORMAP) if COLORMAP else None

    figure = plt.figure(figsize=(9, 9), edgecolor=COLOR1)
    axes = figure.add_subplot(111)
    axes.set_aspect('equal')
    axes.matshow(vlmdata.matrix_downwash, cmap=colormap)

    # 2.2. DISPLAY LABELS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    axes.set_xlabel('i')
    axes.set_ylabel('j')
    axes.set_title("Downwash factor matrix")

    plt.tight_layout()

    if plt_settings['save']:
        fname = os.path.join(plt_settings['plot_dir'], f"downwash_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname)}'")
        plt.savefig(fname, dpi=300)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')

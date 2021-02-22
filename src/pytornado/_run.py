#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2019-2020 Airinnova AB and the PyTornado authors
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

"""
Run the model
"""

from . import MODULE_NAME
from .__version__ import __version__
from ._assembly import create_system_matrices
from ._log import logger
from ._meshing import create_mesh
from ._plot import plot_all
from ._solve import solve


def run_model(m):
    """
    Run the complete model analysis

    Args:
        :m: model instance
    """

    logger.info(f"===== {MODULE_NAME} {__version__} =====")

    # ----- MESHING -----
    logger.info("Meshing...")
    create_mesh(m)

    # ----- ASSEMBLING SYSTEM MATRICES -----
    logger.info("Assembling matrices...")
    create_system_matrices(m)

    # ----- SOLVING -----
    logger.info("Solving...")
    solve(m)

    # ----- POST-PROCESSING -----
    logger.info("Post-processing...")
    plot_all(m)

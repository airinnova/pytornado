#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate the model API docuementation
"""

import os

from mframework import doc2rst

from pytornado._model import mspec

HERE = os.path.abspath(os.path.dirname(__file__))
doc2rst(mspec, HERE)

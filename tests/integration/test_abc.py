#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from pytornado import Model


def test_basic():
    model = Model()
    model.run()

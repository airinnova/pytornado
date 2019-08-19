#!/usr/bin/env bash

# python3 setup.py sdist bdist_wheel

# Workaround: do not upload a binary wheel for now
python3 setup.py sdist
twine upload dist/*

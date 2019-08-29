#!/usr/bin/env bash

cd $(dirname $0)

if [[ "$1" == "make" ]]; then
    pytornado --make-example
    python mod_settings.py
    pytornado -vr pytornado/settings/template.json
    mv pytornado/_plots/template_000/results_cp3D_*.png pytornado/example_plot.png
elif [[ "$1" == "clean" ]]; then
    rm -r "pytornado"
else
    echo "Wrong argument... Abort."
    exit 1
fi

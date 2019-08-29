#!/usr/bin/env bash

cd $(dirname $0)

if [[ "$1" == "make" ]]; then
    pytornado --make-example
elif [[ "$1" == "clean" ]]; then
    rm -r "pytornado"
else
    echo "Wrong argument... Abort."
    exit 1
fi

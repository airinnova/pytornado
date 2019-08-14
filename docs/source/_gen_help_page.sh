#!/usr/bin/env bash

cd $(dirname $0)
echo "Generating help page"

pytornado -h > user_guide/_help_page.txt

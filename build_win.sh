#!/bin/bash

set -e

# Tested on:
# Minimum python 3.8.10
# Minimum Windows 7

pip3 install -U pyinstaller==5.0.1

mkdir -p build/tmp
poetry export --without-hashes --format=requirements.txt > build/tmp/requrements.txt
pip3 install -U -r build/tmp/requrements.txt

#Actually python3 but in windows cmd named python
python py2exe.py
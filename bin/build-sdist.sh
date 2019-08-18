#!/usr/bin/env bash

/usr/bin/python3.6 -m venv env3.6
source env3.6/bin/activate
env3.6/bin/python -m pip install --upgrade setuptools wheel
env3.6/bin/python -m pip install -r requirements.txt
env3.6/bin/python setup.py build_ext --inplace
env3.6/bin/python setup.py sdist

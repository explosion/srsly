#!/bin/bash

if [ "${VIA}" == "compile" ]; then
  pip install -r requirements.txt
  python setup.py build_ext --inplace
  pip install -e .
fi


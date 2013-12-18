#!/bin/bash

echo Content-type: text/plain; charset=utf-8
echo

source INIT.sh
export PYTHON=$PYTHON3
export PYTHONPATH=$PYTHON3PATH
cd u
$PYTHON setChar.py

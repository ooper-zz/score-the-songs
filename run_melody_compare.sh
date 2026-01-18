#!/bin/bash
# Melody Comparison Tool Launcher

cd "$(dirname "$0")/singing_score_calculation"
../venv/bin/python melody_compare_simple.py

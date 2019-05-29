#!/usr/bin/env bash
source /home/erosita/sw/sass-setup.sh eSASSdevel

python create_simput.py
python efeds_sixte_simulator.py
python run_esass.py


#!/usr/bin/env bash
source activate transients
source /home/erosita/sw/sass-setup.sh eSASSdevel

python create_simput.py
python efeds_sixte_simulator.py
python prepare_event_files.py
python run_esass.py


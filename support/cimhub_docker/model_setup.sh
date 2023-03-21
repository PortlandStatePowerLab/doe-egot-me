#!/bin/bash
cd python_scripts/
python3 dss_x_y_coordinates.py
python3 create_ders_historical_data_input.py
python3 upload_psu_feeder.py -u
read -p "Press Enter to continue"


#!/bin/bash
cd python_scripts/
python3 create_ders_historical_data_input.py
python3 upload_model.py
read -p "Press Enter to continue"


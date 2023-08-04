#!/bin/bash

#cd derms_help_files
#python3 map_dcms_ders.py

cd DERScripts
echo "\n\n------------ UPLOADING MODEL ------------\n\n"
python3 upload_model.py
echo "\n\n------------ Initializing DER-EMs ------------\n\n"
bash inialize_DER_EMS.sh

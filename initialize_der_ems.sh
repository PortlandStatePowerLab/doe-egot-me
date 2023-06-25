#!/bin/bash
cd DERScripts
echo "\n\n------------ UPLOADING MODEL ------------\n\n"
python3 upload_model.py
echo "\n\n------------ Initializing DER-EMs ------------\n\n"
bash inialize_DER_EMS.sh

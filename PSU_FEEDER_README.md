# Introduction:

The ME is being constantly updated as we are putting the system together. The ME is being integrated with DERMS. Therefore, the current setup **may** change in the coming weeks. 

## Requirements:

- Download CIMHub module using the following command:
    - ```pip3 install cimhub```

## Upload PSU Feeder to Blazegraph:
- ```cd support/upload_model_to_blazegraph/```
- ```python3 upload_model.py```
    - The upload_mode.py script uploads the model, list measurements, and insert measurements.
    - There is no need to run DropDER or insert_DER scripts. The OpenDSS file already contains the required DERs and Non-DERs models.

# Important Note:
- The model is big and heavily loaded. So it takes time to run simulation and pull measurements from Blazegraph.
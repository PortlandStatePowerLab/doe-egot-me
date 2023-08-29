### **NOTE:**

**If this is the first time using the ME, read the README.md first. The following is not for first-time-users.**

# Introduction:

The ME is being constantly updated as we are putting the system together. The ME is being integrated with DERMS. Therefore, the current setup **may** change in the coming weeks. 

## Requirements:

- Download CIMHub module using the following command:
    - ```pip3 install cimhub```

# Model Overview:

The PSU Model contains 960 loads and 960 DERs. The backbone of the IEEE-13 Node Feeder is the same. However, from each bus, a set of transformers has been placed to step down the voltage to a residential level (240/120).

## **Base Model:**

Within the ME main directory, a folder named **dss_files** contains the base model in both dss format and xml format. The model is uploaded to blazegraph with only non-DER loads. Those are later converted into houses during the setup process. The non-DER loads are controlled internally using schedule profiles. The schedule profiles are pre-set and pre-configured by GridAPPS-D.

## **Modifying the Base Model:**
Modifying the Base model requires some OpenDSS knoweledge beforehand. The Base model contains 3-phase and two-phase buses. All the 3-phase buses start with the letter "n" and all the 2-phase buses start with "tlx".

**NOTE:**

Modifying the Base Model requires exporting a new XML file. Also, OpenDSS needs to be installed in your system. Once the required changes are applied to the Base Model, do the following:

- ```cd /dss_files/```
- Open the **cim_test.dss**
- The first line directs to the Base Model. Adjust the path to the **Master.dss** accordingly. Save the changes and exit.
- Run the **cim_test.dss** file as follows:
    - ```dss cim_test.dss``` Or ```opendsscmd cim_test.dss```

## **Setup:**

Before running a simulation, the model need to be set with DER-EMs and houses. The following steps will direct you toward setting up the Base model:

- ### **Edit the Simulation Configuration file:**
    - ```cd Configuration/```
    - Open **simulation_configuration.txt** and change the following to **True**:
        - "randomize_zipload_fractions": "True"
        - "use_houses": "True"

- ### **Upload PSU Feeder and Run PowerGrid API scripts:**

    - In the ME main directory, run the following:
        - ```./initialize_der_ems.sh```

- ### **To delete all feeder and only upload the PSU feeder to the Blazegraph**:
    - Edit the upload_model.py script and uncomment the remove_all_feeders() method.
        - ```cd DERScripts/```
        - Open upload_model.py
        - Within the main method, uncomment the following line:
            - ```feeder.remove_all_feeders()```

## **Insert 3-phase DERs into the model:**
As mentioned previously, 2-phase DERs are associated with all buses that start with "tlx". However, 3-Phase DERs are associated with buses that start with "n". Refer to **EGoT_der_psu.txt** for more information. 

To add 3-phase DER, do the following:
- ```cd DERScripts/```
- Open the **EGoT_der_psu.txt**.
- The first row is set as an example. Just make sure the buses start with "n" for all 3-Phase DERs.
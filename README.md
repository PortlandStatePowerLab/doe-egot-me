# EGoT-ME
##### Energy Grid of Things - Modeling Environment
##### Sean Keene -  seakeene@pdx.edu
##### Portland State University - Power Engineering Group

This repository contains the Modeling Environment for the EGoT project.

## Description

The ME is designed to simulate the effects of aggregated, dispatched DERs on the
energy grid. This is done by a DER aggregator or management system; for the EGoT
project, we will be using the Grid Service Provider, or GSP. The ME has the ability to
interface with physical DERs, emulators, or historical data via logs. Changes in these
DERs (i.e. due to a GSP dispatch) will affect changes in their electrical state.
These electrical changes are processed within simulated DERs (DER-S) and delivered to
their respectively assigned electrical model DERs (DER-EMs). These DER-EMs
are contained within a larger Electrical Distribution Model (EDM), which is 
itself contained within and driven by a Model Controller (MC). The EDM is 
implemented in GridAPPS-D for it's simulation and intercommunication capabilities;
the Model Controller is a class-based Python script expressly designed to be 
extensible and modifiable by the Test Engineer. The simulation will output grid states 
to logs as well as a simulated Grid Operator, which will be a simple decision-making 
class that takes the grid states, decides if a service should be requested, and sends 
a signal to the GSP, creating a closed feedback loop within the system.

Two DER-S types in development are: RWHDERS, a Resistive Water Heater DER-S, and 
DERSHistoricalDataInput, a historical data log processor. In the future,
new types of DERs can be implemented frictionlessly to the ME by development of
a new DER-S class for each one. As long as the DER-S produces electrical states and
provides identification and locational data, it can be directly introduced into the ME
without further modification to the modeling system.

## Contents

* **/Configuration/** Contains configuration files read in to the ME, such as the topology.
* **/DERScripts/** A set of scripts provided by PNNL's [CIMHub](https://github.com/GRIDAPPSD/CIMHub) project. These provide the "backend" for Initialise_DER_EMs.bat
* **/DERSHistoricalDataInputs/** Contains .csv input files used the Historical Data Input DER-S. Intended to be modified by the end user to provide custom DER inputs.
* **/Journal/**: Contains the LaTex files required to  generate the design journal, 
  main.pdf. auxil and out folders are also required for this. 
* **/Log Demos/**: Contains various .csv logs that are referenced in documentation or
elsewhere. These logs are for demonstration and not used by the system.
* **/Logged Grid State Data/** Simulation output logs providing timestamped measurements, grid states and amplifying data for the most recent simulation.
* **/Outputs to DERMS/** Contains the .xml file currently being used as the ME-DERMS API. 
* **/RWHDERS Inputs/** Contains input files for each DER managed by RWHDERS.
* **Initialise_DER_EMs.bat** A batch script that, when run, will automatically inject DER-EMs into the grid model based on the contents of DERScripts/EGoT13_der.txt (for example). 
* **manually_posted_service_input.xml** Contains data dictating when and what grid services will be manually posted. Since Grid Operator automatic operation is not currently supported, this is necessary for grid services to be requested in a test.
* **ModelController.py**: Contains the MC script.
* **Journal.pdf** is the design journal for this project, which is generally updated
  whenever an update is made to the system and pushed to this repository.
* **README.md** is this file.

## Background Documentation
* [Development Journal](https://github.com/PortlandStatePowerLab/doe-egot-me/blob/main/out/main.pdf)
* [Development Plan Documents (PEG only)](https://drive.google.com/drive/folders/1gzclY2N1w7PiS4PjuwpQj0qUheekqnkn?usp=sharing)
* [Flow Charts and other design documents (PEG only)](https://drive.google.com/drive/folders/13gm4Shm-kZ0PfSjn-9UMrA0cDD80fIy0?usp=sharing)
* [Estimated Quarterly Goals(Outdated)](https://www.overleaf.com/read/jrrvwgtvqryt)

## Important Links

* [GridAPPS-D Documentation](https://gridappsd.readthedocs.io/en/latest/using_gridappsd/index.html)
* [GridAPPS-D GitHub Repository](https://github.com/GRIDAPPSD)
# EGoT-ME
##### Energy Grid of Things - Modeling Environment
##### Sean Keene -  seakeene@pdx.edu
##### Portland State University - Power Engineering Group

NOTE: The following is out of date as of 8/18/2021. To be updated in the next few
days.

This repository contains the Modeling Environment for the EGoT project. The ME is
in the process of leaving the design phase and entering development.

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

* **Journal**: Contains the LaTex files required to  generate the design journal, 
  main.pdf. auxil and out folders are also required for this. 
* **Outdated**: Contains old test scripts, logs, and files that are no longer in use
* **ModelController.py**: Contains the MC script.
* **queries.txt** is a simple text file from PNNL containing numerous examples of
  sparql queries. 
* **Main.pdf** is the design journal for this project, which is generally updated
  whenever an update is made to the system and pushed to this repository.
* **README.md** is this file.

## Background Documentation

* [Development Plan Documents (PEG only)](https://drive.google.com/drive/folders/1gzclY2N1w7PiS4PjuwpQj0qUheekqnkn?usp=sharing)
* [Flow Charts and other design documents (PEG only)](https://drive.google.com/drive/folders/13gm4Shm-kZ0PfSjn-9UMrA0cDD80fIy0?usp=sharing)
* [Estimated Quarterly Goals(Outdated)](https://www.overleaf.com/read/jrrvwgtvqryt)

## Important Links

* [GridAPPS-D Documentation](https://gridappsd.readthedocs.io/en/latest/using_gridappsd/index.html)
* [GridAPPS-D GitHub Repository](https://github.com/GRIDAPPSD)
### Midrar Adham
### midrar@pdx.edu

Upload IEEE 13-Node Feeder to GridAPPS-D Blazegraph.

# Repository Structure:
This repository include the Modeling Environment and scripts that upload a customized IEEE 13-Node Feeder to GridAPPS-D Blazegraph.

# Requirements:
For developers, the following must be installed:
    1- GridLAB-D (minimum version is 4.3)
    2- OpenDSS (version 1.2.17 or less)
    3- CIMHub.
    4- Python 3.
For general use, you only need to have CIMHub installed.

# 
### **Note**:

This directory includes the OpenDSS software version 1.2.17. This version prepends "_" in the OpenDSS exported XML files. A symlink has been created to link the opendss binary file in this directory. Typing ```dss``` command in the terminal should run the older version of OpenDSS. Typing ```opendsscmd``` command should run the latest version of OpenDSS. 
# EGoT-ME
######Energy Grid of Things - Modeling Environment
######Sean Keene -  seakeene@pdx.edu
######Portland State University - Power Engineering Group

This repository contains the Modeling Environment for the EGoT project. The ME
is currently in an early development stage.

## Description

The ME is designed to simulate the effects of aggregated, dispatched DERs on the
energy grid. These DERs are aggregated and dispatched by a Grid Service Provider,
or GSP. The ME will eventually have the ability to recieve DER dispatch commands
from a GSP, or simulate them via external script or .csv input. These dispatches
will affect the DERs physically in certain ways which will be simulated
appropriately. The end result of these simulated DERs (DER-S) is an electrical
model of the DER (DER Electrical Distribution Model, or DER-EDM). This DER-EDM
is contained within a larger Electrical Distribution Model (EDM), which is 
itself contained within and driven by a Model Controller (MC). The MC will be
implemented in GridAPPS-D for it's simulation and intercommunication capabilities.
The simulation will output grid states to a simulated Grid Operator, which will
be a simple decision-making script that takes the grid states, decides if a service
should be requested, and sends a signal to the GSP, creating a closed feedback loop
within the system.

In the earliest stages, the DERs in question will be resistive water heaters due
to their simplicity and existing test data. Once the system is completed, however,
implementing new types of DERs will require only development of a DER-S for this
DER, after which it should integrate into the EDM without friction.

## Background Documentation

* [Development Plan Documents (PEG only)](https://drive.google.com/drive/folders/1gzclY2N1w7PiS4PjuwpQj0qUheekqnkn?usp=sharing)
* [Estimated Quarterly Goals](https://www.overleaf.com/read/jrrvwgtvqryt)

## Important Links

* [GridAPPS-D Documentation](https://gridappsd.readthedocs.io/en/latest/using_gridappsd/index.html)
* [GridAPPS-D GitHub Repository](https://github.com/GRIDAPPSD)
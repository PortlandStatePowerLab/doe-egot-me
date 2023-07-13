# Overview
This directory gives an introduction to how grid services are implemented within the Modeling Environment (ME). The EGoT project contains several entities that interact with each other mainly by using IEEE 2030.5. The ME does not deal with IEEE 2030.5 directly, however, the ME contains information that needs to be included when some entities start communicating.

# EGoT Entities of Interest:

The EGoT contains the following entities, where the highlighted entities are either within the ME or interact with the ME:

- **Grid Operator (GO)**
- Grid Service Provider
- **Distributed Energy Resource Management System (DERMS)**
- **Distributed Control Module (DCM)**
- Distributed Trust Module (DTM)

# Contents:
This folder contains mermaid diagrams to facilitate interactions between these entities. Note that the following entities are not implemented within the ME; they, however, interact with ME:
- **DERMS**
- **DCM**

# IEEE 2030.5 Resources:
A set of resources are used with each implemented grid service. These are for background information. All these resources are not used within the ME. Rather, they are used in the communication between DERMS and DCM.  In this Section, these resources are defined.
- **DERProgram:** is a program created to provide incentives for DERs that participate in grid services
- **DERControl:** is exposed by the DERProgram which in turn the client DER is managed by a single DERControl event.
- **DERCurve:** is associated with the DERProgram resource and contains several points that define a client DER behavior (i.e Volt/Var Control)
- **DERCapability:** exposes the DER capability as of its nameplate values.
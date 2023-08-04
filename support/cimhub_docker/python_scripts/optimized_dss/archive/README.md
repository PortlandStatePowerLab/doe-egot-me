#Progress Report:

The PSU 13-node feeder is this folder was optimized by eliminating the triplex lines between the trip nodes and the DERs. Each triplex node connects 8 DERs through 8 triplex lines. 

## Problem:

When the triplex lines between the triplex nodes and the DERs are eliminated, this means that each 8 DERs are directly connected to one triplex node. This is a problem because when the DER-EMs' magnitudes are updated, since they share the same bus, it will be hard to specify which DER is being updated. Thereforem this approach is no longer usefull.

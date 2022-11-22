Feature: DER-S

  @tpme1
  Scenario: DER01: The DER-S SHALL provide electrical data to the MC necessary to generate control inputs for the DER-EMs.
    Given DER-S inputs are available
    When A DER-S update occurs
    Then The Unified Input Request should indicate an input request in the proper format
    And The Unified Input Request should indicate an input request with the correct unique IDs and magnitudes.

  @tpme2 @problematic # This is a horrible requirement. Careful how we implement this one.
  Scenario: DER02: The DER-S SHALL have a configurable/reprogrammable API between external DER representations and itself.
    Given Output logs exist for two unique simulations
    And DER Inputs for each simulation were not identical
    Then The logs should indicate proper values for each input.

  @tpme1
  Scenario: DER03: The DER-S SHALL provide unique identifiers for its respective DERs.
    Given DER-S inputs are available
    When A DER-S update occurs
    Then The Unified Input Request should indicate an input request at the correct time
    And The Unified Input Request should indicate an input request with the correct unique IDs.

  @tpme1
  Scenario: DER04: The DER-S SHALL provide locational/topography information for its respective DERs.
    Given DER-S inputs are available
    When The DER-Ss configuration process occurs (as in simulation startup)
    Then Each DER-S should contain information associating a Unique ID with a locational identifier

#  @notdone @unrevised
#  Scenario: DER05: The DER-S SHOULD be able to receive physical DER states.
#    Given An API has been developed between the DER-S and a physical controller for a DER. A ME simulation is underway.
#    When The physical controller sends data to the DER-S.
#    Then The DER-S should produce an updated electrical representation of the physical DER as viewed by the terminal or in logs.
#
#  @notdone @unrevised
#  Scenario: DER06: The DER-S SHOULD be able to receive simulated or emulated DER states
#    Given An API has been developed between the DER-S and a DER emulator script. A ME simulation is underway.
#    When The script sends data to the DER-S.
#    Then The DER-S should produce an updated electrical representation of the simulated or emulated DER as viewed by the terminal or in logs.
#
#  @unrevised
#  Scenario: DER07: The DER-S SHOULD be able to receive data-represented DER states
#    Given An API has been developed between the DER-S and a file containing DER historical data. A ME simulation is underway.
#    When The DER-S reads the historical data file.
#    Then The DER-S should produce an updated electrical representation of the data-represented DER as viewed by the terminal or in logs.
#
#  @notdone @unrevised
#  Scenario: DER08: The DER-S MAY have the capability to receive direct control messages from a DERMS.
#    Given An API has been developed between the DER-S and a DERMS. A ME simulation is underway.
#    When The DERMS sends data to the DER-S.
#    Then The DER-S should produce an updated electrical representation of the DERMS message as viewed by the terminal or in logs.
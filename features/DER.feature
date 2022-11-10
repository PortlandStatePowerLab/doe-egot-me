Feature: DER-S

  @tpme1 @unrevised
  Scenario: DER01: The DER-S SHALL provide electrical data to the MC necessary to generate control inputs for the DER-EMs.
    Given A simulation is running which includes at least one DER-S
    When The DER-S receives updated DER states from an external source (such as an emulator, file, or physical system).
    Then The associated DER-EMs update to reflect the updated DER states as seen by the MC logs.

  @tpme2 @unrevised
  Scenario: DER02: The DER-S SHALL have a configurable/reprogrammable API between external DER representations and itself.
    Given A test is running which includes at least one DER-S.
    When A DER-S retrieves data from an external system, program or file.
    Then The DER-S produces an updated electrical representation of the DER as viewed by the terminal or in logs.

  @tpme1 @unrevised
  Scenario: DER03: The DER-S SHALL provide unique identifiers for its respective DERs.
    Given A test is running which includes at least one DER-S.
    When A DER-S retrieves data from an external system, program or file.
    Then Unique identifiers are provided to the assignment handler class representing each DER within each DER-S.

  @tpme1 @unrevised
  Scenario: DER04: The DER-S SHALL provide locational/topography information for its respective DERs.
    Given A test is running which includes at least one DER-S.
    When A DER-S retrieves data from an external system, program or file.
    Then Correct locational identifiers are provided to the assignment handler class representing each DER within each DER-S.

  @notdone @unrevised
  Scenario: DER05: The DER-S SHOULD be able to receive physical DER states.
    Given An API has been developed between the DER-S and a physical controller for a DER. A ME simulation is underway.
    When The physical controller sends data to the DER-S.
    Then The DER-S produces an updated electrical representation of the physical DER as viewed by the terminal or in logs.

  @notdone @unrevised
  Scenario: DER06: The DER-S SHOULD be able to receive simulated or emulated DER states
    Given An API has been developed between the DER-S and a DER emulator script. A ME simulation is underway.
    When The script sends data to the DER-S.
    Then The DER-S produces an updated electrical representation of the simulated or emulated DER as viewed by the terminal or in logs.

  @unrevised
  Scenario: DER07: The DER-S SHOULD be able to receive data-represented DER states
    Given An API has been developed between the DER-S and a file containing DER historical data. A ME simulation is underway.
    When The DER-S reads the historical data file.
    Then The DER-S produces an updated electrical representation of the data-represented DER as viewed by the terminal or in logs.

  @notdone @unrevised
  Scenario: DER08: The DER-S MAY have the capability to receive direct control messages from a DERMS.
    Given An API has been developed between the DER-S and a DERMS. A ME simulation is underway.
    When The DERMS sends data to the DER-S.
    Then The DER-S produces an updated electrical representation of the DERMS message as viewed by the terminal or in logs.
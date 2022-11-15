Feature: EDM

  @tpme1
  Scenario: EDM01: The EDM SHALL be implemented in GridAPPS-D.
    Given The Model Controller has completed the simulation startup process.
    Then A GridAPPS-D simulation object should be instantiated.

  @tpme2 @problematic # Not sure how to demonstrate this without modifying ME. Will return to it.
  Scenario: EDM02: The EDM SHALL include a database of grid models to be used in simulations.
    Given Output logs exist for two unique simulations
    Then Output logs should exist for two unique simulations


  @tpme1
  Scenario: EDM03: The EDM SHALL calculate new grid states at regular intervals.
    Given DER Input files exist
    And Logs from a simulation using these DER Input files exist
    Then Log files should indicate values update regularly at defined intervals.

  @tpme1
  Scenario: EDM04: The EDM SHALL provide a means for measuring electrical characteristics within the simulated grid model.
    Given Logs from a simulation exist
    Then Log files should indicate power and voltage readings exist for three phases of any bus.

  @tpme1
  Scenario: EDM05: The EDM SHALL have configurable start time and duration.
    Given The "Config.txt" file is available
    When The Model Controller runs a full simulation
    Then The simulation should start at the proper start time
    And The simulation should end at the proper end time (start time + duration)

  @tpme1
  Scenario: EDM06: The EDM SHALL include non-DER asset models.
    Given Logs from a simulation exist
    Then The logs should contain non-zero values for Voltage for a non-DER asset
    And The logs should contain non-zero values for Power for a non-DER asset

  @notdone @tpme1
  Scenario: EDM07: The EDM SHALL include DER-EMs that are generalizable to a variety of DER types (including loads, sources, and storage assets)
    Given DER Inputs exist which include a DER-EM that acts as a load, source, and storage
    And Logs from a simulation exist which use these inputs
    Then The logs should indicate the DER acted as a storage, load, and source.

  @tpme1
  Scenario: EDM08: The EDM SHALL have the capability to add DER-EMs to existing grid models.
    Given Logs from a simulation exist
    Then The logs should contain non-zero values for Voltage for a DER-EM
    And The logs should contain non-zero values for Power for a DER-EM

  @tpme1
  Scenario: EDM09: The EDM SHALL model an electrical distribution system including unbalanced components.
    Given Logs from a simulation exist
    Then The voltage values on each phase for a single load should not be exactly equal
    And The power values on each phase for a single load should not be exactly equal

  @tpme1
  Scenario: EDM10: The EDM SHALL provide a unique identifier to each DER-EM.
    Given DER Inputs are available
    When The DER assignment process is called
    Then The Assignment Lookup table should contain the name of each DER input
    And The Assignment Lookup Table should contain an mRID for each DER input
    And The mRID of each input in the Assignment Lookup Table should not be identical to any other input in the table.

  @tpme1
  Scenario: EDM11: The EDM SHALL store locational/topological data for each DER-EM for assignment purposes.
    Given DER Inputs are available
    When The DER assignment process is called
    Then The Assignment Lookup Table should contain the name of each DER input
    And Each DER-EM name should be associated with a locational identifier in the Assignment Lookup Table.
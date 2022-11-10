Feature: EDM

  @tpme1
  Scenario: EDM01: The EDM SHALL be implemented in GridAPPS-D.
    Given The Model Controller has completed the simulation startup process.
    Then A GridAPPS-D simulation object should be instantiated.

  @tpme2 @unrevised
  Scenario: EDM02: The EDM SHALL include a database of grid models to be used in simulations.
    Given The TE configured a simulation using a specific grid model from the database
    When The TE runs the simulation.
    Then Simulation logs should show measurements characteristic of the selected grid model.

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

  @tpme1 @unrevised
  Scenario: EDM08: The EDM SHALL have the capability to add DER-EMs to existing grid models.
    Given A grid model exists with the EDM’s model database.
    When The TE adds DER-EMs and measurement points to the model, and runs a simulation in which the DER-EMs are controlled.
    Then DER-EMs respond as expected per the controls used. This can be observed by the MC output logs.

  @tpme1 @unrevised
  Scenario: EDM09: The EDM SHALL model an electrical distribution system including unbalanced components.
    Given The TE has configured a simulation involving one or more unbalanced components within the model.
    When The TE executes the simulation.
    Then The measurements for each of a single component’s phases are logged. The values for each phase are not equal.

  @tpme1 @unrevised
  Scenario: EDM10: The EDM SHALL provide a unique identifier to each DER-EM.
    Given The TE has configured a simulation using one of the models within the EDM’s database. This model has one or more DER-EMs added.
    When The TE executes the simulation.
    Then The simulation generates output logs. Measurements for each DER-EM are displayed with a unique name.

  @tpme1 @unrevised
  Scenario: EDM11: The EDM SHALL store locational/topological data for each DER-EM for assignment purposes.
    Given The TE has configured a simulation including DER-EMs located on at least one bus.
    When The TE executes the simulation.
    Then The MC produces logs including measurements for each DER-EM. These measurements contain the locational identifier for each DER-EM.
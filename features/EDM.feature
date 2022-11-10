Feature: EDM

  Scenario: EDM01: The EDM SHALL be implemented in GridAPPS-D.
    Given A test is constructed using GridAPPS-D as the simulation platform.
    When The TE initiates the test.
    Then The test completes as expected.

  Scenario: EDM02: The EDM SHALL include a database of grid models to be used in simulations.
    Given The TE configured a simulation using a specific grid model from the database
    When The TE runs the simulation.
    Then Simulation logs show measurements characteristic of the selected grid model.

  Scenario: EDM03: The EDM SHALL calculate new grid states at regular intervals.
    Given A simulation is running.
    When Three seconds elapse.
    Then A new set of grid state measurements is sent to the callback method, which prints the measurements to the terminal using a test function.

  Scenario: EDM04: The EDM SHALL provide a means for measuring electrical characteristics within the simulated grid model.
    Given A simulation is running.
    When Three seconds elapse.
    Then A new set of grid state measurements is sent to the callback method, which prints the measurements to the terminal using a test function.

  Scenario: EDM05: The EDM SHALL have configurable start time and duration.
    Given The TE has configured a simulation to be executed representing a specific start time for a specified duration.
    When The TE begins the simulation.
    Then The simulation starts at the proper time and ends after the proper duration has elapsed. These times can be viewed by a test function in the EDMTimekeeper class which prints the simulation time every timestep.

  Scenario: EDM06: The EDM SHALL include non-DER asset models.
    Given The TE has configured a simulation to be executed using a grid model containing non-DER assets as well as measurement points for these assets.
    When The TE runs the simulation.
    Then Non-DER assets are shown in the measurements within the output logs. The measurements have reasonable values.

  @notdone
  Scenario: EDM07: The EDM SHALL include DER-EMs that are generalizable to a variety of DER types (including loads, sources, and storage assets)
    Given Create a BIS model that allows for load, source and storage behaviours.
    When TE runs a simulation including inputs which control the DER-EM in a manner that makes it act like a load, source, and a storage asset.
    Then The DER-EM responds like a load, a source, and a storage asset.

  Scenario: EDM08: The EDM SHALL have the capability to add DER-EMs to existing grid models.
    Given A grid model exists with the EDM’s model database.
    When The TE adds DER-EMs and measurement points to the model, and runs a simulation in which the DER-EMs are controlled.
    Then DER-EMs respond as expected per the controls used. This can be observed by the MC output logs.

  Scenario: EDM09: The EDM SHALL model an electrical distribution system including unbalanced components.
    Given The TE has configured a simulation involving one or more unbalanced components within the model.
    When The TE executes the simulation.
    Then The measurements for each of a single component’s phases are logged. The values for each phase are not equal.

  Scenario: EDM10: The EDM SHALL provide a unique identifier to each DER-EM.
    Given The TE has configured a simulation using one of the models within the EDM’s database. This model has one or more DER-EMs added.
    When The TE executes the simulation.
    Then The simulation generates output logs. Measurements for each DER-EM are displayed with a unique name.

  Scenario: EDM11: The EDM SHALL store locational/topological data for each DER-EM for assignment purposes.
    Given The TE has configured a simulation including DER-EMs located on at least one bus.
    When The TE executes the simulation.
    Then The MC produces logs including measurements for each DER-EM. These measurements contain the locational identifier for each DER-EM.
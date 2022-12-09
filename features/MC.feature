Feature: MC

  @notdone @tpme3 # GIGO. Will make do, suggest breaking down requirements like this in the future.
  Scenario: MC01: The MC SHALL coordinate simulations and input/output communications.
    When The EDMTimeKeeper on-timestep function is called
    And The EDMMeasurementProcessor measurement processing function is called
    Then On-timestep updates should occur
    And New processed measurements should be available
    And A new unified input request should be generated
    And The GOSensor should attempt to create a new GOPostedService object if applicable
    And GOOutputInterface should generate an output message

  @notdone @tpme1
  Scenario: MC02: The MC SHALL provide access to grid states data to the GO.
    Given The EDMMeasurementProcessor has received at least one set of measurements.
    Then The EDMMeasurementProcessor should provide measurements by a function call
    And The measurements should have human-readable names (not mRIDs).

  @notdone @tpme3/home/seanjkeene/PycharmProjects/doe-egot-melogtool
  Scenario: MC03: The MC SHALL provide input and output interfaces.
    Given DER-S inputs are available
    And A manually posted service input file is available
    When The DER-S input processing method is called
    And The GOSensor grid service request method is called
    Then The unified input request should update
    And The GO should output an XML file available for use by the GSP.

  @tpme1  # Requires extensive log parsing. Consider rewriting.
  Scenario: MC04: The MC SHALL recognize if DER-Ss have changed state since the prior timestep.
    Given Logs from a simulation exist
    Then The logs should indicate a DER-S changed state from one timestep to the next.

  @tpme1  @wip
  Scenario: MC05: The MC SHALL update DER-EMs as necessary.
    Given Logs from a simulation exist
    Then The logs should indicate a DER-S changed state from one timestep to the next.
    And The logs should indicate the DER-S updated at the right time in the input file.

  @tpme1 @unrevised @problematic # Not sure how to approach. Will come back to it.
  Scenario: MC06: The MC SHALL retrieve grid states data from the EDM at regular intervals.
    Given A ME simulation is running.
    When A measurement timestep--three seconds-- elapses.
    Then Measurements are placed in a dictionary in the EDMMeasurementProcessor class, which are then printed to the terminal by a test function.

  @tpme1
  Scenario: MC07: The MC SHALL use a defined time step size for coordination purposes.
    When The EDMTimeKeeper's on-timestep function is called
    Then Time is incremented by one second

  @tpme1
  Scenario: MC08: The MC SHALL provide an automated method to assign DER-EMs to DER-Ss (based on locational data.)
    Given DER-S inputs are available
    When The DER-S assignment process is called
    Then The DER association table contains keys for each input DER name
    And The DER association table contains mRIDs associated with each name

#  @unrevised
#  Scenario: MC09: The MC SHOULD produce and store timestamped logs of grid state and operational data.
#    Given The ME is configured; no DER-S or GO are required.
#    When The TE runs a simulation.
#    Then A timestamped output log is produced.
#
#  @unrevised
#  Scenario: MC10: The MC MAY have the ability to inform/alert the TE.
#    Given A simulation is running.
#    When One second elapses, causing the EDMTimeKeeper’s callback function to be called and incrementing the simulation timestep.
#    Then The MC prints a message to the terminal informing the TE of the current simulation timestep.
#
#  @unrevised
#  Scenario: MC11: The MC MAY have a closeout process.
#    Given A simulation is running.
#    When The configured simulation duration elapses, and the simulation end message is provided to the EDMTimeKeeper by the GridAPPS-D log topic.
#    Then A test message is printed to the terminal informing the TE that the simulation has completed. The program closes without error.
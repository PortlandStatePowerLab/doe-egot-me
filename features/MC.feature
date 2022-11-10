Feature: MC

  @notdone @tpme3 @unrevised
  Scenario: MC01: The MC SHALL coordinate simulations and input/output communications.
    Given The TE has configured a simulation including DER-EMs, at least one DER-S input, and both logs and output to a DERMS via the GO-DERMS API. The DERMS is running and awaiting messages.
    When The TE executes the simulation.
    Then The simulation runs successfully without errors. Inputs from the DER-S are reflected in the DER-EMs as demonstrated by output logs. Messages from the GO to the DERMS are delivered properly as confirmed by the DERMS.

  @notdone @tpme1 @unrevised
  Scenario: MC02: The MC SHALL provide access to grid states data to the GO.
    Given The ME is performing a simulation.
    When The timekeeper calls an accessor method to assign grid states from the measurement processor to the GO’s grid state buffer.
    Then The GO’s grid state buffer contains the most recent grid state measurements. These measurements are printed to the terminal by a test function.

  @notdone @tpme3 @unrevised
  Scenario: MC03: The MC SHALL provide input and output interfaces.
    Given A simulation is running in which both the DER-S and GO-GSP interfaces are needed.
    When On startup, the MC attempts to connect to external resources via the input and output interfaces.
    Then A DER-S successfully connects to its DER resource, and the GO successfully connects to the DERMS.

  @tpme1 @unrevised
  Scenario: MC04: The MC SHALL recognize if DER-Ss have changed state since the prior timestep.
    Given A test is running involving a DER-S. The DER-S state has changed since the previous simulation timestep.
    When One second elapses. The simulation time step increments, calling the once-per-timestep encapsulation method.
    Then The input processor creates an input message for the EDM and sends it; this message is printed to the terminal for test purposes.

  @tpme1 @unrevised
  Scenario: MC05: The MC SHALL update DER-EMs as necessary.
    Given A test is running involving a DER-S and DER-EMs. The DER-S state has changed since the previous simulation timestep.
    When The input processor creates an input message for the EDM and sends it.
    Then The DER-EMs update to reflect the new grid states as demonstrated by new measurement values at the proper time in the simulation output logs.

  @tpme1 @unrevised
  Scenario: MC06: The MC SHALL retrieve grid states data from the EDM at regular intervals.
    Given A ME simulation is running.
    When A measurement timestep--three seconds-- elapses.
    Then Measurements are placed in a dictionary in the EDMMeasurementProcessor class, which are then printed to the terminal by a test function.

  @tpme1 @unrevised
  Scenario: MC07: The MC SHALL use a defined time step size for coordination purposes.
    Given A simulation is running.
    When One second elapses.
    Then The EDMTimeKeeper’s coordination method is called, as determined by a message being printed to the terminal once per second by a test function.

  @tpme1 @unrevised
  Scenario: MC08: The MC SHALL provide an automated method to assign DER-EMs to DER-Ss (based on locational data.)
    Given The TE has configured a test and begun execution. The ME is undergoing the simulation startup process.
    When Each DER-S retrieves or provides locational data to the MC.
    Then Each input DER from each DER-S is assigned and associated with a DER-EM, the results of which are sent to the measurement processor for logging. The processed measurements with locational and association data are delivered to the MCOutputLog class.Logs are generated containing said data.

  @unrevised
  Scenario: MC09: The MC SHOULD produce and store timestamped logs of grid state and operational data.
    Given The ME is configured; no DER-S or GO are required.
    When The TE runs a simulation.
    Then A timestamped output log is produced.

  @unrevised
  Scenario: MC10: The MC MAY have the ability to inform/alert the TE.
    Given A simulation is running.
    When One second elapses, causing the EDMTimeKeeper’s callback function to be called and incrementing the simulation timestep.
    Then The MC prints a message to the terminal informing the TE of the current simulation timestep.

  @unrevised
  Scenario: MC11: The MC MAY have a closeout process.
    Given A simulation is running.
    When The configured simulation duration elapses, and the simulation end message is provided to the EDMTimeKeeper by the GridAPPS-D log topic.
    Then A test message is printed to the terminal informing the TE that the simulation has completed. The program closes without error.
Feature: GO

  @notdone
  Scenario: GO01: The GO SHOULD have awareness of EDM grid model states.
    Given A ME simulation is running, in which a set of measurements has already been provided to the measurement processor. Per-timestep actions are being performed according to the timekeeper class.
    When The timekeeper uses the measurement processor’s accessor method to send grid states to the GO class.
    Then The GO prints the grid states to the terminal using a test function.

  @notdone
  Scenario: GO02: The GO SHOULD determine an appropriate grid service based on system state data from the EDM.
    Given A test is being executed.
    When Grid states are sent to the GO class.
    Then Grid service requests are generated by the GO class and printed to the terminal via a test function.

  @notdone
  Scenario: GO03: The GO SHALL have an API between itself and the DERMS.
    Given The TE has configured a simulation in which a GO-DERMS connection is required. The DERMS is online and awaiting communications from the GO.
    When The TE executes the simulation.
    Then The GO is able to connect to the DERMS and send and receive data as expected. The simulation completes without error.

  @notdone
  Scenario: GO04: The GO SHALL be able to request grid services from the DERMS.
    Given A test is underway. GO-DERMS communications have been established.
    When A grid service request decision is made by the GO sensor class (either manually or automatically).
    Then A message in the proper format is sent to the DERMS.

  Scenario: GO05: The GO SHALL provide a method to permit the TE to request grid services.
    Given A test is underway. The TE has flagged the GO to manually request a particular grid service at a particular time.
    When The timekeeper calls the GO’s manual decision making method at the proper time.
    Then A manual grid service request is generated and sent to the API.


  @notdone
  Scenario: GO06: The GO SHOULD provide feedback data to the DERMS.
    Given A ME test is underway. GO-GSP communications are established.
    When Feedback data is provided to the GO sensor class by the measurement processor.
    Then Feedback data is provided to the DERMS by the GO API class within a formatted message.


  @notdone
  Scenario: GO07: The GO MAY alert the MC if it loses communication with a DERMS.
    Given The ME is performing a test involving an open connection between the GO and DERMS.
    When The connection between the GO and DERMS is broken.
    Then A message is printed to the terminal informing the TE about the broken connection.




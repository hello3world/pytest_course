Feature: Worker

    Scenario: Create a worker with basic attributes
        Given a worker named "John" with salary 100 and 40 hours per week
        Then the worker name should be John
        And the worker salary should be 100

    Scenario: Calculate annual salary
        Given a worker named "John" with salary 100 and 40 hours per week
        When I calculate the worker annual salary
        Then the annual salary should be 192000

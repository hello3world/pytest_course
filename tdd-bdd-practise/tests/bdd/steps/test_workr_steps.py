import pytest
from pytest_bdd import given, when, then, parsers
from src.worker import Worker 


@pytest.fixture
def context():
    return {}

@given(
    parsers.parse(
        'a worker named "{name}" with salary {salary:d} and {hours_per_week:d}'
    ),
    target_fixture="worker_data",
)
def worker_data(name: str, salary: int, hours_per_week: int):
    return {
        "worker": Worker(name=name, salary_per_hour=salary, hours_per_week=hours_per_week)
    }

@then(parsers.parse('the worker name should be "{expected_name}"'))
def worker_name_should_be(worker_data, expected_name: str):
    assert worker_data["worker"].name == expected_name

@then(parsers.parse("the worker salary should be {expected_salary:d}"))
def worker_salary_should_be(worker_data, expected_salary: int):
    assert worker_data["worker"].salary == expected_salary

@when("I calculate the worker annual salary")
def calculate_annual_salary(worker_data):
    worker_data["annual_salary"] = worker_data["worker"].get_annual_salary()
    
@then(parsers.parse("the worker annual salary should be {expected_annual_salary:d}"))
def worker_annual_salary_should_be(worker_data, expected_annual_salary: int):
    assert worker_data["annual_salary"] == expected_annual_salary
    
# pytest -v --gherkin-terminal-reporter
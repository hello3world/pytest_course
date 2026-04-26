from src.worker import Worker

def test_worker_init():
    worker = Worker(name='John', salary=100, hours_per_week=40)
    assert worker.name == 'John'
    assert worker.salary == 100
    assert worker.hours_per_week == 40

def test_calculate_annual_salary():
    worker = Worker(name='John', salary=100, hours_per_week=40)
    annual_salary = worker.get_annual_salary()
    assert annual_salary == 100 * 40 * 4 * 12
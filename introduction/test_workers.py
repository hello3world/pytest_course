from worker import Worker


def test_worker():
    worker = Worker(name="John", salary=1000, work_hours=40)
    assert worker.salary == 1000
    assert worker.work_hours == 40
    expected_salary = 1000 * 40 * 12
    assert worker.get_annual_salary() == expected_salary

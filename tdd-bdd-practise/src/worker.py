class Worker:
    def __init__(self, name: str, salary: int | float, hours_per_week: int | float):
        self.name = name
        self.salary = salary
        self.hours_per_week = hours_per_week

    def get_annual_salary(self):
        annual_salary = self.salary * self.hours_per_week * 4 * 12
        return annual_salary
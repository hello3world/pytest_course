class Worker:
    def __init__(self, name: str, salary: float, work_hours: float):
        self.name = name
        self.salary = salary
        self.work_hours = work_hours
        
    def get_annual_salary(self) -> float:
        return self.salary * self.work_hours * 12
    
    def get_name(self) -> str:
        return self.name
    
    def get_salary(self) -> float:
        return self.salary
    
    def get_work_hours(self) -> float:
        return self.work_hours

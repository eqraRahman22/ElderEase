# Strategy Pattern Implementation
# This allows us to change how schedules are assigned without changing the core scheduling logic.

from abc import ABC, abstractmethod
from .models import ElderlyProfile, CareSchedule

class ScheduleStrategy(ABC):
    @abstractmethod
    def get_schedules(self):
        pass

class AllSchedulesStrategy(ScheduleStrategy):
    def get_schedules(self):
        return CareSchedule.objects.all()

class LocationBasedStrategy(ScheduleStrategy):
    def __init__(self, location):
        self.location = location

    def get_schedules(self):
        return CareSchedule.objects.filter(location__icontains=self.location)

class RateBasedStrategy(ScheduleStrategy):
    def __init__(self, max_rate):
        self.max_rate = max_rate

    def get_schedules(self):
        return CareSchedule.objects.filter(hourly_rate__lte=self.max_rate)

from solution.ConsumerTypes.MachineConsumer import MachineConsumer
from dataclasses import dataclass
WATER_CTH_J  = 4180#J/K/kg
WATER_CTH_WH = WATER_CTH_J / 3600 #Wh/K/kg
BASE_TEMP    = 283 #10 °C
END_TEMP     = 333 #60° C
class ECSConsumer(MachineConsumer):
    power          : int
    volume         : int
    def __init__(self, id, profile, start_time, end_time, power, volume):
        super().__init__(id, profile, start_time, end_time, 1)
        self.power = power
        self.volume = volume
    def get_total_duration(self) -> int:
        #returns the total duration of a heating cycle
        return int(3600 * (END_TEMP - BASE_TEMP) * self.volume * WATER_CTH_WH / self.power)
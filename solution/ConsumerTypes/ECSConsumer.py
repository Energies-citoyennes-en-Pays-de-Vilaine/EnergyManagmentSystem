from solution.ConsumerTypes.MachineConsumer import MachineConsumer
from dataclasses import dataclass
WATER_CTH_J  = 4180#J/K/kg
WATER_CTH_WH = WATER_CTH_J / 3600 #Wh/K/kg
BASE_TEMP    = 283 #10 °C
END_TEMP     = 333 #60° C
class ECSConsumer(MachineConsumer):
    power          : int
    volume         : int
    def __init__(self, id, profile, start_time, end_time, power, volume, consumer_machine_type=-1):
        super().__init__(id=id, profile=profile, start_time=start_time, end_time=end_time, machine_count=1, consumer_machine_type=consumer_machine_type)
        self.power = power
        self.volume = volume
    def __repr__(self):
        to_return = "ECSConsumer("
        to_return += f"id={self.id},"
        to_return += f"profile={self.profile},"
        to_return += f"start_time={self.start_time},"
        to_return += f"end_time={self.end_time},"
        to_return += f"power={self.power},"
        to_return += f"volume={self.volume},"
        to_return += f"consumer_machine_type={self.consumer_machine_type},"
        to_return += ")"
        return to_return
    def get_total_duration(self) -> int:
        #returns the total duration of a heating cycle
        return int(3600 * (END_TEMP - BASE_TEMP) * self.volume * WATER_CTH_WH / self.power)
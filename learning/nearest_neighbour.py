from typing import List
import numpy as np
from solution.Utils.utils import mini, maxi
    
class windTurbineDataPoint():
    direction_deg : int
    wind_speed_km_per_h : float
    temperature_k : int

class windTurbineData():
    points : windTurbineDataPoint
    def load_from_file(self):
        pass
class nnWeigths():
    direction : float
    speed : float
    temperature : float
    
def get_distance(p1 : windTurbineDataPoint, p2 : windTurbineDataPoint, coeffs : nnWeigths) -> float:
    deg_mini = mini(p1.direction_deg, p2.direction_deg)
    deg_maxi = maxi(p1.direction_deg, p2.direction_deg)
    deg_distance = mini((deg_maxi - deg_mini) ** 2, (deg_mini + 360 - deg_maxi) ** 2)
    temp_distance = (p1.temperature_k - p2.temperature_k) ** 2
    speed_distance = (p1.wind_speed_km_per_h - p2.wind_speed_km_per_h) ** 2
    return deg_distance * coeffs.direction + temp_distance * coeffs.temperature + speed_distance * coeffs.speed



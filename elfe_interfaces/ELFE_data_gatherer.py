from learning.database.ELFE_db_types import ELFE_BallonECS, ELFE_BallonECSHeuresCreuses, ELFE_ChauffageAsservi, ELFE_ChauffageAsserviModeleThermique, ELFE_ChauffageNonAsservi, ELFE_EquipementPilote, ELFE_MachineGenerique, ELFE_MachineGeneriqueCycle, ELFE_VehiculeElectriqueGenerique
from learning.database.ELFE_db_creator import ELFE_database_names
from learning.database.EMS_db_types import EMSCycle, EMSCycleData, EMSDeviceTemperatureData, EMSMachineData, EMSPowerCurveData, InitialWheatherForecast
from learning.database.EMS_db_creator import execute_queries, fetch
from credentials.db_credentials import db_credentials
from typing import List, Union
from solution.ConsumerTypes.HeaterConsumer import HeaterConsumer
from solution.ConsumerTypes.SumConsumer import SumConsumer
from solution.ConsumerTypes.MachineConsumer import MachineConsumer
MODE_PILOTE = 30
ELFE_MachineGenerique.timestamp_de_fin_souhaite
def get_machines(timestamp) -> List[MachineConsumer]:
	to_return : List[MachineConsumer]= []
	machines_to_schedule = fetch(db_credentials["ELFE"], f" SELECT machine.mesures_puissance_elec_id, machine.delai_attente_maximale_apres_fin, machine.timestamp_de_fin_souhaite "
													   + f" FROM {ELFE_database_names['ELFE_MachineGenerique']} AS machine" 
	                                                   + f" INNER JOIN {ELFE_database_names['ELFE_MachineGeneriqueCycle']} AS cycle ON cycle.cycle_equipement_pilote_machine_generique_id = machine.id " 
													   + f" INNER JOIN {ELFE_database_names['ELFE_EquipementPilote']} AS equipement ON machine.equipement_pilote_id = equipement.id "
													   + f" WHERE equipement.mode = {MODE_PILOTE};")
	pass


from credentials.db_credentials import db_credentials
from learning.database.EMS_db_creator import execute_queries
from learning.database.ELFE_db_types import ELFE_BallonECS, ELFE_BallonECSHeuresCreuses, ELFE_ChauffageAsservi, ELFE_ChauffageNonAsservi ,ELFE_ChauffageAsserviModeleThermique, ELFE_EquipementPilote, ELFE_MachineGenerique, ELFE_MachineGeneriqueCycle, ELFE_VehiculeElectriqueGenerique

ELFE_database_names = {
	"ELFE_BallonECS"                       : "equipement_pilote_ballon_ecs",
	"ELFE_BallonECSHeuresCreuses"          : "equipement_pilote_ballon_ecs_heures_creuses",
	"ELFE_ChauffageAsservi"                : "equipement_pilote_chauffage_asservi",
	"ELFE_ChauffageAsserviModeleThermique" : "chauffage_asservi_modele_thermique",
	"ELFE_ChauffageNonAsservi"             : "equipement_pilote_chauffage_non_asservi",
	"ELFE_EquipementPilote"                : "equipement_pilote_ou_mesure",
	"ELFE_MachineGenerique"                : "equipement_pilote_machine_generique",
	"ELFE_MachineGeneriqueCycle"           : "equipement_pilote_machine_generique_cycle",
	"ELFE_VehiculeElectriqueGenerique"     : "equipement_pilote_vehicule_electrique_generique",
}

def create_tables(credentials):
	tables_queries = [
		ELFE_BallonECS                      .get_create_table_str(ELFE_database_names["ELFE_BallonECS"                       ]),
		ELFE_BallonECSHeuresCreuses         .get_create_table_str(ELFE_database_names["ELFE_BallonECSHeuresCreuses"          ]),
		ELFE_ChauffageAsservi               .get_create_table_str(ELFE_database_names["ELFE_ChauffageAsservi"                ]),
		ELFE_ChauffageAsserviModeleThermique.get_create_table_str(ELFE_database_names["ELFE_ChauffageAsserviModeleThermique" ]),
		ELFE_ChauffageNonAsservi            .get_create_table_str(ELFE_database_names["ELFE_ChauffageNonAsservi"             ]),
		ELFE_EquipementPilote               .get_create_table_str(ELFE_database_names["ELFE_EquipementPilote"                ]),
		ELFE_MachineGenerique               .get_create_table_str(ELFE_database_names["ELFE_MachineGenerique"                ]),
		ELFE_MachineGeneriqueCycle          .get_create_table_str(ELFE_database_names["ELFE_MachineGeneriqueCycle"           ]),
		ELFE_VehiculeElectriqueGenerique    .get_create_table_str(ELFE_database_names["ELFE_VehiculeElectriqueGenerique"     ]),
	]
	execute_queries(credentials, tables_queries)

if __name__ == "__main__":
	create_tables(db_credentials["ELFE"])
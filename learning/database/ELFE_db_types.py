from learning.database.EMS_db_types import DBAnnotation, serializableThroughDatabase, PrimaryAutoInt
from dataclasses import dataclass

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_EquipementPilote():
	Id                                  : PrimaryAutoInt
	equipement_pilote_specifique_id     : int
	equipement_pilote_ou_mesure_type_id : int
	equipement_pilote_ou_mesure_mode    : int
	etat_controle                       : int
	etat_commande                       : int
	nom                                 : str
	description                         : str
	typologie_installation_domotique    : int
	ems_consigne_marche                 : bool

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_ChauffageAsserviModeleThermique():
	Id 	        : PrimaryAutoInt
	nom         : str
	description : str

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_ChauffageAsservi():
	Id                                         : PrimaryAutoInt
	equipement_pilote_ou_mesure_id             : int
	temperature_eco                            : int
	temperature_confort                        : int
	prog_semaine_periode_1_confort_actif       : bool
	prog_semaine_periode_1_confort_heure_debut : int
	prog_semaine_periode_1_confort_heure_fin   : int
	prog_semaine_periode_2_confort_actif       : bool
	prog_semaine_periode_2_confort_heure_debut : int
	prog_semaine_periode_2_confort_heure_fin   : int
	prog_weekend_periode_1_confort_actif       : bool
	prog_weekend_periode_1_confort_heure_debut : int
	prog_weekend_periode_1_confort_heure_fin   : int
	prog_weekend_periode_2_confort_actif       : bool
	prog_weekend_periode_2_confort_heure_debut : int
	prog_weekend_periode_2_confort_heure_fin   : int
	delta_temp_maximale_temp_demandee          : int
	puissance                                  : int
	modele_thermique_id                        : int
	mesures_puissance_elec_id                   : int
	mesure_temperature_id                      : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_ChauffageNonAsservi():
	Id                                         : PrimaryAutoInt
	equipement_pilote_ou_mesure_id             : int
	prog_semaine_periode_1_confort_actif       : bool
	prog_semaine_periode_1_confort_heure_debut : int
	prog_semaine_periode_1_confort_heure_fin   : int
	prog_semaine_periode_2_confort_actif       : bool
	prog_semaine_periode_2_confort_heure_debut : int
	prog_semaine_periode_2_confort_heure_fin   : int
	prog_weekend_periode_1_confort_actif       : bool
	prog_weekend_periode_1_confort_heure_debut : int
	prog_weekend_periode_1_confort_heure_fin   : int
	prog_weekend_periode_2_confort_actif       : bool
	prog_weekend_periode_2_confort_heure_debut : int
	prog_weekend_periode_2_confort_heure_fin   : int
	puissance_moyenne_eco                      : int
	puissance_moyenne_confort                  : int
	pourcentage_eco_force                      : int
	mesures_puissance_elec                     : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_MachineGenerique():
	Id                                           : PrimaryAutoInt
	equipement_pilote_ou_mesure_id               : int
	timestamp_de_fin_souhaite                    : int
	delai_attente_maximale_apres_fin             : int
	cycle_equipement_pilote_machine_generique_id : int
	mesures_puissance_elec_id                    : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_VehiculeElectriqueGenerique():
	Id                                           : PrimaryAutoInt
	equipement_pilote_ou_mesure_id               : int
	pourcentage_charge_restant                   : int
	pourcentage_charge_finale_minimale_souhaitee : int
	duree_de_charge_estime                       : int
	timestamp_dispo_souhaitee                    : int
	puissance_de_charge                          : int
	capacite_de_batterie                         : int
	mesures_puissance_elec                       : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_MachineGeneriqueCycle():
	Id                                     : PrimaryAutoInt
	equipement_pilote_machine_generique_id : int
	duree_cycle                            : int
	nom                                    : str
	description                            : str

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_BallonECS():
	Id                             : PrimaryAutoInt
	equipement_pilote_ou_mesure_id : int
	volume_ballon                  : int
	puissance_chauffe              : int
	mesures_puissance_elec_id      : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class ELFE_BallonECSHeuresCreuses():
	Id                              : PrimaryAutoInt
	equipement_pilote_ballon_ecs_id : int
	nom                             : int
	description                     : int
	actif                           : bool
	debut                           : int
	fin                             : int
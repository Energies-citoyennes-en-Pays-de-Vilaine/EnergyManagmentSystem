from credentials.db_credentials import db_credentials
from learning.database.EMS_db_creator import execute_queries
from learning.database.history_db_types import history_Model, history_Curve, history_Prediction

history_database_names = {
	"history_Model"      : "history_model",
	"history_Curve"      : "history_curve",
	"history_Prediction" : "history_Prediction"
}
history_model_dictionnary = {
	"currently_in_use" : 0,
	"persistance"      : 1
}

history_curve_dictionnary = {
	"general_P_C" : 0
}

def create_tables(credentials):
	tables_queries = [
		history_Model     .get_create_table_str(history_database_names["history_Model"     ]),
		history_Curve     .get_create_table_str(history_database_names["history_Curve"     ]),
		history_Prediction.get_create_table_str(history_database_names["history_Prediction"]),
	]
	execute_queries(credentials, tables_queries)
	models = []
	curves = []
	for model_key in history_model_dictionnary:
		models.append(history_Model(history_model_dictionnary[model_key], model_key))
	for curve_key in history_curve_dictionnary:
		curves.append(history_Curve(history_curve_dictionnary[curve_key], curve_key))
	queries = []
	for model in models:
		queries.append(model.get_create_or_update_in_table_str(history_database_names["history_Model"]))
	for curve in curves:
		queries.append(curve.get_create_or_update_in_table_str(history_database_names["history_Curve"]))
	execute_queries(credentials, queries)

if __name__ == "__main__":
	create_tables(db_credentials["EMS"])
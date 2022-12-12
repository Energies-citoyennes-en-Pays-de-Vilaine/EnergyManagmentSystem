import shutil
import os
from datetime import datetime
from learning.database.EMS_db_creator import fetch
from credentials.db_credentials import db_credentials
TIME_KEEP=3600
FOLDER = "data/in_use"
if __name__ == "__main__":
	in_use_files = os.listdir(FOLDER)
	in_use_files = list(filter(lambda x: x != 'default.csv', in_use_files))
	current_timestamp = datetime.now().timestamp()
	finish_time_move = int(current_timestamp - TIME_KEEP)
	query = (f"SELECT csv FROM cycledata WHERE csv IN ({', '.join(['%s' for i in in_use_files])}) AND moved_timestamp != 0 AND moved_timestamp < %s;" , in_use_files + [finish_time_move])

	to_delete = fetch(db_credentials["EMS"], query)
	for to_delete_tuple in to_delete:
		to_delete_file = f"{FOLDER}/{to_delete_tuple[0]}"
		print(f"deleting {to_delete_file}")
		os.remove(to_delete_file)
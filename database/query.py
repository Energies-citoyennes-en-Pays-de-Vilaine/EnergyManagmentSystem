import psycopg2
def execute_queries(credentials, queries):
	cred = credentials
	try:
		if "options" not in cred:
			cred["options"] = ""
		connection = psycopg2.connect(host = cred["host"], database = cred["database"], user = cred["user"], password = cred["password"], options=cred["options"])
		cursor = connection.cursor()
		for query in queries:
			if (isinstance(query, str)):
				cursor.execute(query)
			else:
				cursor.execute(query[0], query[1])
		# close communication with the PostgreSQL database server
		cursor.close()
		# commit the changes
		connection.commit()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if connection is not None:
			connection.close()
			
def fetch(credentials, query):
	cred = credentials
	result = None
	try:
		if "options" not in cred:
			cred["options"] = ""
		connection = psycopg2.connect(host = cred["host"], database = cred["database"], user = cred["user"], password = cred["password"], options=cred["options"])
		cursor = connection.cursor()
		if (isinstance(query, str)):
			cursor.execute(query)
		else:
			cursor.execute(query[0], query[1])
		result = cursor.fetchall()
		cursor.close()
		# commit the changes
		connection.commit()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if connection is not None:
			connection.close()	
	return result		
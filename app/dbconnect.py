import MySQLdb

def connection():
	conn = MySQLdb.connect(host="localhost",
							user = "root",
							passwd = "test123",
							db = "buzzbee")
	c = conn.cursor()

	return c, conn
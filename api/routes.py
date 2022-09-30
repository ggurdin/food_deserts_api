from api import app
from flask import request
import json
import os
import pymysql
from dotenv import load_dotenv


if os.environ.get('GAE_ENV') == 'standard':
	db_user = os.environ.get('DB_USER')
	db_password = os.environ.get('DB_PASS')
	db_name = os.environ.get('DB_NAME')
	db_connection_name = os.environ.get('DB_CONNECTION')
	db_host = os.environ.get('DB_HOST')
	unix_socket = '/cloudsql/{}'.format(db_connection_name)
	cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name)

else:
	load_dotenv()
	db_user = os.environ.get('DB_USER')
	db_password = os.environ.get('DB_PASS')
	db_name = os.environ.get('DB_NAME')
	db_host = os.environ.get('DB_HOST')
	cnx = pymysql.connect(user=db_user, password=db_password, host=db_host, db=db_name)


@app.route("/")
def index():
	return "Index"

@app.route("/api/counties")
def counties():
	with cnx.cursor() as cursor:
		cursor.execute("SELECT DISTINCT county FROM tract_demographics;")
		result = cursor.fetchall()
		ret = json.dumps({"counties": [x[0] for x in result]})
		cnx.close()
	return ret

@app.route("/api/demographic_info")
def demographics():
	county = request.args['county'].lower()
	with cnx.cursor() as cursor:
		cursor.execute("SELECT DISTINCT county FROM tract_demographics;")
		result = cursor.fetchall()
		counties = [x[0].lower() for x in result]
		if county in counties:
			county_data_sql = f"SELECT tract_id, low_income, proverty_rate, median_family_income, population_2010 FROM tract_demographics WHERE LOWER(county) LIKE '{county}';"
			cursor.execute(county_data_sql)
			result = cursor.fetchall()
			ret = {"county_data": []}
			for x in result:
				ret["county_data"].append({"census_tract": x[0], "low_income": x[1], "proverty_rate": x[2], "median_family_income": x[3], "population_2010": x[4]})
			return json.dumps(ret)
		else:
			return json.dumps({"status": "not found"})
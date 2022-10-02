from api import app
from flask import request
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

@app.route("/<type>/")
def urban(type):
	if type not in ["urban", "rural"]:
		return {"status": "not found"}
	county = None
	if "county" in request.args:
		county = request.args["county"].lower()
	type_flag = 0
	if type == "urban":
		type_flag = 1
	with cnx.cursor() as cursor:
		sql = f"SELECT tract_id FROM food_desert_data WHERE is_urban = {type_flag}"
		if county:
			sql = sql + f' AND county = "{county}"'
		cursor.execute(sql)
		ret = cursor.fetchall()
		tract_ids = {"tracts": [x[0] for x in ret]}
	return tract_ids

@app.route("/low_income/")
def low_income():
	county = None
	if "county" in request.args:
		county = request.args["county"].lower()
	with cnx.cursor() as cursor:
		sql = "SELECT tract_id FROM food_desert_data WHERE low_income = 1"
		if county:
			sql = sql + f' AND LOWER(county) LIKE "{county}";'
		print(sql)
		cursor.execute(sql)
		ret = cursor.fetchall()
		tract_ids = {"tracts": [x[0] for x in ret]}
	return tract_ids

@app.route("/<lila>/<distance>/")
def li_distance(lila, distance):
	if lila not in ["low_income", "low_access"]:
		return {"status": "not found"}
	county = None
	if "county" in request.args:
		county = request.args["county"].lower()
	if distance not in ["half_mile", "one_mile", "ten_miles", "twenty_miles"]:
		return {"status": "not found"}
	with cnx.cursor() as cursor:
		sql = f"SELECT tract_id FROM food_desert_data WHERE la_{distance} = 1"
		if lila == "low_income":
			sql = sql + " AND low_income = 1"
		if county:
			sql = sql + f' AND county LIKE "{county}"'
		cursor.execute(sql)
		ret = cursor.fetchall()
		tract_ids = {"tracts": [x[0] for x in ret]}
	return tract_ids

@app.route("/<lila>/vehicle")
def li_vehicle(lila):
	if lila not in ["low_income", "low_access"]:
		return {"status": "not found"}
	county = None
	if "county" in request.args:
		county = request.args["county"].lower()
	with cnx.cursor() as cursor:
		sql = f"SELECT tract_id FROM food_desert_data WHERE low_vehicle_access = 1"
		if lila == "low_income":
			sql = sql + " AND low_income = 1"
		if county:
			sql = sql + f' AND county LIKE "{county}"'
		cursor.execute(sql)
		ret = cursor.fetchall()
		tract_ids = {"tracts": [x[0] for x in ret]}
	return tract_ids

@app.route("/<lila>/<distance>/<type>")
def li_distance_type(lila, distance, type):
	if lila not in ["low_income", "low_access"]:
		return {"status": "not found"}
	county = None
	if "county" in request.args:
		county = request.args["county"].lower()
	if distance not in ["half_mile", "one_mile", "ten_miles", "twenty_miles"] or type not in ["urban", "rural"]:
		return {"status": "not found"}
	type_flag = 0
	if type == "urban":
		type_flag = 1
	with cnx.cursor() as cursor:
		sql = f"SELECT tract_id FROM food_desert_data WHERE la_{distance} = 1 AND is_urban = {type_flag}"
		if lila == "low_income":
			sql = sql + " AND low_income = 1"
		if county:
			sql = sql + f' AND county LIKE "{county}"'
		cursor.execute(sql)
		ret = cursor.fetchall()
		tract_ids = {"tracts": [x[0] for x in ret]}
	return tract_ids

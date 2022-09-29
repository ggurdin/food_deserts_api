from api import app
from flask import request, jsonify
import json
from sqlalchemy import create_engine

engine = create_engine(f'postgresql://{app.config["DB_USER"]}:{app.config["DB_PASSWORD"]}@{app.config["DB_HOST"]}')

@app.route("/api/counties")
def counties():
	with engine.connect() as connection:
		result = connection.execute("SELECT DISTINCT county FROM tract_demographics;")
		counties = json.dumps({"counties": [x['county'] for x in result]})
	return counties

@app.route("/api/demographic_info")
def demographics():
	county = request.args['county'].lower()
	with engine.connect() as connection:
		counties = connection.execute("SELECT DISTINCT county FROM tract_demographics;")
		counties = [x['county'].lower() for x in counties]
		if county in counties:
			county_data_sql = f"SELECT tract_id, low_income, proverty_rate, median_family_income, population_2010 FROM tract_demographics WHERE county ILIKE '{county}';"
			result = connection.execute(county_data_sql)
			ret = {"county_data": []}
			for x in result:
				ret["county_data"].append({"census_tract": x[0], "low_income": x[1], "proverty_rate": x[2], "median_family_income": x[3], "population_2010": x[4]})
			return json.dumps(ret)
		else:
			return json.dumps({"status": "not found"})
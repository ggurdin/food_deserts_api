from api import app
from flask import request
import os
import pymysql
from dotenv import load_dotenv
from flask import render_template
import json
from google.cloud import storage
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly


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

def get_geojson():
    client = storage.Client()
    bucket_name = "richmond_geojsonn"
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('new_richmond.json')
    return json.loads(blob.download_as_string(client=None))

def get_tract_df():
	tract_data = requests.get("https://richmondfooddeserts.com/api/tract_demographics/")
	tract_data = tract_data.json()
	df = pd.DataFrame.from_records(tract_data["demographics"])
	df = df[["census_tract", "county", "median_family_income", "population"]]
	df = df.rename({
		"census_tract": "Census Tract",
		"county": "County",
		"median_family_income": "Median Family Income",
		"population": "Population"
	}, axis=1)
	return df

def create_map(geojson, df):
	customdata = np.stack((df['Census Tract'], df['County'], df['Median Family Income'].astype(int)), axis=-1)
	fig = go.Figure(data=go.Choropleth(
		locations=df['Census Tract'],
		geojson=geojson,
		z = df['Population'],
		featureidkey="properties.GEO_ID",
		showscale=False,
		customdata=customdata,
		hovertemplate = (
			'Census Tract: %{customdata[0]}<br>' +
			'County: %{customdata[1]}<br>' + 
			'Population: %{customdata[2]}<br>' + 
			'<extra></extra>'
		)
	))    
	fig.update_geos(fitbounds="locations", showcoastlines=False, showland=False, showframe=False)
	fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
	fig.update_layout(dragmode=False)
	return fig


@app.route("/")
def index():
	geojson = get_geojson()
	df = get_tract_df()
	map = create_map(geojson, df)
	map = json.dumps(map, cls=plotly.utils.PlotlyJSONEncoder)
	return render_template("map.html", map=map)

@app.route("/api/<type>/")
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

@app.route("/api/low_income/")
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

@app.route("/api/<lila>/<distance>/")
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

@app.route("/api/<lila>/vehicle")
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

@app.route("/api/<lila>/<distance>/<type>")
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

@app.route("/api/tract_demographics/")
def tract_info():
	sql = f"""
		SELECT 
			tract_id AS census_tract,
			county,
			is_urban,
			population,
			housing_units,
			living_in_gqtrs AS living_in_group_quarters,
			poverty_rate,
			median_family_income,
			low_income_pop AS low_income_population,
			kids_pop AS child_population, 
			seniors_pop AS senior_population, 
			white_pop AS white_population, 
			black_pop AS black_population, 
			asain_pop AS asian_population, 
			pacific_pop AS native_hawaiian_and_pacific_islander_population, 
			native_pop AS native_american_and_native_alaskan_population, 
			other_pop AS mixed_race_and_other_population, 
			latino_pop AS hispanic_and_latino_population, 
			vehicle_pop AS housing_units_without_vehicle_access, 
			snap_pop AS housing_units_on_snap
		FROM food_desert_data
	"""
	if "tract_id" in request.args:
		tract_id = int(request.args["tract_id"])
		sql = sql + f" WHERE tract_id = {tract_id}"
	with cnx.cursor() as cursor:
		cursor.execute(sql)
		columns = cursor.description 
		resp = list(cursor.fetchall())
		columns = [x[0] for x in columns]
		print(resp)
		print(columns)
		ret = {"demographics": []}
		for tract in resp:
			ret["demographics"].append({key: value for key, value in zip(columns, tract)})
	return ret

@app.route("/api/access/<distance>")
def access(distance):
	if "tract_id" not in request.args:
		return {"status": "not found"}
	tract_id = int(request.args["tract_id"])
	if distance not in ["half_mile", "one_mile", "ten_miles", "twenty_miles"]:
		return {"status": "not found"}
	with cnx.cursor() as cursor:
		sql = f"""
			SELECT
				la_pop_{distance} AS low_access_population,
				lali_pop_{distance} AS low_access_low_income_population,
				la_kids_{distance} AS low_access_child_population,
				la_seniors_{distance} AS low_access_senior_population,
				la_white_{distance} AS low_access_white_population,
				la_black_{distance} AS low_access_black_population,
				la_asian_{distance} AS low_access_asian_population,
				la_pacific_{distance} AS low_access_hawaiian_and_pacific_islander_population,
				la_native_{distance} AS low_access_native_american_and_native_alaskan_population,
				la_other_{distance} AS low_access_mixed_race_and_other_population,
				la_latino_{distance} AS low_access_hispanic_and_latino_population,
				la_vehicle_{distance} AS housing_units_without_vehicle_access,
				la_snap_{distance} AS low_access_housing_units_on_snap
			FROM food_desert_data
			WHERE tract_id = {tract_id}
		"""
		cursor.execute(sql)
		columns = cursor.description 
		resp = list(cursor.fetchone())
		columns = [x[0] for x in columns]
		return {key: value for key, value in zip(columns, resp)}
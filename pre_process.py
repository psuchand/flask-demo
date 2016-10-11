import pandas as pd
import numpy as np
import seaborn as sns

from datetime import timedelta

import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import matplotlib

from helper_functions import *

##############################################
#Constants
DATA_DIR = "./"

trip_data_cols = ['hack_license', 'pickup_datetime','dropoff_datetime','pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude','trip_time_in_secs','trip_distance']
trip_fare_cols = [' hack_license',' pickup_datetime', ' fare_amount', ' tip_amount', 'tolls_amount']


##############################################
#Read Taxi Data

def process_taxi_data(i):
	"""
	Load two dataframes into memory, do basic computations, clean it, 
	and return the rides dataframe.
	"""
	
	print("Starting process", i)

	trip_data_names = ["trip_data_"+str(i)+".csv.zip"]
	trip_fare_names = ["trip_fare_"+str(i)+".csv.zip"]

	trip_data = []
	for name in trip_data_names:
		print("Reading " + name)
		usecols = working_column_names(DATA_DIR + name, trip_data_cols)
		df = pd.read_csv(DATA_DIR + name, usecols = usecols)
		df = cleanup_column_names(df)
		trip_data.append(df)

	# trip_data_1 = pd.read_csv(DATA_DIR + "trip_data_1.csv.zip", usecols = trip_data_cols)#, nrows=10000)
	# trip_data_2 = pd.read_csv(DATA_DIR + "trip_data_2.csv.zip", usecols = trip_data_cols)#, nrows=10000)

	trip_data = pd.concat(trip_data)
	
	trip_fare = []
	for name in trip_fare_names:
		print("Reading " + name)
		usecols = working_column_names(DATA_DIR + name, trip_fare_cols)
		df = pd.read_csv(DATA_DIR + name, usecols = usecols)
		df = cleanup_column_names(df)
		trip_fare.append(df)

	print("Done reading data.")

	# trip_fare_1 = pd.read_csv(DATA_DIR + "trip_fare_1.csv.zip", usecols = trip_fare_cols)#, nrows=100000)
	# trip_fare_2 = pd.read_csv(DATA_DIR + "trip_fare_2.csv.zip", usecols = trip_fare_cols)#, nrows=100000)

	trip_fare = pd.concat(trip_fare)

	#trip_fare.columns = [z.strip() for z in trip_fare.columns]

	#delete old data
	# del trip_data_1
	# del trip_data_2
	# del trip_fare_1
	# del trip_fare_2

	#Parse datetime columns
	datetime_cols = ['pickup_datetime', ' pickup_datetime', 'dropoff_datetime']
	for col in datetime_cols:
	    if col in trip_data.columns.tolist():
	        trip_data[col] = pd.to_datetime(trip_data[col])
	    if col in trip_fare.columns.tolist():
	        trip_fare[col] = pd.to_datetime(trip_fare[col])
	        
	rides = pd.merge(trip_data,trip_fare, on=['hack_license','pickup_datetime'])

	#Reclaim memory
	#del trip_data
	#del trip_fare

	##############################################
	#Add Profit columns
	rides['profit'] = rides['fare_amount'] + rides['tip_amount'] - 3.6*rides.trip_distance/29.0 - rides['tolls_amount']#$3.60/Gallon, 29 MPG
	rides = remove_trips_invalid_profit(rides)

	print("Numer of rows: %d"%len(rides.index))
	return rides

def working_column_names(name,desired_names):
	desired_names_strip = [z.strip() for z in desired_names]
	df = pd.read_csv(name, nrows=1)
	L = [z for z in df.columns if z.strip() in desired_names_strip]

	assert len(L) == len(desired_names), "Error! Desired column names not available: " + str(L)
	return L

def remove_rows_with_bad_gps(rides):
	print "Removing rows with bad gps...",
	rides = rides[(rides.pickup_longitude < -71) & (rides.pickup_longitude > -75) & (rides.pickup_latitude > 38) & (rides.pickup_latitude < 42)]
	rides = rides[(rides.dropoff_longitude < -71) & (rides.dropoff_longitude > -75) & (rides.dropoff_latitude > 38) & (rides.dropoff_latitude < 42)]
	print "done."
	return rides

def remove_trips_invalid_profit(rides):
	"""
	Ignore rides that have profit of more than $150/hr
	"""
	return rides[rides.profit/(rides.trip_time_in_secs/(60.0*60.0)) < 150]

def filter_data_to_region(rides):
	"""
	Filter data to lie within a certain region.
	"""
	print ("Filtering data to region.")

	#New york
	# llcrnrlat=    40.491553
	# llcrnrlon=  -74.278795
	# urcrnrlat = 40.849861
	# urcrnrlon =  -73.718492

	#Manhattan
	# llcrnrlat = 40.685727
	# llcrnrlon= -74.040356 
	# urcrnrlat = 40.920917
	# urcrnrlon=-73.748309

	#Columbia University
	# llcrnrlat =40.794643
	# llcrnrlon=-73.975520
	# urcrnrlat=40.811503
	# urcrnrlon=-73.948259

	#Absolute bagels bounding box
	# llcrnrlat =40.797029
	# llcrnrlon=-73.974294
	# urcrnrlat=40.806626
	# urcrnrlon=-73.959547

	#JFK Bounding box
	#llcrnrlat, llcrnrlon = [40.638357,-73.797522]
	#urcrnrlat, urcrnrlon = [40.653205, -73.770271]

	#Queens
	#llcrnrlat, llcrnrlon = [40.638950, -73.875320]
	#urcrnrlat, urcrnrlon =[40.796641, -73.726318]

	#Washington Heights to Eastchester (Bronx)
	#llcrnrlat, llcrnrlon = [40.836914, -73.942623]
	#urcrnrlat, urcrnrlon =[40.885936, -73.823966]

	#Brooklyn
	#llcrnrlat, llcrnrlon = [40.564613, -74.016310]
	#urcrnrlat, urcrnrlon = [40.707493, -73.917782]

	#Midtown
	#llcrnrlat, llcrnrlon = [40.748528, -74.000847]
	#urcrnrlat, urcrnrlon =[40.760869, -73.957466]

	#Lower Manhattan
	#llcrnrlat, llcrnrlon = [40.706498, -74.016040]
	#urcrnrlat, urcrnrlon = [40.728834, -73.990048]

	#Upper East Side
	#llcrnrlat, llcrnrlon = [40.764751, -73.971011]
	#urcrnrlat, urcrnrlon = [40.783880, -73.944470]

	#Upper West Side
	#llcrnrlat, llcrnrlon = [40.768395, -73.993184]
	#urcrnrlat, urcrnrlon = [40.800890, -73.959538]

	#Staten Island
	llcrnrlat, llcrnrlon = [40.494599, -74.253496]
	urcrnrlat, urcrnrlon = [40.648507, -74.056273]

	#Hell's kitchen:
	#llcrnrlat =40.758774
	#llcrnrlon=-74.003318
	#urcrnrlat=40.775696
	#urcrnrlon= -73.976103

	#Wall Street and Broadway
	#lat_0 = 40.707854
	#lon_0 = -74.011536

	#Brooklyn
	# lat_brooklyn = 40.697933
	# lon_brooklyn = -73.919656

	##############################################
	#Filter Rides to given area
	mask = lambda df: (df.pickup_longitude >= llcrnrlon )  &  (df.pickup_longitude <= urcrnrlon)  & (df.pickup_latitude >= llcrnrlat) & (df.pickup_latitude <= urcrnrlat)
	rides = rides[mask(rides)]
	return rides

def add_pos_column(rides, delete_old_columns = False, num_digits=3, multiplier=1):
	##############################################
	#Round GPS Coordinates

	rides_rounded_coords = round_gps_coordinates(rides, num_digits, multiplier)
	round_string = "%." + str(num_digits) + "f"
	rides['pos'] = [str(z) for z in zip(rides_rounded_coords.pickup_longitude.apply(lambda z: round_string%z), 
						rides_rounded_coords.pickup_latitude.apply(lambda z: round_string%z))]


	rides.loc[:,'pos'] = rides.pos.apply(lambda s: s.replace("\'",""))

	if delete_old_columns:
		del rides['pickup_latitude']
		del rides['pickup_longitude']

	#rides.loc[:,('pos')] = rides.pos.apply(lambda s: s.replace("\'",""))
	rides = rides[rides.pos != "(0.0000, 0.0000)"]
	rides = rides[rides.pos != "(0.000, 0.000)"]
	rides = rides[rides.pos != "(0.00, 0.00)"]
	rides = rides[rides.pos != "(0.0, 0.0)"]

	return rides

def add_dropoff_pos_column(rides, delete_old_columns = False, num_digits=3, multiplier=1):
	##############################################
	#Round GPS Coordinates

	rides_rounded_coords = round_gps_coordinates(rides, num_digits, multiplier, type="dropoff")
	round_string = "%." + str(num_digits) + "f"
	rides['dropoff_pos'] = [str(z) for z in zip(rides_rounded_coords.dropoff_longitude.apply(lambda z: round_string%z), 
						rides_rounded_coords.dropoff_latitude.apply(lambda z: round_string%z))]

	rides.loc[:,'dropoff_pos'] = rides.dropoff_pos.apply(lambda s: s.replace("\'",""))

	if delete_old_columns:
		del rides['dropoff_latitude']
		del rides['dropoff_longitude']

	#rides.loc[:,('pos')] = rides.pos.apply(lambda s: s.replace("\'",""))
	rides = rides[rides.dropoff_pos != "(0.0000, 0.0000)"]
	rides = rides[rides.dropoff_pos != "(0.000, 0.000)"]
	rides = rides[rides.dropoff_pos != "(0.00, 0.00)"]
	rides = rides[rides.dropoff_pos != "(0.0, 0.0)"]


	return rides

def filter_weekday_mornings(X):
	"""
	Select rides that occur on weekday mornings only.
	"""
	morning_hours = [7,8,9] #7am-10am according to trip advisor.

	X['day_of_week'] = X.pickup_datetime.apply(lambda z: z.dayofweek)
	X['hour'] = X.pickup_datetime.apply(lambda z: z.hour)

	X = X[X.hour.isin(morning_hours)]
	X = X[X.day_of_week.isin(range(0,5))]

	del X['day_of_week']
	del X['hour']

	return X

def cleanup_column_names(df):
	df.columns = [z.strip() for z in df.columns]
	return df

def round_gps_coordinates(rides, num_digits, multiplier, type="pickup"):
	"""
	Round GPS coordinates.
	"""
	names = ["_longitude", "_latitude"]
	for c in names:
		name = type + c
		rides.loc[:, name] = multiplier*rides.loc[:, name]
		rides.loc[:, name] = rides[name].apply(lambda z: round(z, num_digits))
		rides.loc[:, name] = 1.0/float(multiplier)*rides.loc[:, name]

	return rides

def calculate_trip_distances(rides):
	"""
	Determine the distance between two points, according to taxi-drivers.

	To determine the distance between two points, use this
	taxi_distance.loc[["(-71.31, 41.50)","(-71.30, 41.50)"]]['trip_distance'].values[0]

	or to determine time use this

	taxi_distance.loc[["(-71.31, 41.50)","(-71.30, 41.50)"]]['trip_time_in_secs'].values[0]	"""

	print "Calculating taxi distance...",
	taxi_distance = rides[['pos','dropoff_pos', 'profit','trip_distance','trip_time_in_secs','tolls_amount']].groupby(['pos','dropoff_pos']).mean()
	taxi_distance.dropna(inplace=True)
	print "done."
	return taxi_distance

if __name__ == "__main__":

	rides_list = []
	wages_list = []

	for i in [2]:
		rides = process_taxi_data(i)
		rides = remove_rows_with_bad_gps(rides)
		rides = filter_weekday_mornings(rides)
		rides = add_pos_column(rides, num_digits=2)
		rides = add_dropoff_pos_column(rides, num_digits=2)

		wages = hourly_wage_df(rides)
		wages = cleanup_column_names(wages)

		rides_list.append(rides)
		wages_list.append(wages)

		#rides.to_csv("rides"+str(i) + ".csv")
		#wages.to_csv("wages"+str(i) + ".csv")

	rides = pd.concat(rides_list)
	rides.to_csv("rides.csv")

	taxi_distance = calculate_trip_distances(rides)
	taxi_distance.to_csv("taxi_distance.csv")

	wages = pd.concat(wages_list)
	wages.to_csv("wages.csv")
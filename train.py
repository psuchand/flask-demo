from ml_helper_functions import *
from helper_functions import *
from pre_process import *

import pandas as pd

DATA_DIR = "./"
TRAINING_DIR = DATA_DIR + "training/"

def train(rides, output_dir):
    """Train the ML algorithm on the given dataset. 

	Naively train based on profit of locations. This strategy does quite well.

	With parameters
	starting_pos = "(-73.88, 40.75)" #Jackson Heights
	starting_hour = 9
	max_trip_length_seconds = 60*60

	The naive algorithm gives drivers an average salary of $38.148/hr, which is
	about average. After training, the algorithm gives drivers an average salary of
	$42.670/hr. This is about a 12% increase in hourly salary.

    Training data is saved in TRAINING_DIR, and loaded in the ML algorithm.
    """

    X = rides.groupby('pos').size()
    good_positions = X[ X > X.quantile(.8)]

    good_positions.to_csv(output_dir + "good_positions.csv")
    #Determine Expected Profit
    expected_profit = rides[['pos','profit']]
    expected_profit = expected_profit[(expected_profit.profit < 200) & (expected_profit.profit > -5)]
    expected_profit = expected_profit.groupby('pos').mean()
    expected_profit.to_csv(output_dir + "expected_profit.csv")

def train_from_good_riders(rides, wages, output_dir):
    """
    Train the ML algorithm on the given dataset.
		
	Train based on locations frequented by good drivers.

	With parameters
	starting_pos = "(-73.88, 40.75)" #Jackson Heights
	starting_hour = 9
	max_trip_length_seconds = 60*60
	
	This naive random algorithm gives drivers an average salary of $38.254/hr, which is
	about average. After training, the algorithm gives drivers an average salary of
	$43.270/hr. This is about a 13% increase in hourly salary.

    Training data is saved in TRAINING_DIR, and loaded in the ML algorithm.
    """


    #Identify good drivers
    wages = wages[wages.hourly_wage<100]
    wages = wages[(wages.percent_time_idle>5) & (wages.percent_time_idle<100)]

    #Rate drivers as TOP and BOTTOM by percent idle time
    top = wages[(wages.percent_time_idle > 3) & (wages.percent_time_idle < 10)]
    bottom = wages[wages.percent_time_idle > 19]

    #Clean data
    bottom = bottom[(bottom.hourly_wage<150) & (bottom.hourly_wage>5)]
    top = top[(top.hourly_wage<150) & (top.hourly_wage>5)]

    top_drivers = top.hack_license.values
    good_positions = locations_frequented_by_drivers(rides, top_drivers, top_percent =.3)

    #X = rides.groupby('pos').size()
    #good_positions = X[ X > X.quantile(.8)]

    good_positions.to_csv(TRAINING_DIR + "good_positions.csv")
    #Determine Expected Profit
    expected_profit = rides[['pos','profit']]
    expected_profit = expected_profit[(expected_profit.profit < 200) & (expected_profit.profit > -5)]
    expected_profit = expected_profit.groupby('pos').median()
    expected_profit.to_csv(TRAINING_DIR + "expected_profit.csv")


if __name__ == "__main__":
	print "This function trains the ML model based on rides.csv. Output is in " + TRAINING_DIR + "\n"
	print "Reading data...",
	rides = pd.read_csv(TRAINING_DIR + "rides.csv")
	wages = pd.read_csv(TRAINING_DIR + "wages.csv")
	print "done."
	print "Training...",

	#Pick one of the training methods below.
	
	#1.) Naive training via profit of location.
	#train(rides, TRAINING_DIR)
	
	#2.) Training from habits of good drivers 
	train_from_good_riders(rides, wages, TRAINING_DIR)
	print "done."
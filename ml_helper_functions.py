from random import random
from math import floor
from vincenty import vincenty
import pandas as pd

PENALTY_PROFIT_BAD_POS = -8
PENALTY_TIME_BAD_POS = 60*10
DRIVING_SPEED_IN_MPH = 12.5

COST_OF_TRAVEL_TIME_DOLLARS_HR = 42
OVERALL_AVG_WAIT_TIME = 11.4*60 #In Seconds
GOOD_POSITION_WAIT_TIME = 3*60 #In seconds

#DATA_DIR = "../../taxi-data/"
DATA_DIR = "./"
TRAINING_DIR = DATA_DIR + "training/"


def random_ride(rides, from_position, starting_hour):
    """
    Randomly choose a ride from the given dataframe, at the specified position.    
    Sampling is done assuming the distribution of rides does not vary within the hour.
    """

    #Restrict to rides for the given hour and position
    rides = rides[(rides.hour == starting_hour) & (rides.pos == from_position)]

    try:
        choice = rides.sample(1)

        ending_pos = choice['dropoff_pos'].values[0]
        time_of_ride = choice['trip_time_in_secs'].values[0]
        distance_of_ride = choice['trip_distance'].values[0]
        
        profit = choice['profit'].values[0]
        profit -= gas_price_for_distance(distance_of_ride)
        
#         print "ending_pos",ending_pos
#         print "time_of_ride",time_of_ride
#         print "distance_of_ride",distance_of_ride
#         print "profit",profit


        return ending_pos, profit, time_of_ride, distance_of_ride
    except Exception:
        print "Penalty!"
        return None, PENALTY_PROFIT_BAD_POS, PENALTY_TIME_BAD_POS, None

def better_position(starting_pos):
    """
    Determine a list of positions that good drivers frequent.

    Return the a list of positions that we think it would be worth to go to.
    """
    if starting_pos not in expected_profit.index:
        return None
    
    expected_profit_incl_travel = expected_profit_for_good_locations.apply( 
                            lambda z: z + time_and_gas_estimated_cost_function(starting_pos,z.name) , axis = 1)
            
    expected_profit_do_nothing = expected_profit.loc[starting_pos].values[0]
    
    good_choices = expected_profit_incl_travel
    good_choices = good_choices[good_choices.profit > expected_profit_do_nothing ]
    if len(good_choices.index) > 0:
        print "\texpected_profit do_nothing=%.2f, move=%.2f"%(expected_profit_do_nothing,expected_profit.loc[good_choices.profit.argmax()].values[0])
        return good_choices.profit.argmax()
        
        #Another option is to sample randomly
        #return good_choices.sample(1).index.values[0]
    else:
        return None

def trip_time_and_distance(starting_pos, to_position):
    """
    Determine the average time of travel and trip distance according to
    NYC taxi rides.
    """
    dist = None
    drive_time_in_sec = None
    try:
        dist = taxi_distance.loc[[starting_pos,to_position]]['trip_distance'].values[0]
        drive_time_in_sec = taxi_distance.loc[[starting_pos,to_position]]['trip_time_in_secs'].values[0]
    except Exception as e:
        pass

    return dist, drive_time_in_sec
    
def time_and_gas_estimated_cost_function(starting_pos, to_position):
    
    dist, drive_time_in_sec = trip_time_and_distance(starting_pos, to_position)
        
    if dist == None or drive_time_in_sec == None:
        return -1000000
    
    if dist > 4:
        return -1000000
    
    if drive_time_in_sec > 20*60:
        return -1000000
    
    #This is gas price + travel time.
    return -1*(3.6*dist/29.0 + ((drive_time_in_sec/float(60*60))*COST_OF_TRAVEL_TIME_DOLLARS_HR))
    
def gas_price_for_distance(dist):
    return 3.6*dist/29.0

# def gas_price(start_pos, to_position):
#     s_long, s_lat = [float(z) for z in starting_pos[1:-1].split(",")]
#     d_long,d_lat = [float(z) for z in to_position[1:-1].split(",")]
#     dist = vincenty((d_lat, d_long), (s_lat, s_long), miles=True)

#     return 3.6*dist/29.0

# def travel_time_in_seconds(starting_pos, to_position):
    
#     s_long, s_lat = [float(z) for z in starting_pos[1:-1].split(",")]
#     d_long,d_lat = [float(z) for z in to_position[1:-1].split(",")]
#     dist = vincenty((d_lat, d_long), (s_lat, s_long), miles=True)
    
#     return dist/float(DRIVING_SPEED_IN_MPH)

def simulate_naive_trajectory(rides, starting_position, starting_hour, max_trip_length_seconds):
    """
    Simulate the naive strategy of just doing a pickup wherever you are. 
    """
    current_pos = starting_position
    profit = 0
    trip_length_in_seconds = 0
    while trip_length_in_seconds < max_trip_length_seconds:

        #Pick a random ride.
        ending_pos, added_profit, time_of_ride, distance_of_ride = random_ride(rides, current_pos, starting_hour)
        #ending_pos, added_profit, length_of_ride = 
        profit += added_profit
        print "-",
        trip_length_in_seconds += time_of_ride + floor(random()*OVERALL_AVG_WAIT_TIME)
        if ending_pos != None:
            current_pos = ending_pos
           
    hourly_salary = float(profit)/float(trip_length_in_seconds/(60.0*60.0))
    print "Hourly salary: %.2f"%hourly_salary
    return hourly_salary

def simulate_informed_trajectory(rides, starting_position, starting_hour, max_trip_length_seconds):
    """
    Simulate the naive strategy of just doing a pickup wherever you are. 
    """
    current_pos = starting_position
    profit = 0
    trip_length_in_seconds = 0
    while trip_length_in_seconds < max_trip_length_seconds:

        #Pick a random ride.
        #print "Picking new random ride. Current profit = ", profit
        ending_pos, added_profit, time_of_ride, distance_of_ride = random_ride(rides, current_pos, starting_hour)
        #ending_pos, added_profit, length_of_ride = random_ride(rides, current_pos, starting_hour)
        #print "Got added profit = ", added_profit
        profit += added_profit
        trip_length_in_seconds += time_of_ride
        
        print "-",
        
        if ending_pos != None:
            #Would informed drivers make a different choice?
            p =  better_position(ending_pos)
            if p != None:
                print "\tBetter Position \n\t" + "Swapping: " + reverse_geocode(ending_pos) + "\n\tWith: " + reverse_geocode(p)
                current_pos = p
                drive_dist, drive_time_in_sec = trip_time_and_distance(ending_pos, p)                
                #Update time remaining, and profit based on gas cost
                trip_length_in_seconds += drive_time_in_sec
                #print "\tPrice of gas : ", gas_price_for_distance(drive_dist)
                profit -= gas_price_for_distance(drive_dist)
                
                #print "\tProfit = ", profit
                #Model wait time at new position.
                trip_length_in_seconds += floor(random()*GOOD_POSITION_WAIT_TIME)

                #print "*",
                print "\tTrying better position: %.2f minutes lost."%(float(drive_time_in_sec)/(60.0))
                continue
            
            current_pos = ending_pos
            
        trip_length_in_seconds += floor(random()*OVERALL_AVG_WAIT_TIME)
        #print "Profit = ", profit

    hourly_salary = float(profit)/float(trip_length_in_seconds/(60.0*60.0))
    print "Hourly salary: %.2f"%hourly_salary
    return hourly_salary

def reverse_geocode(pos):
    """
    Given a longitude, latitude pair, reverse geocode and print it.
    """
    lon, lat = [float(z) for z in pos.strip().replace("(", "").replace(")","").split(",")]
    address = geocoder.google([lat, lon], method='reverse').address
    
    if address == None:
        return ""
    else:
        return address
    
def random_nearby_position(pos):
    """
    Return a random nearby position
    """
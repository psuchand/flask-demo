##############################################
#Helper functions

#Plot profit for given cabbies
##############################################
import pandas as pd
import numpy as np

def plot_profit_for_drivers(drivers):
    """
    If cabbies is a list, we plot the profit 
    (calculated via the rides dataframe) 
    for drivers in that list.
    
    If drivers is not a list, it is a dataframe,
    and its index is the required list.
    """
    import numpy as np

    drivers_list = []
    if type(drivers) in [list,np.ndarray] :
        drivers_list = drivers
    else:
        drivers_list = drivers.index

    #Calculate profit per hack_license
    df = rides[rides.hack_license.isin(drivers_list)]
    df = df.groupby('hack_license')['profit'].sum()
    
    print("Mean profit = %.2f"%df.mean())
    print("Median profit = %.2f"%df.median())
    print("Profit 10 percent quantile = %.2f\nProfit 90 percent quantile = %.2f\n"%(df.quantile(.1), df.quantile(.9)))

    #Histogram. X-axis is profit, Y is number of cabbies
    df.hist(bins=40, normed = True)
    
def plot_wage_for_drivers(drivers):
    """
    If cabbies is a list, we plot their hourly wage 
    (calculated via the rides and wage dataframe) 
    for drivers in that list.
    
    If drivers is not a list, it is a dataframe,
    and its index is the required list.
    """
    drivers_list = []
    if type(drivers) in [list,np.ndarray] :
        drivers_list = drivers
    else:
        drivers_list = drivers.index

    #Calculate profit per hack_license
    df = rides[rides.hack_license.isin(drivers_list)]
    df = df.groupby('hack_license')['profit'].sum()
    
    print("Mean profit = %.2f"%df.mean())
    print("Median profit = %.2f"%df.median())
    print("Profit 10 percent quantile = %.2f\nProfit 90 percent quantile = %.2f\n"%(df.quantile(.1), df.quantile(.9)))

    #Histogram. X-axis is profit, Y is number of cabbies
    df.hist(bins=40, normed = True)

#Minimum number of rides in a location, before it can be considered frequented
MIN_CLUSTER = 5

def frequented_pickup_locations(df, top_percent = .9):
    """
    Given a dataframe, return ordered pairs of
    the locations the most frequently occuring locations, as 
    determined by the given quantile.
    """
    
    print("frequented_pickup_locations")
    X = df[['pos']].groupby('pos').size()
    X = X[X > MIN_CLUSTER]

    #top_percent = .9
    upper_quantile = X.quantile(top_percent)
    X = X[X >= upper_quantile]

    # X = pd.DataFrame()
    # X['pos'] = df['pos']
    
    # X = X[X.groupby('pos').pos.transform(len) > MIN_CLUSTER]
    
    # gb = X.groupby('pos').size()
    
    # quantile = .9
    # upper_quantile = gb.quantile(quantile)
    # gb = gb[gb >= upper_quantile]

    #Print statistics
    print("Statistics for table. X = position frequented by driver, Y = #pickups.")
    print X.describe()
    print("\n")
    
    return X

def locations_frequented_by_drivers(df, drivers, top_percent = .9):
    """
    rides is the main dataset of all drivers.
    """
    import numpy as np

    drivers_list = []
    if type(drivers) in [list,np.ndarray] :
        drivers_list = drivers
    else:
        drivers_list = drivers.index

    return frequented_pickup_locations(df[df.hack_license.isin(drivers_list)], top_percent=top_percent)

#Locations frequented by most profitable cabbies

def locations_frequented_by_most_profitable_cabbies(df):
    """
    Return locations frequented by the most profitable cabbies.
    """
    
    profit_by_rider = rides[['hack_license', 'profit']].groupby('hack_license').sum()
    upper_quantile = profit_by_rider.quantile(.9)
    most_profitable_riders = profit_by_rider[profit_by_rider >= upper_quantile]
    return frequented_pickup_locations(df[df.hack_license.isin(most_profitable_riders.index)])

def locations_frequented_by_least_profitable_cabbies(df):
    """
    Return locations frequented by the least profitable cabbies.
    """
    
    profit_by_rider = rides[['hack_license', 'profit']].groupby('hack_license').sum()
    upper_quantile = profit_by_rider.quantile(.1)
    least_profitable_riders = profit_by_rider[profit_by_rider <= upper_quantile]
    return frequented_pickup_locations(df[df.hack_license.isin(least_profitable_riders.index)])

#Determine the fraction of a driver's fares that come from a given set of locations

def percent_fares_from_given_positions(X, good_positions):
    """
    df is a dataframe with keys
    hack_license, pickup_longitude, pickup_latitude
    
    This function does NOT round gps coordinates.
    """
    
    df = X[['hack_license', 'pos']]
    gb = df.groupby('hack_license')
    df = gb.apply(lambda z: z['pos'].isin(good_positions.index))
    df = df.reset_index()
    del df['level_1']
    return df.groupby('hack_license').apply(lambda z: z.mean())

#Data cleanup
MIN_PICKUPS = 1

def cleanup(df):
    """
    1) Remove all cabbies that haven't made more than MIN_PICKUPS pickups
    
    2.) Only keep drivers whose #pickups made is within 2 standard deviations 
    of the median.

    """
    
    riders = df['hack_license'].value_counts()
    mean = riders.mean()
    std = riders.std()
    
    riders = riders[riders <= (mean + 2*std)]
    riders = riders[riders >= (mean - 2*std)]

    riders = riders[riders >= MIN_PICKUPS]
    riders = riders.index
        
    rides = df[df.hack_license.isin(riders)]    
    
    #Clean up by fare amount and tip amount.
    MAX_RIDE_TIME = rides.trip_time_in_secs.quantile(.99)
    rides = rides[(rides.trip_time_in_secs < MAX_RIDE_TIME) & (rides.trip_time_in_secs > 0)]

    MAX_TIP = rides.tip_amount.quantile(.99)
    rides = rides[(rides.tip_amount < MAX_RIDE_TIME) & (rides.tip_amount > 0)]

    MAX_FARE = rides.fare_amount.quantile(.99)
    rides = rides[(rides.fare_amount < MAX_RIDE_TIME) & (rides.fare_amount > 0)]

    print "Returned %d rows"%len(rides.index)
    return rides


#Plot profit for drivers that frequent good positions
FREQUENTING_THRESHOLD = .5
NOT_FREQUENTING_THRESHOLD = .2

def plot_profit_for_riders_frequenting_and_not_frequenting_good_positions(rides, good_positions):
    """
    Plot profit for riders frequenting, and not frequenting good positions
    """

    df = percent_fares_from_given_positions(rides, good_positions)
    
    #Plot profit for drivers that frequent good positions
    print df.head()
    drivers_frequenting = df[df.pos >= FREQUENTING_THRESHOLD]
    drivers_not_frequenting = df[df.pos <= NOT_FREQUENTING_THRESHOLD]

    print("drivers_frequenting")
    print drivers_frequenting.describe()
    plot_profit_for_drivers(drivers_frequenting)
    print("drivers_not_frequenting")
    print drivers_not_frequenting.describe()
    plot_profit_for_drivers(drivers_not_frequenting)
    
##############################################
#Initialization

def plot_points(coords):
    """
    Given a collection of points, plot them.
    """
    
    #Plot a given set of gps coordinates on the map
    import matplotlib
    matplotlib.rcParams['figure.figsize'] = (40,30)
    
    #Wall Street and Broadway
    lat_0 = 40.707854
    lon_0 = -74.011536
    
    GPS_COORDS_LONGS, GPS_COORDS_LATS = zip(*coords.tolist())
    
    GPS_COORDS_LONGS = [float(z) for z in GPS_COORDS_LONGS]
    GPS_COORDS_LATS = [float(z) for z in GPS_COORDS_LATS]
    
    my_map = Basemap(projection='merc', lat_0=lat_0, lon_0=lon_0,
        resolution = 'h', area_thresh = .1,
        llcrnrlon = llcrnrlon, llcrnrlat = llcrnrlat,
        urcrnrlon = urcrnrlon, urcrnrlat = urcrnrlat)
    
    longs, lats = my_map(GPS_COORDS_LONGS, GPS_COORDS_LATS)
    print "Number of points: ", len(longs)
    
    my_map.drawmapboundary()
    my_map.readshapefile(DATA_DIR + r"gadm-us/NewYork-shp/shape/roads", "osm-nyc")
    my_map.plot(longs, lats, 'ro', markersize = 10, alpha = 1, label = "Positions with least waiting time (<= 1 min)")
    
    # for i in xrange(len(longs)):
    #     if (not all 
    #         ([
    #                 top_positions.iloc[i].pos[0] >= llcrnrlon,
    #                 top_positions.iloc[i].pos[1] >= llcrnrlat,
    #                 top_positions.iloc[i].pos[0] <= urcrnrlon,
    #                 top_positions.iloc[i].pos[1] <= urcrnrlat
    #         ])):
    #         continue
    #     plt.text(longs[i], lats[i], str(top_positions.iloc[i].wait_time))
    
    plt.legend(fontsize = 'xx-large')
    plt.title("Locations for Taxi drivers to pick up customers with least waiting time (near 106th and Broadway)")
    #plt.figure(figsize=(40,30))
    plt.show

from bokeh.io import output_file, show
from bokeh.models import (GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool
)

def coord_from_string(coord_string):
            """
            Coordinates are encoded as strings, convert 
            back to coordinates.
            """
            s = coord_string

            try:
                return [float(z) for z in s]
            except Exception, e:
                replace = list("(,)\'\"")
                for t in replace:
                    s = s.replace(t, " ")

                return [float(z) for z in s.strip().split()]

def extract_longs_lats(coords):
    """
    Convert coordinates as above to a list of 
    longitude, latitude pairs.
    """


    a = np.array([coord_from_string(z) for z in coords])
    a = a.transpose()
    
    longs = a[0]
    lats = a[1]

    return longs, lats


def plot_points_gmaps(coords_blue, coords_red, filename = "gmap_plot.html"):
    """
    Plot a collection of points via google maps
    """    

    def coords_to_ColumnDataSource(coords):
        """
        Convert coordinates as above to a column data source as required by Google's API
        """

        longs, lats = extract_longs_lats(coords)

        #Old code
        # a = np.array([coord_from_string(z) for z in coords])
        # a = a.transpose()
        
        # longs = a[0]
        # lats = a[1]
        
        return ColumnDataSource(
            data= dict(        
                lon=longs,
                lat=lats
            )
        )

    center = coord_from_string(coords_blue[0])
    map_options = GMapOptions(lng=center[0], lat=center[1], map_type="roadmap", zoom=11)
    
    plot = GMapPlot(
        x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options,
        api_key = "AIzaSyB3_kW006gZmQJA929W7794Q4GbIn2fLnU"    
    )

    source_blue = coords_to_ColumnDataSource(coords_blue)
    source_red  = coords_to_ColumnDataSource(coords_red)

    circle_blue = Circle(x="lon", y="lat", size=5, fill_color="blue", fill_alpha=0.8, line_color=None)
    circle_red = Circle(x="lon", y="lat", size=5, fill_color="red", fill_alpha=0.8, line_color=None)

    plot.add_glyph(source_blue, circle_blue)    
    plot.add_glyph(source_red, circle_red)

    plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool())
    output_file(filename)
    show(plot)

#Maximum number of hours between taxi rides within one shift.
MAX_BREAK = 3

def hourly_wage_df(rides):
    """Calculate an hourly wage for each driver
    """
    #Load data, make sure it is in chronological order
    #Load data, make sure it is in chronological order
    wage = rides.loc[:,('hack_license','pickup_datetime')]

    print("Starting with num rows = ", len(wage.index))

    grouped = wage.groupby('hack_license')

    #Put elements of group in chronological order, then shift
    f = lambda z: z.sort_values().shift(-1)
    print("Calculating idle time ...")
    shifted_pickup = grouped.transform(f)

    #Load data, make sure it is in chronological order
    wage = rides.loc[:,('hack_license','dropoff_datetime','trip_time_in_secs')]

    wage['shifted_pickup'] = shifted_pickup
    wage['idle_time'] = wage.shifted_pickup - wage.dropoff_datetime

    #Convert idle time to seconds
    print("Converting times to seconds...")
    wage.loc[:,"idle_time"] = wage.loc[:,"idle_time"].apply(lambda z: float(z.total_seconds()))

    #If the next trip that this driver took is before the previous dropoff, there is an error. Replace these values with 0.
    wage.loc[ wage.idle_time < 0,("idle_time")] = 0

    #These trips correspond to the last trip of the driver 
    wage.loc[wage.idle_time.isnull(), "idle_time"] = 0

    #If the next trip is more than 3 hours before the previous one, assume that the driver went off shift
    print("Determining when drivers went on break...")
    wage.loc[wage.idle_time > MAX_BREAK*60*60, "idle_time"] = 0

    #Return the wage dataset
    wage = wage[['hack_license','idle_time','trip_time_in_secs']]

    print("Calculating percent idle time, profit, hourly wage, ...")
    wage = wage.groupby('hack_license').sum()
    wage['percent_time_idle'] = 100*wage.idle_time/(wage.trip_time_in_secs + wage.idle_time)
    wage['hours_worked'] =  (wage['idle_time'] + wage['trip_time_in_secs'])/float(60*60)

    print("Adding profit column")
    df = rides[['hack_license', 'profit']].groupby('hack_license')['profit'].sum()

    wage = pd.concat([df,wage], axis =1)
    wage['hourly_wage'] = wage.profit/wage.hours_worked

    print("Ending with num rows = ", len(wage.index))
    return wage

def distance_to_dollars(x):
    """
    Given a distance in miles, return the cost of getting there
    """
    return 3.6*rides.trip_distance/29.0


def set_difference(A,B):
    """
    Return elements of A not in B and elements of B not in A
    """

    try:
        return list(set(A) - set(B)), list(set(B) - set(A))
    except Exception:
        print ("Not hashable, trying again ... ")
        Ahashable = [tuple(z) for z in A]
        Bhashable = [tuple(z) for z in B]
        return set_difference(Ahashable, Bhashable)
